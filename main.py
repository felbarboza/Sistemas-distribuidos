import json
import socket
from socket import *
import sys
import struct
import threading
import time
from copyreg import constructor


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
        self.multicastIp = '224.1.1.1'
        self.multicastPort = 4444
        self.sending_sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        ttl = struct.pack('b', 32)
        self.sending_sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)

        self.listening_sock = socket(AF_INET, SOCK_DGRAM)
        self.listening_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listening_sock.bind(("", self.multicastPort ))
        group = inet_aton(self.multicastIp)
        mreq = struct.pack('4sL', group, INADDR_ANY)
        self.listening_sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

        self.listenThread = threading.Thread(target=self.listen_messages_multicast)
        self.listenThread.start()
        
        self.listenThread2 = threading.Thread(target=self.listen_messages_unicast)
        self.listenThread2.start()

    def set_address(self, address):
        self.address = address

    def set_port(self, port):
        self.port = port

    def set_remote(self, remoteAddress, remotePort):
        self.remotes.append((remoteAddress, remotePort))

    def listen_messages_multicast(self):
        while True:
            message = eval(self.listening_sock.recv(4096))
            if(message['port']==self.port):
                continue
            print('process ', self.name, ' Received message from: ',
                  message['name'], message['message_type'])
            if(message['message_type'] == 'Request'):
                if(((message['processTime'] > self.requestedTime) and self.state == 'Wanted') or self.state == 'Held'):
                    self.waitingQueue.append(
                        (message['address'], message['port']))
                else:
                    print('process ', self.name, ' Replying to ',
                          message['name'], 'it can access the CS')
                    responseMessage = {
                        'message_type': 'Reply', 'address': self.address, 'port': self.port, 'processTime': time.time(), 'name': self.name}
                    self.sendMessageUnicast(
                        (message['address'], message['port']), responseMessage)
            if(message['message_type'] == 'Reply'):
                self.replyQueue.remove(
                    (message['address'], message['port']))

    def listen_messages_unicast(self):
        listener = socket(AF_INET, SOCK_DGRAM)
        listener.bind((self.address, self.port))

        while True:
            message = eval(listener.recv(4096))
            if(message['port']==self.port):
                continue
            print('process ', self.name, ' Received message from: ',
                  message['name'], message['message_type'])
            if(message['message_type'] == 'Request'):
                if(((message['processTime'] > self.requestedTime) and self.state == 'Wanted') or self.state == 'Held'):
                    self.waitingQueue.append(
                        (message['address'], message['port']))
                else:
                    print('process ', self.name, ' Replying to ',
                          message['name'], 'it can access the CS')
                    responseMessage = {
                        'message_type': 'Reply', 'address': self.address, 'port': self.port, 'processTime': time.time(), 'name': self.name}
                    self.sendMessageUnicast(
                        (message['address'], message['port']), responseMessage)
            if(message['message_type'] == 'Reply'):
                self.replyQueue.remove(
                    (message['address'], message['port']))


    def sendMessage(self, message):
        self.sending_sock.sendto(str(message).encode('utf8'), (self.multicastIp, self.multicastPort))

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
        self.sendMessage(message)

        for remoteAddress in self.remotes:
            self.replyQueue.append(remoteAddress)

        while(len(self.replyQueue) > 0):
            pass

        self.state = 'Held'

        print('process: ', self.name, 'entered mutex')

        return True

    def sendMessageUnicast(self, address_and_port, message):
        sender = socket(AF_INET, SOCK_DGRAM)
        sender.sendto(str(message).encode('utf8'), address_and_port)
        sender.close()

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
            self.sendMessageUnicast(replyAddress, message)
            aux_queue.append(replyAddress)
        for address in aux_queue:
            self.waitingQueue.remove(address)
