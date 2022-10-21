import socket


class Control:
    def __init__(self, ip):
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        try:
            self.command_socket.connect((ip, 5000))
            self.connected = True
            print("Connection Successful !")
        except Exception as e:
            print(e)
            print("Connect to server Failed!: Server IP is right? Server is opened?")
            self.connected = False
            raise e

    def stop_tcp_client(self):
        try:
            self.command_socket.shutdown(2)
            self.command_socket.close()
        except Exception as e:
            print(e)
            pass

    def send_data(self, s):
        if self.connected:
            self.command_socket.send(s.encode('utf-8'))

    def recv_data(self):
        if not self.connected:
            return ""
        try:
            return self.command_socket.recv(1024).decode('utf-8')
        except Exception as e:
            print(e)
            pass
        return ""


if __name__ == '__main__':
    pass
