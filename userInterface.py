# interfata client care comunica cu server
import os
import shutil
from packet import *

""" comanda packete comunicare:
    0 - mesaj simplu
    1 - frame
    
        - clientul vrea de la server fisierele si directoarele
    201 - client vrea ca server-ul sa avanseze in working_directory
    202 - client vrea ca server-ul sa se intoarca inapoi in working_directory
    203 - client vrea descarcare fisier( nume fisier este transmis in packet.data) ce se afla in working_directory
    204 - client vrea creare/incarcare fisier/director in working directory (daca packet.data e terminat in txt se creaza fisier daca nu director)
    205 - client vrea stergere firier/director ---||---
    206 - client vrea mutare fisier in alt director
"""
def start_menu():
    print("░█░█░█▀▀░█░░░█▀▀░█▀█░█▄█░█▀▀░░░▀█▀░█▀█░░░▀█▀░█░█░█▀▀░░░█▀▀░█▀▀░█▀▄░█░█░█▀▀░█▀▄")
    print("░█▄█░█▀▀░█░░░█░░░█░█░█░█░█▀▀░░░░█░░█░█░░░░█░░█▀█░█▀▀░░░▀▀█░█▀▀░█▀▄░▀▄▀░█▀▀░█▀▄")
    print("░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀▀▀░░░░▀░░▀▀▀░░░░▀░░▀░▀░▀▀▀░░░▀▀▀░▀▀▀░▀░▀░░▀░░▀▀▀░▀░▀")

def show_menu():

    print("▣ List files and directories from Server(1)")
    print("▣ Download files from Server (2)")
    print("▣ Upload files on Server (3)")
    print("▣ Delete files from Server (4)")
    print("▣ Move a file from current directory to another directory on Server (5)")
    print("▣ Go to a chosen directory (6)")
    print("▣ Return to home directory (7)")
    print("-----------------------------------------------------------------------------")


def list_files_and_dirs(directory_path):
    # List all files and directories in the specified directory
    try:
        # Get the list of files and directories
        files_and_dirs = os.listdir(directory_path)
        for x in files_and_dirs:
            if x.endswith(".txt"):
                print(f"file -> {x}")
            else:
                print(f"dir ->  {x}")
        return files_and_dirs
    except FileNotFoundError:
        return ["Directory not found"]


def get_choice():
    while True:
        try:
            choice = int(input("▣ Please choose an option (1-7): "))
            if choice in [1, 2, 3, 4,5,6,7]:
                return choice
            else:
                print("Invalid option, please choose a number between 1 and 7.")
        except ValueError:
            print("Invalid input! Please enter a number between 1 and 7.")

def create_file(directory_path, file_name):
    try:
        with open(directory_path+"\\"+file_name, 'x') as file:
            print(f"File {file_name} was created")
    except FileExistsError:
        print("The file already exists!")


def delete_file(directory_path, file_name):
    if os.path.exists(directory_path+"\\"+file_name):
        os.remove(directory_path+"\\"+file_name)
    else:
        print("The file does not exist")

    print(f"File {file_name} was deleted.")


def exists_file(directory_path, file_name):
    file_path = os.path.join(directory_path, file_name)
    ok = False
    if os.path.exists(file_path):
        f.write(f"The file {file_name} exists.\n")
        ok = True
    else:
        print(f"The file {file_name} does not exist.")

    return ok

def move_file(source_path, destination_path):
    # source_path: A string representing the path of the source file.
    # destination_path: A string representing the path of the destination file or directory
    #  If the destination is a directory then the file will be copied into the destination using the base filename from the source.
    #  Also, the destination must be writable.
    #  If the destination is a file and already exists then it will be replaced with the source file otherwise a new file will be created.
    try:
        if not os.path.exists(destination_path):
            print("The destination directory does not exist.")
            os.mkdir(destination_path)
            print("The destination directory has been created.")
        shutil.move(source_path, destination_path)
        print(f"File moved from {source_path} to {destination_path}")
    except FileNotFoundError:
        print(f"The file {source_path} was not found.")
    except PermissionError:
        print(f"You do not have permission to move the file.")
    except Exception as e:
        print(f"An error occurred: {e}")


def remove_directory(directory_path, dir_name):
    try:
        os.rmdir(directory_path+"\\"+dir_name)
    except IsADirectoryError:
        print("Can't remove directory until it is empty")
    except NotADirectoryError:
        print("Not a directory")
    except PermissionError:
        print("You don't have permission to remove the directory.")
