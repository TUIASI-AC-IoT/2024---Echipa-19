from client import ClientUDP
from server import ServerUDP

if __name__ == '__main__':

    #Staring the server on a different thread
    server=ServerUDP()
    server.run()

    #Starting the client
    client=ClientUDP()
    client.run()
