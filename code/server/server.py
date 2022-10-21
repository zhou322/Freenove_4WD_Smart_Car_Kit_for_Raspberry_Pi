import fcntl
import io
import socket
import struct
from threading import Thread

# noinspection PyUnresolvedReferences
from picamera2 import Picamera2

from buzzer import *
from command import COMMAND, COMMAND_SEPARATOR, COMMAND_TERMINATOR
from led import *
from light_tracking import *
from line_tracking import *
from mode import MODE
from thread import *
from ultrasonic import *

CONTROL_PORT = 5000
VIDEO_PORT = 8000


def get_interface_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                        0x8915,
                                        struct.pack('256s', b'wlan0'[:15])
                                        )[20:24])


class Server:
    def __init__(self):
        # sockets
        self.control_socket = socket.socket()
        self.video_socket = socket.socket()
        # connections
        self.control_connection = None
        self.video_connection = None
        self.video_stream = None
        # peripherals
        self.motor = Motor()
        self.servo = Servo()
        self.led = Led()
        self.ultrasonic = Ultrasonic()
        self.buzzer = Buzzer()
        self.adc = ADC()
        self.light = Light(self.adc)
        self.infrared = LineTracking()
        # threads
        self.follow_light_thread = Thread(target=self.light.run)
        self.follow_line_thread = Thread(target=self.infrared.run)
        self.ultrasonic_thread = Thread(target=self.ultrasonic.run)
        self.ultrasonic_data_thread = Thread(target=self.send_ultrasonic_data)
        self.light_data_thread = Thread(target=self.send_light_data)
        self.power_data_thread = Thread(target=self.send_power_data)
        self.led_thread = None
        # misc
        self.connection_established = True
        self.ultrasonic_timer_running = False
        self.light_thread_running = False
        self.current_led_mode = None
        self.current_mode = MODE.OFF

    def start_tcp_server(self):
        host = str(get_interface_ip())
        self.control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.control_socket.bind((host, CONTROL_PORT))
        self.control_socket.listen(1)
        self.video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.video_socket.bind((host, VIDEO_PORT))
        self.video_socket.listen(1)
        print('Server address: ' + host)

    def stop_tcp_server(self):
        try:
            self.video_stream.close()
            self.video_connection.close()
            self.control_connection.close()
        except Exception as e:
            print(e)
            print(COMMAND_TERMINATOR + "No client connection")

    def send_command(self, data):
        self.control_connection.send(data.encode('utf-8'))

    def stream_video(self):
        print("Video streaming thread started")
        try:
            self.video_connection, (client_ip, client_port) = self.video_socket.accept()
            self.video_stream = self.video_connection.makefile('wb')
            print("Video client connected from", client_ip, client_port)
        except Exception as e:
            print(e)
            pass
        try:
            with Picamera2() as camera:
                config = camera.create_still_configuration(main={'size': (400, 300)})
                camera.configure(config)
                camera.start()
                time.sleep(2)  # give 2 secs for camera to initialize
                memory_buffer = io.BytesIO()
                # send jpeg format video stream
                print("Start transmit ... ")
                while True:
                    try:
                        camera.capture_file(memory_buffer, format='jpeg')
                        self.video_stream.flush()
                        memory_buffer.seek(0)
                        b = memory_buffer.read()
                        length = len(b)
                        if length > 5120000:
                            continue
                        length_bin = struct.pack('L', length)
                        self.video_stream.write(length_bin)
                        self.video_stream.write(b)
                        memory_buffer.seek(0)
                        memory_buffer.truncate()
                        time.sleep(0.1)
                    except Exception as e:
                        print(e)
                        print("End transmit ... ")
                        break
        except:
            pass
        self.video_socket.close()

    def stop_mode(self):
        try:
            stop_thread(self.power_data_thread)
        except Exception as e:
            print(e)
            pass
        try:
            stop_thread(self.follow_line_thread)
            self.motor.set_speed(0, 0, 0, 0)
        except Exception as e:
            print(e)
            pass
        try:
            stop_thread(self.follow_light_thread)
            self.motor.set_speed(0, 0, 0, 0)
        except Exception as e:
            print(e)
            pass
        try:
            stop_thread(self.ultrasonic_thread)
            self.motor.set_speed(0, 0, 0, 0)
            self.servo.set_servo_pwm('0', 90)
            self.servo.set_servo_pwm('1', 90)
        except Exception as e:
            print(e)
            pass

    def read_commands(self):
        print("Control thread started")
        try:
            try:
                self.control_connection, (client_ip, client_port) = self.control_socket.accept()
                print("Client connected from", client_ip, client_port)
            except Exception as e:
                print(e)
                print("Client connect failed")
            if not self.power_data_thread.is_alive():
                self.power_data_thread.start()
            rest_cmd = ''
            all_data = ''
            while True:
                try:
                    all_data = rest_cmd + self.control_connection.recv(1024).decode('utf-8')
                except Exception as e:
                    print(e)
                    if self.connection_established:
                        break
                if len(all_data) < 5:
                    rest_cmd = all_data
                    if rest_cmd == '' and self.connection_established:
                        break
                rest_cmd = ''
                if all_data == '':
                    break
                else:
                    cmd_array = all_data.split(COMMAND_TERMINATOR)
                    if cmd_array[-1] != "":
                        rest_cmd = cmd_array[-1]
                        cmd_array = cmd_array[:-1]

                for oneCmd in cmd_array:
                    data = oneCmd.split(COMMAND_SEPARATOR)
                    if data is None:
                        continue
                    elif COMMAND.CMD_MODE in data:
                        if data[1] == MODE.OFF:
                            self.stop_mode()
                            self.current_mode = MODE.OFF
                        elif data[1] == MODE.FOLLOW_LIGHT:
                            self.stop_mode()
                            self.current_mode = MODE.FOLLOW_LIGHT
                            self.follow_light_thread.start()
                        elif data[1] == MODE.ULTRASONIC_OBSTACLE_DETECTION:
                            self.stop_mode()
                            self.current_mode = MODE.ULTRASONIC_OBSTACLE_DETECTION
                            self.ultrasonic_thread.start()
                        elif data[1] == MODE.FOLLOW_LINE:
                            self.stop_mode()
                            self.current_mode = MODE.FOLLOW_LINE
                            self.follow_line_thread.start()

                    elif (COMMAND.CMD_MOTOR in data) and self.current_mode == MODE.OFF:
                        try:
                            data1, data2, data3, data4 = [int(d) for d in data[1:]]
                            if data1 is None or data2 is None or data2 is None or data3 is None:
                                continue
                            self.motor.set_speed(data1, data2, data3, data4)
                        except:
                            pass
                    elif COMMAND.CMD_SERVO in data:
                        try:
                            data1 = data[1]
                            data2 = int(data[2])
                            if data1 is None or data2 is None:
                                continue
                            self.servo.set_servo_pwm(data1, data2)
                        except:
                            pass

                    elif COMMAND.CMD_LED in data:
                        try:
                            data1, data2, data3, data4 = [int(d) for d in data[1:]]
                            if data1 is None or data2 is None or data2 is None or data3 is None:
                                continue
                            self.led.led_index(data1, data2, data3, data4)
                        except:
                            pass
                    elif COMMAND.CMD_LED_MOD in data:
                        self.current_led_mode = data[1]
                        if self.current_led_mode == '0':
                            try:
                                stop_thread(self.led_thread)
                            except:
                                pass
                            self.led.led_mode(self.current_led_mode)
                            time.sleep(0.1)
                            self.led.led_mode(self.current_led_mode)
                        else:
                            try:
                                stop_thread(self.led_thread)
                            except:
                                pass
                            time.sleep(0.1)
                            self.led_thread = Thread(target=self.led.led_mode, args=(data[1],))
                            self.led_thread.start()
                    elif COMMAND.CMD_SONIC in data:
                        if data[1] == '1':
                            self.ultrasonic_timer_running = True
                            if not self.ultrasonic_data_thread.is_alive():
                                self.ultrasonic_data_thread = Thread(target=self.send_ultrasonic_data)
                                self.ultrasonic_data_thread.start()
                        else:
                            self.ultrasonic_timer_running = False
                    elif COMMAND.CMD_BUZZER in data:
                        try:
                            self.buzzer.run(data[1])
                        except:
                            pass
                    elif COMMAND.CMD_LIGHT in data:
                        if data[1] == '1':
                            self.light_thread_running = True
                            if not self.light_data_thread.is_alive():
                                self.light_data_thread = Thread(target=self.send_light_data)
                                self.light_data_thread.start()
                        else:
                            self.light_thread_running = False
                    elif COMMAND.CMD_POWER in data:
                        adc_power = self.adc.recv(2) * 3
                        try:
                            self.send_command(
                                COMMAND.CMD_POWER + COMMAND_SEPARATOR + str(adc_power) + COMMAND_TERMINATOR)
                        except:
                            pass
        except Exception as e:
            print(e)
        self.control_socket.close()
        self.stop_tcp_server()

    def send_ultrasonic_data(self):
        while True:
            if self.ultrasonic_timer_running:
                adc_ultrasonic = self.ultrasonic.get_distance()
                try:
                    self.send_command(COMMAND.CMD_SONIC + COMMAND_SEPARATOR + str(adc_ultrasonic) + COMMAND_TERMINATOR)
                except Exception as e:
                    print(e)
                    self.ultrasonic_timer_running = False
                    break
                time.sleep(0.1)
            else:
                break

    def send_light_data(self):
        while True:
            if self.light_thread_running:
                adc_light1 = self.adc.recv(0)
                adc_light2 = self.adc.recv(1)
                try:
                    self.send_command(COMMAND.CMD_LIGHT + COMMAND_SEPARATOR + str(adc_light1) + COMMAND_SEPARATOR + str(
                        adc_light2) + COMMAND_TERMINATOR)
                except Exception as e:
                    print(e)
                    self.light_thread_running = False
                    break
                time.sleep(0.1)
            else:
                break

    def send_power_data(self):
        while True:
            adc_power = self.adc.recv(2) * 3
            try:
                self.send_command(COMMAND.CMD_POWER + COMMAND_SEPARATOR + str(adc_power) + COMMAND_TERMINATOR)
            except Exception as e:
                print(e)
                break
            time.sleep(30)

    def power(self):
        while True:
            adc_power = self.adc.recv(2) * 3
            print(f"Current power {adc_power}V")
            time.sleep(60)
            if adc_power < 6.8:
                for i in range(4):
                    self.buzzer.on()
                    time.sleep(0.1)
                    self.buzzer.off()
                    time.sleep(0.1)
            elif adc_power < 7:
                for i in range(2):
                    self.buzzer.on()
                    time.sleep(0.1)
                    self.buzzer.off()
                    time.sleep(0.1)
            else:
                self.buzzer.off()


if __name__ == '__main__':
    pass
