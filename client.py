import socket
import time
from packet import *
from slidingWindow import *
from userInterface import *
import random

class ClientUDP:
    def __init__(self, udp_ip="127.0.0.1", udp_port=5005, peer_ip="127.0.0.1", peer_port=5004):
        self.udp_address = (udp_ip, udp_port)
        self.peer_address = (peer_ip, peer_port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.settimeout(200)  # pt mai tarziu
        self.client.bind(self.udp_address)

        self.disconnect_message = "Disconnect please !"

        self.connected = True
        self.sending_frames=False

        self.present_time = None
        self.last_frame = None
        self.time_between_ack = None

        self.receiver = Receiver()
        self.sender=Sender()

        self.ups_am_pierdut_un_frame = False
        self.working_directory = "C:\\Users\\BRAN IOANA ANDREEA\\Desktop\\ProiectRC\\Client"
        self.file_path = "C:\\Users\\BRAN IOANA ANDREEA\\Desktop\\ProiectRC\\Client\\doc.txt"

        #self.file = FilePackets(self.file_path)
        #self.packets = self.file.packetize_file()

        #creare fisier pt afisare mesaje intre client si server
        #verifica daca exista fisierul, daca nu ,il creeaza
        #pt fiecare print din client si server file.write()
        # dupa disconnect in interfata -> inchidere fisier

    def send_message(self, message, sequence_number=0):  # seq number de pus packete intermediare
        try:
            packet = PacketUDP(sequence_number, 0, 0, message)  # 0 pt ca e de tip mesaj nu dam ACK
            f.write(f"Client -> Sending message: {message}, seq num = {sequence_number} \n")
            self.client.sendto(packet.packing_data(), self.peer_address)

        except Exception as e:
            print(f"Client -> Error : {e}")

        except ConnectionResetError:
            print("Client -> Connection was closed by the server")

    def receive(self):
        while self.connected:
            try:
                self.process_frames_buffer()  # procesam pachetele din buffer

                data_bytes, client_address = self.client.recvfrom(BUFFER_SIZE + HEADER_SIZE)
                packet = PacketUDP()
                packet.unpacking_data(data_bytes)

                if data_bytes:
                    self.process_data(packet, client_address)

            except Exception as e:
                print(f"Client -> Error : {e}")
                self.connected = False

        self.client.close()

    def send_request(self, command_type,  file_name):  # doar un exemplu de cum ar trebuii ca client sa trimita request la server
        if command_type == 201:
            try:

                packet = PacketUDP(0, command_type, 0, file_name) # file_name = dir_name
                f.write(f"Client -> Sending request: go to directory {file_name} \n")
                self.client.sendto(packet.packing_data(), self.peer_address)

            except Exception as e:
                print(f"Client -> Error : {e}")

            except ConnectionResetError:
                print("Client -> Connection was closed by the server")

        elif command_type == 202:
            try:

                packet = PacketUDP(0, command_type, 0,file_name)
                f.write(f"Client -> Return to home directory \n")
                self.client.sendto(packet.packing_data(), self.peer_address)

            except Exception as e:
                print(f"Client -> Error : {e}")

            except ConnectionResetError:
                print("Client -> Connection was closed by the server")

        elif command_type == 203:  # client vrea sa descarce
            self.receiver.reset()

            if exists_file(self.working_directory, file_name):
                f.write(f"Client -> File {file_name} will be overwritten! \n")
                delete_file(self.working_directory, file_name)

            create_file(self.working_directory, file_name)
            self.file_path = self.working_directory + "\\" + file_name  # file_path = unde se salveaza continutul ce urmeaza a fii primit de la server

            try:
                packet = PacketUDP(0, command_type, 0, file_name)
                f.write(f"Client -> Sending request: download file {file_name} from {self.working_directory} \n")
                self.client.sendto(packet.packing_data(), self.peer_address)

            except Exception as e:
                print(f"Client -> Error : {e}")

            except ConnectionResetError:
                print("Client -> Connection was closed by the server")

        elif command_type == 204:  # client vrea sa incarce in server fisier
            self.sender.reset()

            self.file_path = os.path.join(self.working_directory, file_name)
            self.file = FilePackets(self.file_path)
            self.packets = self.file.packetize_file()

            if exists_file(self.working_directory, file_name):
                try:
                    packet = PacketUDP(0, command_type, 0, file_name)
                    f.write(f" Client -> Sending request: upload file {file_name} from {self.working_directory} \n")
                    self.client.sendto(packet.packing_data(), self.peer_address)

                except Exception as e:
                    print(f"Client -> Error : {e}")

                except ConnectionResetError:
                    print("Client -> Connection was closed by the server")

                time.sleep(0.2)
                self.sending_frames = True

        elif command_type == 205:

            try:
                packet=PacketUDP(0,command_type,0,file_name)
                f.write(f"Client -> Sending request to delete {file_name} \n ")
                self.client.sendto(packet.packing_data(),self.peer_address)

            except Exception as e:
                print(f"Client -> Error {e}")

            except ConnectionResetError:
                print("Client -> Connection was closed by the server")

        elif command_type == 206: # send_request(206,fisier+" "+dir)
            try:
                packet=PacketUDP(0,command_type,0,file_name)
                f.write(f"Client -> Sending request to delete {file_name} \n")
                self.client.sendto(packet.packing_data(),self.peer_address)

            except Exception as e:
                print(f"Client -> Error {e}")

            except ConnectionResetError:
                print("Client -> Connection was closed by the server")

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
                            f.write(f"Client -> Sending frame {self.sender.frame_num} \n")
                            self.client.sendto(packet.packing_data(), self.peer_address)
                            self.sender.frame_num += 1
                            self.sender.w_end += 1
                            f.write(f"Client_s w_end {self.sender.w_end} w_start {self.sender.w_start} frame_num {self.sender.frame_num} \n")

                        except Exception as e:
                            print(f"Client -> Error : {e}")

    def calculate_time(self):
        self.last_frame = time.time()

    def process_data(self, packet, client_address):
        if packet.comm_type == 0:  # stand-alone message
            self.process_message(packet, client_address)

        if packet.comm_type == 1:  # frame part of bigger sequence
            self.process_frame(packet, client_address)

    def process_message(self, packet, client_address):
        f.write(f"Client -> Message received : {packet.data} {packet.seq_num} from : {client_address} \n")
        if packet.data == self.disconnect_message:
            f.write("Client -> Disconnect message received. Server disconnected from client. \n")
            self.connected = False

        if packet.data == "ACK":  # verif si seq num sa vedem daca e in sliding window
            self.sender.w_start += 1
            f.write(f"Server_r w_end {self.sender.w_end} w_start {self.sender.w_start} seq_num {packet.seq_num} \n")

            if self.sender.w_start == self.file.total_packets:
                self.sending_frames = False

    def process_frame(self, packet, client_address):
        f.write(f"Client -> Frame received : {packet.seq_num} from : {client_address} \n")

        if self.receiver.next_expected_frame == packet.seq_num:  # daca corespunde se trimite direct ACK
            self.send_ack(packet.seq_num, packet.data)
        else:  # pachetul se pune in buffer
            self.send_to_buffer(packet)

    def send_ack(self, seq_num, data):
        self.pierdem_frame()
        if self.ups_am_pierdut_un_frame:
            f.write(f"Client -> pierdem frame {seq_num} \n")
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

    def process_frames_buffer(self):
        if len(self.receiver.packet_buffer) > 0:  # trimitem ack si pt pachetele din buffer
            while self.receiver.next_expected_frame in self.receiver.packet_buffer:
                self.send_message("ACK", self.receiver.next_expected_frame)
                # scriem si packetele din buffer in fisier
                receive_file(self.file_path, self.receiver.packet_buffer[self.receiver.next_expected_frame],self.receiver.next_expected_frame)
                self.receiver.remove_from_buffer(self.receiver.next_expected_frame)
                self.receiver.next_expected_frame += 1

    def disconnect(self):
        self.send_message(self.disconnect_message)

    def pierdem_frame(self):
        random_integer = random.random() * 100
        # f.write(f"NUMARUL RANDOM ESTE {random_integer}")
        if random_integer < 20:
            self.ups_am_pierdut_un_frame = True
        else:
            self.ups_am_pierdut_un_frame = False
