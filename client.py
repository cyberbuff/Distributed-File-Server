import hashlib
import os
import sys
import time
from socket import *
import datetime
from _thread import start_new_thread


class Server:
    def __init__(self, directory, address, sock):
        self.directory = directory
        self.address = address
        self.sock = socket


class Client:
    def __init__(self, conf):
        self.confFile = conf
        self.buffer = 4096
        self.fileDir = os.path.dirname(os.path.realpath(__file__))
        self.clientFilesDir = os.path.join(self.fileDir, "ClientFiles")
        self.serverFilesDir = []
        self.servers = []
        self.username = ""
        self.password = ""
        self.start()

    def start(self):
        self.connectToServers()
        self.createClientFilesDir()

    def createClientFilesDir(self):
        if not os.path.exists(self.clientFilesDir):
            os.mkdir(self.clientFilesDir)
            log("Client File Directory Created")

    def doesFileExist(self, filePath):
        return os.path.exists(filePath)

    def calculateHash(self, filename):
        md5hash = hashlib.md5(filename.encode())
        return (int(md5hash.hexdigest(), 16)) % 4

    def connectToServers(self):
        servers = []
        with open(self.confFile, "r") as f:
            x = [i.rstrip() for i in f.readlines()]
            print(x)
            s = x[:4]
            self.username = x[5].split(":")[1].rstrip()
            self.password = x[6].split(":")[1].rstrip()
            for i in s:
                serverDir = i.split(" ")[1]
                serverConf = i.split(" ")[2].split(":")
                serverAddress = (serverConf[0], int(serverConf[1]))
                serverX = Server(serverDir, serverAddress, None)
                servers.append(serverX)
            self.createConnections(servers)

    def createConnections(self, servers):
        for i in servers:
            self.acceptSocket(i)
        self.listenForCommands()
        # (self.acceptSocket, (i))
        # print(self.sockets)

    def acceptSocket(self, serverX):
        try:
            cSocket = socket(AF_INET, SOCK_STREAM)
            cSocket.connect(serverX.address)
            userConfig = self.username + " " + self.password
            cSocket.sendall(userConfig.encode())
            response = cSocket.recv(self.buffer)
            if response.decode() == "Authenticated":
                serverX.sock = cSocket
                self.servers.append(serverX)
        except error as e:
            log(str(e))
            print(len(self.servers))

    def listenForCommands(self):
        statements = "\n".join(["Available Commands:", "LIST", "PUT", "GET"])
        print(statements)
        while True:
            msg = input('Please enter the command : ')
            if msg is "LIST":
                self.getList(msg)
            elif msg == "PUT":
                print("\n".join(os.listdir(self.clientFilesDir)))
                print("Select the file to send:")

    def getList(self):
        response = []
        for i in self.servers:
            response += self.communicate(i, "LIST")
        print(response)
        responseArray = list(dict.fromkeys(response))
        completeList = []
        incompleteList = []
        for i in responseArray:
            fileName = i[:-2]
            if self.isComplete(fileName, responseArray):
                if not (fileName in completeList):
                    completeList.append(fileName)
            else:
                if not (fileName in incompleteList):
                    incompleteList.append(fileName)
        for i in completeList:
            print(i)
        for j in incompleteList:
            print(j + "[incomplete]")

    def isComplete(self, filename, fileArray):
        fileParts = [(filename+".{0}").format(i) for i in range(0,4)]
        return set(fileParts) <= set(fileArray)

    def communicate(self, server, request):
        server.sock.send(request.encode())
        response = server.sock.recv(self.buffer).decode()
        print(response)
        return response.split("\n")


def log(message):
    logtime = timestamp()
    print(logtime + " : " + message)


def timestamp():
    return "[{0}]".format(str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        c = Client(sys.argv[1])
    else:
        c = Client("dfc.conf")
        # print("Usage: python3 dfc dfc.conf")
