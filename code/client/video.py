import io
import socket
import struct
import sys

import cv2
import numpy as np
from PIL import Image
from image_processing import *


class VideoStreaming:
    def __init__(self, ip):
        self.video_connection = None
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.face_cascade = cv2.CascadeClassifier(r'haarcascade_frontalface_default.xml')
        self.connected = True
        self.face_x = 0
        self.face_y = 0
        try:
            self.video_socket.connect((ip, 8000))
            self.video_connection = self.video_socket.makefile('rb')
        except:
            # print "command port connect failed"
            return

    def stop_tcp_client(self):
        try:
            self.video_socket.shutdown(2)
            self.video_socket.close()
        except:
            pass

    def is_valid_image4_bytes(self, buf):
        b_valid = True
        if buf[6:10] in (b'JFIF', b'Exif'):
            if not buf.rstrip(b'\0\r\n').endswith(b'\xff\xd9'):
                b_valid = False
        else:
            try:
                Image.open(io.BytesIO(buf)).verify()
            except:
                b_valid = False
        return b_valid

    def face_detect(self, img):
        if sys.platform.startswith('win') or sys.platform.startswith('darwin'):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    self.face_x = float(x + w / 2.0)
                    self.face_y = float(y + h / 2.0)
                    img = cv2.circle(img, (int(self.face_x), int(self.face_y)), int((w + h) / 4), (0, 255, 0), 2)
            else:
                self.face_x = 0
                self.face_y = 0
        cv2.imwrite('video.jpg', img)

    def line_detect(self, img):
        try:
            direction = process_image(img)
            print('direction', direction)
        except Exception:
            print("exception")

    def start_streaming(self):
        while True:
            try:
                stream_bytes = self.video_connection.read(4)
                leng = struct.unpack('<L', stream_bytes[:4])
                jpg = self.video_connection.read(leng[0])
                if self.is_valid_image4_bytes(jpg):
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if self.connected:
                        self.face_detect(image)
                        self.line_detect(image)
                        self.connected = False
            except Exception as e:
                print(e)
                break


if __name__ == '__main__':
    pass
