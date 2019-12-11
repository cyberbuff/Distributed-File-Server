from socket import *
import os
import sys
import datetime, time
from _thread import start_new_thread


class Server:
    def __init__(self, port, fileDir):
        self.confFile = "dfs.conf"
        self.fileDir = fileDir
        self.host = "127.0.0.1"
        self.port = int(port)
        self.sSocket = None
        self.buffer = 4096
        self.isAuthenticated = False
        self.start()

    def start(self):
        self.checkFileDir()
        self.createSocket()
        self.listenForConnections()

    def checkFileDir(self):
        if not os.path.exists(self.fileDir):
            os.mkdir(self.fileDir)
            log("File Directory Created")

    def createSocket(self):
        try:
            self.sSocket = socket(AF_INET, SOCK_STREAM)
            self.sSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.sSocket.bind(('', self.port))
        except Exception as e:
            log(str(e))
        except error as e:
            log(str(e))

    def listenForConnections(self):
        try:
            self.sSocket.listen(5)
            log("Listening...")
            while True:
                try:
                    clientSocket, clientAddress = self.sSocket.accept()
                    self.connect(clientSocket)
                except Exception as e:
                    log(str(e))
                    # sys.exit(1)

        except KeyboardInterrupt:
            log("Interrupting Server.")
            time.sleep(.5)

        finally:
            log("Stopping Server...")
            sys.exit()

    def connect(self, clientSocket):
        try:
            request = clientSocket.recv(self.buffer)
            userConfig = request.decode().split(" ")
            self.authenticate(userConfig[0],userConfig[1])
            if self.isAuthenticated :
                clientSocket.send("Authenticated".encode())
                self.listenForCommands(clientSocket)
        except Exception as e:
            log(str(e))

    def listenForCommands(self,cSocket):
        while True:
            request = cSocket.recv(self.buffer).decode()
            if request == "LIST":
                print(os.listdir(self.fileDir))
                cSocket.sendall("\n".join(os.listdir(self.fileDir)).encode())
            elif request == "PUT":
                self.receiveFile()

    def receiveFile(self):
        log("Receiving File...")

    def authenticate(self,username,password):
        try:
            with open(self.confFile, "r") as f:
                x = [i.split(":")[1].rstrip() for i in f.readlines()]
                if x[0] == username and x[1] == password:
                    log("Authentication Successful")
                    self.isAuthenticated = True
                else:
                    raise Exception("Authentication Failed")
                    self.sSocket.close()
        except Exception as e:
            log(str(e))


def log(message):
    logtime = timestamp()
    print(logtime + " : " + message)


def timestamp():
    return "[" + str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + "]"


if __name__ == "__main__":
    if len(sys.argv) > 2:
        s = Server(sys.argv[2], sys.argv[1].replace("/", ""))
    else:
        print("Usage: python3 server.py /DFS1 10001")
