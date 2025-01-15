import struct
# BUFFER_SIZE = 1024
BUFFER_SIZE = 512
HEADER_SIZE = 12  # bytes struct.calculate("i")

#fisier in care stocam comunicarea dintre server si client
f=open("comunicare.txt","w")

class PacketUDP:
    def __init__(self, sequence_number=0, command_type=0, total_length=0, packet_data=''):
        self.seq_num = sequence_number
        self.comm_type = command_type
        self.length = total_length
        self.data = packet_data

    def update(self, sequence_number, command_type, total_length, packet_data): # cam nefolositoare
        self.seq_num = sequence_number
        self.comm_type = command_type
        self.length = total_length
        self.data = packet_data

    def packing_data(self):
        header_bytes = struct.pack("iii", self.seq_num, self.comm_type, self.length)
        data_bytes = header_bytes + self.data.encode('utf-8')
        return data_bytes

    def unpacking_data(self, data_bytes):
        self.seq_num, self.comm_type, self.length = struct.unpack("iii", data_bytes[:HEADER_SIZE])
        packet_data = data_bytes[HEADER_SIZE:]
        self.data = packet_data.decode('utf-8')


class FilePackets:
    def __init__(self, path_of_file):
        self.total_packets = 0
        self.file_path = path_of_file

    def packetize_file(self):
        # Open the file for reading
        with open(self.file_path, 'r') as file:
            file_data = file.read()  # Read the entire file data
            self.total_packets = len(file_data) // BUFFER_SIZE + (1 if len(file_data) % BUFFER_SIZE != 0 else 0)
            packets = {}  # dictionary where all the packets are gonna be

            # Packetize and send each part of the file
            for i in range(self.total_packets):  # from 0 to total_packets - 1
                # Get the start and end indices of the current packet
                start_idx = i * BUFFER_SIZE
                end_idx = min(start_idx + BUFFER_SIZE, len(file_data))

                packet_data = file_data[start_idx:end_idx]
                packets[i] = packet_data

            packets[self.total_packets] = "EOF"
            self.total_packets += 1

            f.write(f"Sending file {self.file_path} with {self.total_packets} packets. \n")

            return packets


def receive_file(file_path, data, seq_num):
    with open(file_path, 'a') as output_file:  # opened in append mode
        f.write("Waiting to receive packets... \n")

        if data == "EOF":  # Check for end-of-file signal
            print("File transfer completed.")
            output_file.close()
        else:
            # Write the received packet to the file
            output_file.write(data)
            output_file.write(f"@@@ packet {seq_num} @@@")

