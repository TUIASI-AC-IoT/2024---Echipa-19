
import socket
import time
import threading

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

        self.client.settimeout(5)

        self.connected=True #flag pt a controla oprirea thread-urilor

    def send_message(self):
        try:
            while self.connected:

                message=input("Client -> Enter message to send: ")
                self.client.sendto(message.encode(self.format), self.peer_address)

                if message == self.disconnect_message:
                    self.connected = False

        except socket.timeout:
            print("Client -> TIMEOUT: No response from server")
        except ConnectionResetError:
            print("Client -> Connection was closed by the server")

    def receive_message(self):
        try:
            while self.connected:
                try:
                    data_bytes, address = self.client.recvfrom(self.buffer_size)
                    msg = data_bytes.decode(self.format)
                    print(f"Server -> {msg}")
                    if msg=="Server -> Goodbye!":
                        print("Client -> Server disconnected")
                        self.connected = False
                except socket.timeout:
                    continue
        except Exception as e:
            print(f"Client -> Error in receiving message {e}")

    def disconnect(self):
        self.connected=False
        self.send_message(self.disconnect_message)
        self.client.close()
        print("Client -> Disconnected. ")

    def run(self):
        try:
            send_thread=threading.Thread(target=self.send_message)
            recv_thread=threading.Thread(target=self.receive_message)

            send_thread.start()
            recv_thread.start()
            print(self.udp_address)
            send_thread.join()
            recv_thread.join()

        except Exception as e:
            print(f"Client -> Error in running thread {e}")
