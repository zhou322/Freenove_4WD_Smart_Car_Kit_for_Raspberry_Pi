from picamera2 import Picamera2


def main():
    camera = Picamera2()
    config = camera.create_still_configuration(main={'size': (400, 300)})
    camera.configure(config)

    camera.start()
    camera.capture_file('image.jpg', 'main')
    camera.stop()


if __name__ == '__main__':
    main()
