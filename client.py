import socket
from packet import PacketUDP
from packet import HEADER_SIZE
from packet import BUFFER_SIZE
import time

WINDOW_SIZE = 4  # Sender's window size
TOTAL_FRAME_NUM = 10  # Total number of frames to send


class ClientUDP:
    def __init__(self, udp_ip="127.0.0.1", udp_port=5005, peer_ip="127.0.0.1", peer_port=5004):
        self.udp_address = (udp_ip, udp_port)
        self.peer_address = (peer_ip, peer_port)
        self.disconnect_message = "Disconnect please !"
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.client.settimeout(10)  # pt mai tarziu
        self.client.bind(self.udp_address)

        self.connected = True

        # self.receiver = Receiver()
        self.next_expected_frame = 0
        self.rcv_message = "Receive please !"

        self.lost_frame = False

    def send_message(self, message):
        try:

            packet = PacketUDP(0, 0, 0, message)  # 0 pt ca e de tip mesaj nu dam ACK
            print(f"Client -> Sending message: {message}")
            self.client.sendto(packet.packing_data(), self.peer_address)

        except Exception as e:
            print(f"Client -> Error : {e}")

        except ConnectionResetError:
            print("Client -> Connection was closed by the server")

    def receive_message(self):
        while self.connected:
            try:
                data_bytes, client_address = self.client.recvfrom(BUFFER_SIZE + HEADER_SIZE)
                packet = PacketUDP()
                packet.unpacking_data(data_bytes)

                if data_bytes:
                    if packet.comm_type == 0:  # stand-alone message
                        print(f"Client -> Message received : {packet.data} from  {client_address}")
                        if packet.data == self.disconnect_message:
                            print("Client -> Disconnect message received. Server disconnected from client.")
                            self.connected = False

                    if packet.comm_type == 1:  # frame part of bigger sequence
                        print(f"Client -> Received frame {packet.seq_num} from  {client_address}")
                        if self.next_expected_frame == packet.seq_num:
                            if self.next_expected_frame < TOTAL_FRAME_NUM:

                                if self.lost_frame == False and packet.seq_num == 6:
                                    self.lost_frame = True
                                else:
                                    self.next_expected_frame += 1
                                    print(f"Client -> Sending ack...")
                                    self.send_message(f"ACK for frame {packet.seq_num}")
                                    print("\n")

                                #self.next_expected_frame += 1
                                #self.send_message("ACK")
                            else:
                                print(f"Packet discarded")
                        else:
                            print(f"Packet discarded")

            except Exception as e:
                print(f"Client -> Error : {e}")
                self.connected = False

        self.client.close()

    def send_frame(self):  # pt alta data
        pass

    def receive_frame(self):  # pt testare acum se afla in in receive_message
        while self.connected:
            # if self.receiving_frames:
            try:
                data_bytes, client_address = self.client.recvfrom(BUFFER_SIZE + HEADER_SIZE)
                packet = PacketUDP()
                packet.unpacking_data(data_bytes)

                if packet.comm_type == 1:  # frame part of bigger sequence
                    print(f"Client -> Packet received : {packet.seq_num} from : {client_address}")
                    if self.next_expected_frame == packet.seq_num:
                        if self.next_expected_frame < TOTAL_FRAME_NUM:
                            # ups pierdem un frame
                            if self.lost_frame == False and packet.seq_num == 6:
                                self.lost_frame = True
                            else:
                                self.next_expected_frame += 1
                                print(f"Client ack for frame {packet.seq_num}")
                                self.send_message("ACK")
                        else:
                            print(f"Packet discarded")
                    else:
                        print(f"Packet discarded")

            except Exception as e:
                print(f"Client -> Error frame : {e}")
                self.connected = False
                # self.client.close() se aplica cel din receive message

    def disconnect(self):
        self.send_message(self.disconnect_message)
