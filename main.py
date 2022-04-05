import json
import socket
import sys
import threading
import time
from copyreg import constructor

# message = {
#     'message_type': 'Reply' | 'Request',
#     'address': '127.0.0.1',
#     'port': 4567 | 5678 | 6789,
#     'processTime': time.time(),
#   'name': ''
# }


class process():
    def __init__(self, address, port, name):
        self.address = address
        self.port = port
        self.name = name
        self.remotes = []
        self.state = 'Released'
        self.requestedTime = time.time()
        self.replyQueue = []
        self.waitingQueue = []

        self.listenThread = threading.Thread(target=self.listen_messages)
        self.listenThread.start()

    def set_address(self, address):
        self.address = address

    def set_port(self, port):
        self.port = port

    def set_remote(self, remoteAddress, remotePort):
        self.remotes.append((remoteAddress, remotePort))

    def listen_messages(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener.bind((self.address, self.port))

        while True:
            message = eval(listener.recv(4096))
            print('Received message from: ',
                  message['name'], message['message_type'])
            if(message['message_type'] == 'Request'):
                if(((message['processTime'] > self.requestedTime) and self.state == 'Wanted') or self.state == 'Held'):
                    self.waitingQueue.append(
                        (message['address'], message['port']))
                else:
                    print('Replying to ',
                          message['name'], 'it can access the CS')
                    responseMessage = {
                        'message_type': 'Reply', 'address': self.address, 'port': self.port, 'processTime': time.time(), 'name': self.name}
                    self.sendMessage(
                        (message['address'], message['port']), responseMessage)
            if(message['message_type'] == 'Reply'):
                self.replyQueue.remove(
                    (message['address'], message['port']))

    def sendMessage(self, address_and_port, message):
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sender.sendto(str(message).encode('utf8'), address_and_port)
        sender.close()

    def getMutex(self):
        print('process: ', self.name, 'want mutex')
        self.state = 'Wanted'
        self.requestedTime = time.time()
        message = {
            'message_type': 'Request',
            'address': self.address,
            'port': self.port,
            'processTime': self.requestedTime,
            'name': self.name,
        }

        for remoteAddress in self.remotes:
            self.sendMessage(remoteAddress, message)
            self.replyQueue.append(remoteAddress)

        while(len(self.replyQueue) > 0):
            pass

        self.state = 'Held'

        print('process: ', self.name, 'entered mutex')

        return True

    def releaseMutex(self):
        print('process: ', self.name, 'is releasing mutex')
        self.state = 'Released'
        message = {
            'message_type': 'Reply',
            'address': self.address,
            'port': self.port,
            'processTime': self.requestedTime,
            'name': self.name
        }
        aux_queue = []
        for replyAddress in self.waitingQueue:
            print('process: ', self.name,
                  'released mutex for port: ', replyAddress[1])
            self.sendMessage(replyAddress, message)
            aux_queue.append(replyAddress)
        for address in aux_queue:
            self.waitingQueue.remove(address)
