import threading
import time
from client import ClientUDP
from server import ServerUDP
from packet import *
from userInterface import *

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

    thread_cc = threading.Thread(target=client.send_file, args=())
    thread_cc.start()

    f.write(f"Server -> Starting.. Active threads :{threading.active_count() - 1} \n")  # how many threads

    start_menu()
    show_menu()
    ok=1 #variabila pentru a sti cand utilizatorul doreste sa continue operatiile sau nu1

    while ok==1:

        choice=get_choice()

        if choice == 1:
            print("Files and directories:")
            print(server.working_directory)
            list_files_and_dirs(server.working_directory)

            ok=int(input("▣ Do you want to continue? (0-no, 1-yes):  "))

        elif choice == 2:
            file_download = input("▣ Please choose a file from Server to download (file_name.txt) : ")
            client.send_request(203,file_download)
            time.sleep(10)

            ok=int(input("▣ Do you want to continue? (0-no, 1-yes):  "))

        elif choice == 3:
            file_upload=input("▣ Please choose a file from Client to upload on Server (file_name.txt) : ")
            client.send_request(204,file_upload)
            time.sleep(10)

            ok=int(input("▣ Do you want to continue? (0-no, 1-yes):  "))

        elif choice == 4:
            file_delete=input("▣ Please choose a file to delete (file_name.txt) : ")
            client.send_request(205,file_delete)
            time.sleep(10)

            ok=int(input("▣ Do you want to continue? (0-no, 1-yes):  "))

        elif choice == 5:
            file_move=input("▣ Please choose a file to move (file_name.txt directory_name) : ")
            client.send_request(206,file_move)
            time.sleep(10)

            ok=int(input("▣ Do you want to continue? (0-no, 1-yes):  "))

        elif choice == 6:
            dir_name=input("▣ Please choose a directory (dir_name ):  ")
            client.send_request(201,dir_name)
            time.sleep(10)

            ok=int(input("▣ Do you want to continue? (0-no, 1-yes):  "))

        elif choice == 7:
            client.send_request(202,"")
            time.sleep(10)

            ok=int(input("▣ Do you want to continue? (0-no, 1-yes):  "))

    client.disconnect()

    thread_c.join()
    thread_s.join()
    thread_ss.join()
    thread_cc.join()

    f.close()

