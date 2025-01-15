import struct
BUFFER_SIZE = 1024
HEADER_SIZE = 12  # bytes struct.calculate("i")


class PacketUDP:
    def __init__(self, sequence_number=0, command_type=0, total_length=0, packet_data='0'):
        self.seq_num = sequence_number
        self.comm_type = command_type
        self.length = total_length
        self.data = packet_data

    def update(self, sequence_number, command_type, total_length, packet_data):
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




