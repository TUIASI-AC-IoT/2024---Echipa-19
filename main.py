import threading
import time
from client import ClientUDP
from server import ServerUDP

if __name__ == '__main__':

    # Staring the server on a different thread
    server = ServerUDP()
    thread_s = threading.Thread(target=server.receive, args=())
    thread_s.start()

    thread_ss = threading.Thread(target=server.send_file, args=())
    thread_ss.start()

    # Starting the client
    client = ClientUDP()
    thread_c = threading.Thread(target=client.receive, args=())
    thread_c.start()

    print(f"Server -> Starting.. Active threads :{threading.active_count() - 1}")  # how many threads

    client.send_message("Hello!")
    time.sleep(1)
    server.send_message("Hi there!")
    time.sleep(1)

    client.send_request("Doc2.txt")
    time.sleep(10)  # timp sa se trimita frame_urile
    client.disconnect()

    thread_c.join()
    thread_s.join()
    thread_ss.join()

