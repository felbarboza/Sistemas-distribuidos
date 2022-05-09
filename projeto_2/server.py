import Pyro4
from Crypto import Random
from Crypto.Hash import SHA384
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Pyro4.core import Daemon


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Server(object):
    def __init__(self):
        self.clients = {}
        self.fila1 = []
        self.fila2 = []
        random_seed = Random.new().read
        self.private_key = RSA.generate(1024, random_seed)
        self.public_key = self.private_key.publickey()
        self.is_resource_1_used = False
        self.is_resource_2_used = False
        self.client_on_resource_1 = ''
        self.client_on_resource_2 = ''
        self.signature = pkcs1_15.new(self.private_key)
        random_seed = Random.new().read
        self.token = RSA.generate(1024, random_seed)

    def getToken(self, name, client):
        if(self.is_resource_1_used and self.is_resource_2_used):
            if(len(self.fila1) > len(self.fila2)):
                self.fila2.append(name)
            else:
                self.fila1.append(name)
        elif(self.is_resource_1_used):
            self.is_resource_2_used = True
            self.client_on_resource_1 = name
            client.notify(self.token, self.signature)
        else:
            self.is_resource_1_used = True
            self.client_on_resource_2 = name
            client.notify(self.token, self.signature)

        if name not in self.clients.keys():
            self.clients[name] = client
            return self.public_key

    def releaseToken(self, name):
        if(self.client_on_resource_1 == name):
            if(len(self.fila1) > 0):
                client = self.clients[self.fila1.pop(0)]
                client.notify(self.token, self.signature)
                self.client_on_resource_1 = name
                self.is_resource_1_used = True
            else:
                self.client_on_resource_1 = ''
                self.is_resource_1_used = False
        elif(self.client_on_resource_2 == name):
            if(len(self.fila2) > 0):
                client = self.clients[self.fila2.pop(0)]
                client.notify(self.token, self.signature)
                self.client_on_resource_2 = name
                self.is_resource_2_used = True
            else:
                self.client_on_resource_2 = ''
                self.is_resource_2_used = False

            return


Pyro4.Deamon.serverSimple({Server: "CentralServer"}, ns=True)
ns = Pyro4.locateNS()
uri = Deamon.register()
