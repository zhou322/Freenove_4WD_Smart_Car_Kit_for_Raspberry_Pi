from picamera import PiCamera


def main():
    camera = PiCamera()
    camera.capture('image.jpg')


if __name__ == '__main__':
    main()
