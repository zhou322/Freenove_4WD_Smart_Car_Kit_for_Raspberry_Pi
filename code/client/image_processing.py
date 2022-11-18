import cv2
import numpy as np
import math


def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    channel_count = img.shape[2]
    match_mask_color = (255,) * channel_count
    cv2.fillPoly(mask, vertices, match_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def draw_lines(img, lines, color=[0, 255, 0], thickness=3):
    # If there are no lines to draw, exit.
    if lines is None:
        return
    # Make a copy of the original image.
    img = np.copy(img)
    # Create a blank image that matches the original in size.
    line_img = np.zeros(
        (
            img.shape[0],
            img.shape[1],
            3
        ),
        dtype=np.uint8,
    )
    # Loop over all lines and draw them on the blank image.
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(line_img, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
    # Merge the image with the lines onto the original.
    img = cv2.addWeighted(img, 0.8, line_img, 1.0, 0.0)
    # Return the modified image.
    return img

def HSL_color_selection(image):
    """
    Apply color selection to the HSL images to blackout everything except for white and yellow lane lines.
        Parameters:
            image: An np.array compatible with plt.imshow.
    """
    #Convert the input image to HSL
    # converted_image = convert_hsl(image)

    converted_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #White color mask
    sensitivity = 150
    lower_threshold = np.uint8([0, 0, 255 - sensitivity])
    upper_threshold = np.uint8([255, sensitivity, 255])
    white_mask = cv2.inRange(converted_image, lower_threshold, upper_threshold)

    #Yellow color mask
    # lower_threshold = np.uint8([10, 0, 100])
    # upper_threshold = np.uint8([40, 255, 255])
    # yellow_mask = cv2.inRange(converted_image, lower_threshold, upper_threshold)

    return white_mask

def get_intersect(a1, a2, b1, b2):
    """
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """
    s = np.vstack([a1,a2,b1,b2])        # s for stacked
    h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
    l1 = np.cross(h[0], h[1])           # get first line
    l2 = np.cross(h[2], h[3])           # get second line
    x, y, z = np.cross(l1, l2)          # point of intersection
    if z == 0:                          # lines are parallel
        return (float('inf'), float('inf'))
    return (x/z, y/z)

def get_driection(image, intersection):
    # (height, width)
    shape = image.shape
    width = shape[1]
    width_area = width / 3

    intersection_x = intersection[0]

    if intersection_x <= width_area:
        return 'left'
    elif width_area < intersection_x <= width_area * 2:
        return 'middle'
    elif width_area * 2 < intersection_x <= width:
        return 'right'
    else:
        return 'unknown'

def process_image(image):
    # Read image
    # image = cv2.imread('001.jpg')


    # Convert image to grayscale
    # converted_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    shape = image.shape
    region_of_interest_vertices = [
        (0, shape[0]),
        (0, shape[0] / 2),
        (shape[1], shape[0] / 2),
        (shape[1], shape[0]),
    ]

    cropped_image = region_of_interest(
        image,
        np.array([region_of_interest_vertices], np.int32),
    )
    # cv2.imwrite('tmp.jpg',cropped_image)
    converted_image = HSL_color_selection(cropped_image)

    # Use canny edge detection
    edges = cv2.Canny(converted_image, 50, 200)
    # cv2.imwrite('tmp.jpg',edges)

    # Apply HoughLinesP method to
    # to directly obtain line end points
    lines_list =[]
    lines = cv2.HoughLinesP(
        edges, # Input edge image
        1, # Distance resolution in pixels
        np.pi/180, # Angle resolution in radians
        threshold=60, # Min number of votes for valid line
        minLineLength=10, # Min allowed length of line
        maxLineGap=10 # Max allowed gap between line for joining them
    )

    tmp_image = draw_lines(
        image,
        lines,
        thickness=5,
    )

    # cv2.imwrite('tmp.jpg',tmp_image)

    left_line_x = []
    left_line_y = []
    right_line_x = []
    right_line_y = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            # print((x1, y1), (x2, y2))
            slope = (y2 - y1) / (x2 - x1) # <-- Calculating the slope.
            # print(slope)
            if math.fabs(slope) < 0.5: # <-- Only consider extreme slope
                continue
            if slope <= 0: # <-- If the slope is negative, left group.
                left_line_x.extend([x1, x2])
                left_line_y.extend([y1, y2])
            else: # <-- Otherwise, right group.
                right_line_x.extend([x1, x2])
                right_line_y.extend([y1, y2])
    # min_y = image.shape[0] * (3 / 5) # <-- Just below the horizon

    intersection = get_intersect((left_line_x[0], left_line_y[0]),
                                 (left_line_x[1], left_line_y[1]),
                                 (right_line_x[0], right_line_y[0]),
                                 (right_line_x[1], right_line_y[1]))
    # print("intersection", intersection)
    # min_y = intersection[1]
    min_y = 0
    max_y = image.shape[0] # <-- The bottom of the image
    # print(min_y, max_y)
    poly_left = np.poly1d(np.polyfit(
        left_line_y,
        left_line_x,
        deg=1
    ))
    left_x_start = int(poly_left(max_y))
    left_x_end = int(poly_left(min_y))
    poly_right = np.poly1d(np.polyfit(
        right_line_y,
        right_line_x,
        deg=1
    ))
    right_x_start = int(poly_right(max_y))
    right_x_end = int(poly_right(min_y))
    line_image = draw_lines(
        image,
        [[
            [left_x_start, max_y, left_x_end, min_y],
            [right_x_start, max_y, right_x_end, min_y],
        ]],
        thickness=5,
    )
    # cv2.imwrite('detectedLines.jpg',line_image)
    cv2.imwrite('video.jpg', line_image)
    return get_driection(line_image, intersection)

    # Save the result image

if __name__ == '__main__':
    image = cv2.imread('raw_image.jpg')
    asdf = process_image(image)
