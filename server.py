import socket
import threading
import time


class ServerUDP:
    def __init__(self, udp_ip="127.0.0.1", udp_port=5004, peer_ip="127.0.0.1", peer_port=5005, buffer_size=1024, format='utf-8'):
        self.udp_address = (udp_ip, udp_port)
        self.peer_address = (peer_ip, peer_port)
        self.buffer_size = buffer_size
        self.format = format
        self.disconnect_message = "Disconnect please !"
        self.message_send = "Hello Client !"

        self.server = socket.socket(family=socket.AF_INET,  # Address family InterNET IP4
                                    type=socket.SOCK_DGRAM)  # UDP type of socket
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.udp_address)  # when receiving, verify the source IP of the packet

        self.connected = True

    def handle_client(self):
        print("Server -> Ready!")
        while self.connected:
            try:
                data_bytes, client_address = self.server.recvfrom(self.buffer_size)
                msg = data_bytes.decode(self.format)

                if msg:
                    print(f"Server -> Message received : {msg} from : {client_address}")

                    if msg == self.disconnect_message:
                        print("Server -> Disconnect message received. Server disconnected.")
                        self.connected = False
                        self.server.sendto("Server -> Goodbye!".encode(self.format),client_address)
                        break
                    else:
                        response="Server -> Received: {msg}"
                        self.server.sendto(response.encode(self.format), self.peer_address)

            except Exception as e:
                print(f"Server -> Error : {e}")
                self.connected = False
                break

    def send_message(self):
        while self.connected:
            try:
                # send response to client
                self.server.sendto(self.message_send.encode(self.format), self.peer_address)
                # sendto instead of send because is UDP it needs the extra information
                print(f"Server -> Message sent : {self.message_send} from : {self.peer_address}")
                time.sleep(2)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Server -> Error in sending : {e}")
                self.connected = False
                break

    def run(self):
        try:
            recv_thread = threading.Thread(target=self.handle_client, args=())
            send_thread = threading.Thread(target=self.send_message, args=())

            recv_thread.start()
            send_thread.start()

            print(f"Server -> Starting.. Active threads :{threading.active_count() - 1}")  # how many threads
            print(self.udp_address)

            recv_thread.join()
            send_thread.join()

        except Exception as e:
            print(f"Server -> Error : {e}")
        finally:
            self.connected = False
            self.server.close()
            print("Server closed")