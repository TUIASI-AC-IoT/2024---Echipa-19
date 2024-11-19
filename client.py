import socket
import time


class ClientUDP:
    def __init__(self, udp_ip="127.0.0.1", udp_port=5005, peer_ip="127.0.0.1", peer_port=5004, buffer_size=1024, format='utf-8'):
        self.udp_address = (udp_ip, udp_port)
        self.peer_address = (peer_ip, peer_port)
        self.buffer_size = buffer_size
        self.format = format
        self.disconnect_message = "Disconnect please !"
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.settimeout(1)
        self.client.bind(self.udp_address)

    def send_message(self, message):
        try:
            print(f"Client -> Sending message: {message}")
            self.client.sendto(message.encode(self.format), self.peer_address)

            data_bytes, address = self.client.recvfrom(self.buffer_size)
            msg = data_bytes.decode(self.format)
            print(f"Client -> Message received : {msg}")

        except socket.timeout:
            print("Client -> TIMEOUT: No response from server")
        except ConnectionResetError:
            print("Client -> Connection was closed by the server")

    def disconnect(self):
        self.send_message(self.disconnect_message)
        self.client.close()

    def run(self):
        self.send_message("Hello Server")
        time.sleep(1) # to give to time to server to process the message
        self.disconnect()
