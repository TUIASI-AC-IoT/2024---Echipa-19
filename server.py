import socket
import time
from packet import *
from slidingWindow import *


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
        self.present_time = None
        self.last_frame = None
        self.time_between_ack = None

        self.sender = Sender()

        self.rcv_message = "Receive please !"
        self.sending_frames = False

        self.working_directory = "C:\\Users\\tiber\\FACULTATE\\RC_p\\SERVER"
        self.file_path = "C:\\Users\\tiber\\FACULTATE\\RC_p\\SERVER\\Doc2.txt"
        self.file = FilePackets(self.file_path)
        self.packets = self.file.packetize_file()

    def send_message(self, message, sequence_number=0):
        try:
            packet = PacketUDP(sequence_number, 0, 0, message)
            print(f"Server -> Sending message: {message}")
            self.server.sendto(packet.packing_data(), self.peer_address)

        except Exception as e:
            print(f"Server -> Error : {e}")

        except ConnectionResetError:
            print("Server -> Connection was closed by the server")

    def receive(self):
        while self.connected:
            try:
                data_bytes, client_address = self.server.recvfrom(BUFFER_SIZE + HEADER_SIZE)
                packet = PacketUDP()
                packet.unpacking_data(data_bytes)

                if data_bytes:
                    self.process_data(packet, client_address)

            except Exception as e:
                print(f"Server -> Error : {e}")
                self.connected = False

            except socket.timeout:
                print("Server -> TIMEOUT: No response from client")
                self.connected = False

        self.server.close()

    def process_data(self, packet, client_address):
        if packet.comm_type == 0:  # stand-alone message
            self.process_message(packet, client_address)

        if packet.comm_type == 203:  # look in userInterface for clarifications
            self.sending_frames = True
            # mai trebuie sa facem update la file_path ceva de genul file_path = working_dir + "\\"+ file_name(packet.data)

    def process_message(self, packet, client_address):
        print(f"Server -> Message received {packet.data} from : {client_address}  {packet.seq_num}")
        if packet.data == self.disconnect_message:
            print("Server -> Disconnect message received. Server disconnected from client.")
            self.send_message(self.disconnect_message)  # server sents a message that the client will be disconnected
            self.connected = False

        if packet.data == "ACK":  # verif si seq num sa vedem daca e in sliding window
            self.sender.w_start += 1
            print(f"Server_r w_end {self.sender.w_end} w_start {self.sender.w_start} seq_num {packet.seq_num}")

            if self.sender.w_start == self.file.total_packets:
                self.sending_frames = False

    def send_file(self):
        while self.connected:
            if self.sending_frames:

                self.present_time = time.time()
                if self.present_time is not None and self.last_frame is not None:
                    self.time_between_ack = self.present_time - self.last_frame
                if self.time_between_ack is not None and self.time_between_ack > 0.5:
                    self.sender.go_back_n()
                    print("MERGEM INAPOI")

                if self.sender.frame_num < self.sender.w_start:  # face update la frame_num atunci cand se trimit consecutiv ACK din buffer
                    self.sender.frame_num = self.sender.w_start

                if self.sender.w_end < self.sender.w_start:  # face update la frame_num atunci cand se trimit consecutiv ACK din buffer
                    self.sender.w_end = self.sender.w_start

                if self.sender.frame_num < self.file.total_packets:
                    if self.sender.w_end - self.sender.w_start < WINDOW_SIZE:
                        self.calculate_time()

                        try:
                            packet = PacketUDP(self.sender.frame_num, 1, 0, self.packets[self.sender.frame_num])  # 1 pt ca e de tip frame
                            print(f"Server -> Sending frame {self.sender.frame_num}")
                            self.server.sendto(packet.packing_data(), self.peer_address)
                            self.sender.frame_num += 1
                            self.sender.w_end += 1
                            print(f"Server_s w_end {self.sender.w_end} w_start {self.sender.w_start} frame_num {self.sender.frame_num}")

                        except Exception as e:
                            print(f"Server -> Error : {e}")

                        except ConnectionResetError:
                            print("Server -> Connection was closed by the server")

    def calculate_time(self):
        self.last_frame = time.time()




