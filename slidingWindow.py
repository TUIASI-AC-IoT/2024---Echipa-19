WINDOW_SIZE = 4  # Sender's window size
PACKET_BUFFER = 5  # size of buffer for out of order packets


class Sender:
    def __init__(self):
        self.w_start = 0
        self.w_end = 0
        self.frame_num = 0

    def go_back_n(self):
        if self.w_end != self.w_start:
            self.w_end = self.w_start
        if self.frame_num != self.w_start:
            self.frame_num = self.w_start


class Receiver:
    def __init__(self):
        self.next_expected_frame = 0
        self.packet_buffer = {}  # dictionary type data

    def add_to_buffer(self, seq_num, data):
        self.packet_buffer[seq_num] = data

    def clear_buffer(self):
        self.packet_buffer.clear()

    def remove_from_buffer(self, seq_num):
        self.packet_buffer.pop(seq_num)
