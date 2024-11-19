import socket
import threading
import time

class ServerUDP:
    def __init__(self,udp_ip="127.0.0.1",udp_port=5004,peer_ip="127.0.0.1",peer_port=5005,buffer_size=1024,format='utf-8'):
        self.udp_address=(udp_ip,udp_port)
        self.peer_address=(peer_ip,peer_port)
        self.buffer_size=buffer_size
        self.format=format
        self.disconnect_message="Server -> Disconnect please !"
        self.message_send="Server -> Hello Client !"

        self.server = socket.socket(family=socket.AF_INET,  # Address family InterNET IP4
                                    type=socket.SOCK_DGRAM)  # UDP type of socket
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.udp_address)  # when receiving, verify the source IP of the packet


    def handle_client(self):
        print("Server -> Ready!")
        connected = True
        while connected:
            try:
                data_bytes, client_address = self.server.recvfrom(self.buffer_size)
                msg = data_bytes.decode(self.format)

                if data_bytes:
                    print(f"Server -> Message received : {msg} from : {client_address}")

                    if msg == self.disconnect_message:
                        print("Server -> Disconnect message received. Server disconnected.")

                    else:
                        # send response to client
                        self.server.sendto(self.message_send.encode(self.format), self.peer_address)
                        self.server.close()
                        # sendto instead of send because is UDP it needs the extra information

            except Exception as e:
                print(f"Server -> Error : {e}")
                connected=False
                break

        self.server.close()
        print("Server -> Server disconnected.")

    def run(self):
        thread = threading.Thread(target=self.handle_client, args=())
        thread.start()
        print(f"Server -> Starting.. Active threads :{threading.active_count() - 1}") # how many threads
#server