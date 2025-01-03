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
        self.client.settimeout(10)  # pt mai tarziu
        self.client.bind(self.udp_address)

        self.disconnect_message = "Disconnect please !"

        self.connected = True

        self.receiver = Receiver()
        self.rcv_message = "Receive please !"

        self.ups_am_pierdut_un_frame = False
        self.working_directory = "C:\\Users\\tiber\\FACULTATE\\RC_p\\CLIENT"
        self.file_path = "C:\\Users\\tiber\\FACULTATE\\RC_p\\CLIENT\\Doc2.txt"

    def send_message(self, message, sequence_number=0):  # seq number de pus packete intermediare
        try:
            packet = PacketUDP(sequence_number, 0, 0, message)  # 0 pt ca e de tip mesaj nu dam ACK
            print(f"Client -> Sending message: {message}, seq num = {sequence_number}")
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

    def send_request(self, file_name):  # doar un exemplu de cum ar trebuii ca client sa trimita request la server

        create_file(self.working_directory, file_name)
        self.file_path = self.working_directory + "\\" + file_name  # file_path = unde se salveaza continutul ce urmeaza a fii primit de la server

        try:
            packet = PacketUDP(0, 203, 0, file_name)
            print(f"Client -> Sending request: download file {file_name} from {self.working_directory}")
            self.client.sendto(packet.packing_data(), self.peer_address)

        except Exception as e:
            print(f"Client -> Error : {e}")

        except ConnectionResetError:
            print("Client -> Connection was closed by the server")

    def process_data(self, packet, client_address):
        if packet.comm_type == 0:  # stand-alone message
            self.process_message(packet, client_address)

        if packet.comm_type == 1:  # frame part of bigger sequence
            self.process_frame(packet, client_address)

    def process_message(self, packet, client_address):
        print(f"Client -> Message received : {packet.data} from : {client_address}")
        if packet.data == self.disconnect_message:
            print("Client -> Disconnect message received. Server disconnected from client.")
            self.connected = False

    def process_frame(self, packet, client_address):
        print(f"Client -> Frame received : {packet.seq_num} from : {client_address}")

        if self.receiver.next_expected_frame == packet.seq_num:  # daca corespunde se trimite direct ACK
            self.send_ack(packet.seq_num, packet.data)
        else:  # pachetul se pune in buffer
            self.send_to_buffer(packet)

    def send_ack(self, seq_num, data):
        self.pierdem_frame()
        if not self.ups_am_pierdut_un_frame:
            print("Client -> pierdem frame")
        else:
            self.receiver.next_expected_frame += 1
            self.send_message("ACK", seq_num)
            receive_file(self.file_path, data, seq_num)

    def send_to_buffer(self, packet):
        if (len(self.receiver.packet_buffer) < PACKET_BUFFER
                and self.receiver.next_expected_frame < packet.seq_num < self.receiver.next_expected_frame + WINDOW_SIZE):
            self.receiver.add_to_buffer(packet.seq_num, packet.data)  # daca nu, se pune in buffer
        else:
            print(f"Packet discarded")

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
        random_integer = random.randint(1, 10)
        if random_integer < 2:
            self.ups_am_pierdut_un_frame = True
        else:
            self.ups_am_pierdut_un_frame = False
