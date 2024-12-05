import struct
import socket

class UDPpacket:
    def __init__(self, seq_nr=0,file_size=0,packet_type='normal',operation='send',data=b''):
        self.seq_nr = seq_nr
        self.file_size = file_size
        self.packet_type = packet_type
        self.operation = operation
        self.data = data # send, receive, upload, download

    #def pack(self):
