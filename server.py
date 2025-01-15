import socket
from packet import PacketUDP
from packet import HEADER_SIZE
from packet import BUFFER_SIZE
import time
WINDOW_SIZE = 4  # Sender's window size
TOTAL_FRAME_NUM = 10  # Total number of frames to send


class ServerUDP:
    def __init__(self, udp_ip="127.0.0.1", udp_port=5004, peer_ip="127.0.0.1", peer_port=5005):
        self.udp_address = (udp_ip, udp_port)
        self.peer_address = (peer_ip, peer_port)
        self.disconnect_message = "Disconnect please !"

        self.server = socket.socket(family=socket.AF_INET,  # Address family InterNET IP4
                                    type=socket.SOCK_DGRAM)  # UDP type of socket
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.settimeout(10) # daca nu primeste ack in 0.5 sec
        self.server.bind(self.udp_address)  # when receiving, verify the source IP of the packet

        self.connected = True
        self.last_ack_time = None
        self.last_frame = None
        self.time_between_ack = None

        # self.sender = Sender()
        self.w_start = 0
        self.w_end = 0
        self.frame_num = 0

        self.rcv_message = "Receive please !"
        self.sending_frames = False

    def send_message(self, message):
        try:
            packet = PacketUDP(0, 0, 0, message)  # 0 pt ca e de tip mesaj nu dam ACK
            print(f"Server -> Sending message: {message}")
            self.server.sendto(packet.packing_data(), self.peer_address)

        except Exception as e:
            print(f"Server -> Error : {e}")

        except ConnectionResetError:
            print("Server -> Connection was closed by the server")

    def receive_message(self):
        while self.connected:
            try:
                data_bytes, client_address = self.server.recvfrom(BUFFER_SIZE + HEADER_SIZE)
                packet = PacketUDP()
                packet.unpacking_data(data_bytes)

                if data_bytes:
                    if packet.comm_type == 0:  # stand-alone message
                        print(f"Server -> Message received : {packet.data} from  {client_address}")
                        if packet.data == self.disconnect_message:
                            print("Server -> Disconnect message received. Server disconnected from client.")
                            self.send_message(self.disconnect_message)  # server sents a message that the client will be disconnected
                            self.connected = False

                        if packet.data == self.rcv_message:
                            self.sending_frames = True

                        if packet.data == "ACK":

                            self.last_ack_time = time.time()

                            self.w_start += 1
                            print(f"Server -> for frame {self.frame_num} w_end {self.w_end} w_start {self.w_start}")

                            if self.w_start == TOTAL_FRAME_NUM:
                                self.sending_frames = False

            except Exception as e:
                print(f"Server -> Error : {e}")
                self.connected = False

            except socket.timeout:
                print("Server -> TIMEOUT: No response from client")
                self.connected = False

        self.server.close()

    def send_frame(self):
        # comparing None with float is not possible in Python3
        while self.connected:
            if self.sending_frames:

                self.last_frame = time.time()
                if self.last_ack_time is not None and self.last_frame is not None:
                    self.time_between_ack = self.last_frame - self.last_ack_time

                if self.time_between_ack is not None and self.time_between_ack > 0.3:
                    self.go_back_n()
                    print("Go back !")

                if (self.w_end < TOTAL_FRAME_NUM) and self.w_end - self.w_start < WINDOW_SIZE:
                    try:
                        packet = PacketUDP(self.frame_num, 1, 0, "BunA ZIua DOiRti uN MEsAJ")  # 1 pt ca e de tip frame
                        print(f"\nServer -> Sending frame {self.frame_num}")
                        self.server.sendto(packet.packing_data(), self.peer_address)
                        self.frame_num += 1
                        self.w_end += 1
                        print(f"Server -> for frame {self.frame_num -1} w_end={self.w_end} w_start={self.w_start}")

                    except Exception as e:
                        print(f"Server -> Error : {e}")

                    except ConnectionResetError:
                        print("Server -> Connection was closed by the server")

    def receive_frame(self):
        pass

    def go_back_n(self):
        self.w_end = self.w_start
        self.frame_num = self.w_start
