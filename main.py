import threading
import time
from client import ClientUDP
from server import ServerUDP

if __name__ == '__main__':

    # Staring the server on a different thread
    server = ServerUDP()
    thread_s = threading.Thread(target=server.receive_message, args=())
    thread_s.start()
    # thread_s.join() intr-un fel thread-urile sunt independente unul de altul?

    # Starting the client
    client = ClientUDP()
    thread_c = threading.Thread(target=client.receive_message, args=())
    thread_c.start()
    # thread_c.join()

    print(f"Server -> Starting.. Active threads :{threading.active_count() - 1}")  # how many threads

    thread_ss = threading.Thread(target=server.send_frame, args=())
    thread_ss.start()

    # thread_cc = threading.Thread(target=client.receive_frame, args=())
    #thread_cc.start()

    client.send_message("Hello!")
    time.sleep(1)
    server.send_message("Hi there!")
    time.sleep(1)
    client.send_message(client.rcv_message)
    time.sleep(3) # timp sa se trimita frame_urile
    client.disconnect()

    thread_c.join()
    thread_s.join()
    thread_ss.join()

