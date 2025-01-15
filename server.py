import socket
import time
from packet import *
from slidingWindow import *
from userInterface import *
import random

class ServerUDP:
    def __init__(self, udp_ip="127.0.0.1", udp_port=5004, peer_ip="127.0.0.1", peer_port=5005):
        self.udp_address = (udp_ip, udp_port)
        self.peer_address = (peer_ip, peer_port)
        self.disconnect_message = "Disconnect please !"

        self.server = socket.socket(family=socket.AF_INET,  # Address family InterNET IP4
                                    type=socket.SOCK_DGRAM)  # UDP type of socket
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.settimeout(200) # daca nu primeste ack in 0.5 sec
        self.server.bind(self.udp_address)  # when receiving, verify the source IP of the packet

        self.connected = True
        self.present_time = None
        self.last_frame = None
        self.time_between_ack = None

        self.sender = Sender()
        self.receiver=Receiver()

        self.sending_frames = False

        self.ups_am_pierdut_un_frame = False

        self.home_directory = "C:\\Users\\BRAN IOANA ANDREEA\\Desktop\\ProiectRC\\Server"
        self.working_directory = "C:\\Users\\BRAN IOANA ANDREEA\\Desktop\\ProiectRC\\Server"
        self.file_path = "C:\\Users\\BRAN IOANA ANDREEA\\Desktop\\ProiectRC\\Server\\doc.txt"
        #self.file = FilePackets(self.file_path)
        #self.packets = self.file.packetize_file()

    def send_message(self, message, sequence_number=0):
        try:
            packet = PacketUDP(sequence_number, 0, 0, message)
            f.write(f"Server -> Sending message: {message} \n ")
            self.server.sendto(packet.packing_data(), self.peer_address)

        except Exception as e:
            print(f"Server -> Error : {e}")

        except ConnectionResetError:
            print("Server -> Connection was closed by the server")

    def receive(self):
        while self.connected:
            try:
                self.process_frames_buffer()

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


    def process_frames_buffer(self):
        if len(self.receiver.packet_buffer) > 0:  # trimitem ack si pt pachetele din buffer
            while self.receiver.next_expected_frame in self.receiver.packet_buffer:
                self.send_message("ACK", self.receiver.next_expected_frame)
                # scriem si packetele din buffer in fisier
                receive_file(self.file_path, self.receiver.packet_buffer[self.receiver.next_expected_frame],self.receiver.next_expected_frame)
                self.receiver.remove_from_buffer(self.receiver.next_expected_frame)
                self.receiver.next_expected_frame += 1

    def process_data(self, packet, client_address):
        if packet.comm_type == 0:  # stand-alone message
            self.process_message(packet, client_address)

        elif packet.comm_type == 1:
            self.process_frame(packet, client_address)

        elif packet.comm_type == 201: #avansare in directorul home in directorul dat
            #create_directory(self.home_directory,packet.data)
            self.working_directory = self.home_directory+"\\"+packet.data

        elif packet.comm_type == 202: # se intoarce in directorul home f
            self.working_directory=self.home_directory

        elif packet.comm_type == 203:  # look in userInterface for clarifications
            self.sender.reset()

            self.sending_frames = True
            f_name = packet.data
            self.file_path = os.path.join(self.working_directory, f_name)  # update file_path, server = SENDER
            self.file = FilePackets(self.file_path)
            self.packets = self.file.packetize_file()

        elif packet.comm_type == 204:  # server asteapta sa primeasca
            self.receiver.reset()

            f_name=packet.data
            if exists_file(self.working_directory, packet.data):
                print(f"Server -> File {f_name} will be overwritten!")
                delete_file(self.working_directory, f_name)

            create_file(self.working_directory, f_name)
            self.file_path = os.path.join(self.working_directory, f_name) #update file_path, unde se descarca datele

        elif packet.comm_type == 205:
            f_name=packet.data
            if f_name.endswith(".txt"):
                delete_file(self.working_directory, f_name)
            else:
                remove_directory(self.working_directory, f_name)

        elif packet.comm_type == 206: # name_list[0] - filename, name_list[1] - dir_name
            name_list=packet.data.split(" ")
            source_path=self.working_directory+"\\"+name_list[0]
            destination_path=self.home_directory+"\\"+name_list[1]
            move_file(source_path,destination_path)

    def process_message(self, packet, client_address):
        f.write(f"Server -> Message received {packet.data} from : {client_address}  {packet.seq_num} \n")
        if packet.data == self.disconnect_message:
            f.write("Server -> Disconnect message received. Server disconnected from client.\n")
            self.send_message(self.disconnect_message)  # server sents a message that the client will be disconnected
            self.connected = False

        if packet.data == "ACK":  # verif si seq num sa vedem daca e in sliding window
            self.sender.w_start += 1
            f.write(f"Server_r w_end {self.sender.w_end} w_start {self.sender.w_start} seq_num {packet.seq_num} \n")

            if self.sender.w_start == self.file.total_packets:
                self.sending_frames = False

    def process_frame(self, packet, client_address):
        f.write(f"Server -> Frame received : {packet.seq_num} from : {client_address} \n")

        if self.receiver.next_expected_frame == packet.seq_num:  # daca corespunde se trimite direct ACK
            self.send_ack(packet.seq_num, packet.data)
        else:  # pachetul se pune in buffer
            self.send_to_buffer(packet)

    def send_ack(self, seq_num, data):
        self.pierdem_frame()
        if not self.ups_am_pierdut_un_frame:
            f.write(f"Server -> pierdem frame {seq_num} \n")
        else:
            self.receiver.next_expected_frame += 1
            self.send_message("ACK", seq_num)
            receive_file(self.file_path, data, seq_num)

    def send_to_buffer(self, packet):
        if (len(self.receiver.packet_buffer) < PACKET_BUFFER
                and self.receiver.next_expected_frame < packet.seq_num < self.receiver.next_expected_frame + WINDOW_SIZE):
            self.receiver.add_to_buffer(packet.seq_num, packet.data)  # daca nu, se pune in buffer
        else:
            f.write(f"Packet discarded \n")

    def send_file(self):
        while self.connected:
            if self.sending_frames:

                self.present_time = time.time()
                if self.present_time is not None and self.last_frame is not None:
                    self.time_between_ack = self.present_time - self.last_frame
                if self.time_between_ack is not None and self.time_between_ack > 0.5:
                    self.sender.go_back_n()
                    f.write("MERGEM INAPOI \n")

                if self.sender.frame_num < self.sender.w_start:  # face update la frame_num atunci cand se trimit consecutiv ACK din buffer
                    self.sender.frame_num = self.sender.w_start

                if self.sender.w_end < self.sender.w_start:  # face update la frame_num atunci cand se trimit consecutiv ACK din buffer
                    self.sender.w_end = self.sender.w_start

                if self.sender.frame_num < self.file.total_packets:
                    if self.sender.w_end - self.sender.w_start < WINDOW_SIZE:
                        self.calculate_time()

                        try:
                            packet = PacketUDP(self.sender.frame_num, 1, 0, self.packets[self.sender.frame_num])  # 1 pt ca e de tip frame
                            f.write(f"Server -> Sending frame {self.sender.frame_num} \n")
                            self.server.sendto(packet.packing_data(), self.peer_address)
                            self.sender.frame_num += 1
                            self.sender.w_end += 1
                            f.write(f"Server_s w_end {self.sender.w_end} w_start {self.sender.w_start} frame_num {self.sender.frame_num} \n")

                        except Exception as e:
                            print(f"Server -> Error : {e}")

                        except ConnectionResetError:
                            print("Server -> Connection was closed by the server")

    def calculate_time(self):
        self.last_frame = time.time()

    def pierdem_frame(self):
        random_integer = random.random() * 100
        # print(f"NUMARUL RANDOM ESTE {random_integer}")
        if random_integer < 20:
            self.ups_am_pierdut_un_frame = True
        else:
            self.ups_am_pierdut_un_frame = False



