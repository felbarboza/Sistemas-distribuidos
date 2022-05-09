import threading
import time

import Pyro4
from Crypto import Random
from Crypto.Hash import SHA384
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Pyro4.core import Daemon


@Pyro4.behavior(instance_mode="single")
@Pyro4.expose
class Server():
    def __init__(self):
        self.clients = {}
        self.fila1 = []
        self.fila2 = []

        # Gera public e private keys
        random_seed = Random.new().read
        self.private_key = RSA.generate(1024, random_seed)
        self.public_key = self.private_key.publickey()

        self.is_resource_1_used = False
        self.is_resource_2_used = False
        self.client_on_resource_1 = ''
        self.client_on_resource_2 = ''

        self.start_time_1 = time.time()
        self.start_time_2 = time.time()

        self.signature = pkcs1_15.new(self.private_key)
        self.decrypted_token = '123456'
        self.signed_token = SHA384.new(
            bytes(self.decrypted_token, encoding='utf-8'))
        self.signed_token = self.signature.sign(self.signed_token)
        print(self.decrypted_token, self.signed_token)
        verifyTime = threading.Thread(target=self.verifyResourceTime)
        verifyTime.start()

    def verifyResourceTime(self):
        while(1):
            if(self.is_resource_1_used == True):
                if((self.start_time_1+10) < time.time()):
                    self.clients[self.client_on_resource_1].releaseToken()
            if(self.is_resource_2_used == True):
                if((self.start_time_2+10) < time.time()):
                    self.clients[self.client_on_resource_2].releaseToken()
            time.sleep(0.1)

    @Pyro4.expose
    def getToken(self, name, client):
        print("cliente ", name, "requisitou o token")
        first_time = False
        if name not in self.clients.keys():
            print("primeira vez de acesso, retornando public key")
            # retorna a chave publica apenas no primeiro
            # pedido de acesso a recurso
            self.clients[name] = client
            client.setPublicKey(self.public_key.exportKey())
        if(self.is_resource_1_used and self.is_resource_2_used):
            if(len(self.fila1) > len(self.fila2)):
                print("os dois recursos estão em uso, adicionando na fila 2")
                self.fila2.append(name)
            else:
                print("os dois recursos estão em uso, adicionando na fila 1")
                self.fila1.append(name)
        elif(self.is_resource_1_used):
            print("usando recurso 2")
            self.is_resource_2_used = True
            self.client_on_resource_2 = name
            client.notify(self.signed_token, self.decrypted_token)
            self.start_time_2 = time.time()
        else:
            print("usando recurso 1")
            self.is_resource_1_used = True
            self.client_on_resource_1 = name
            client.notify(self.signed_token, self.decrypted_token)
            self.start_time_1 = time.time()

    @Pyro4.expose
    def releaseToken(self, name):
        print("Cliente", name, "removeu o acesso")
        if(self.client_on_resource_1 == name):
            print("Liberando recurso 1")
            if(len(self.fila1) > 0):
                new_client_name = self.fila1.pop(0)
                print("Recusto agora com cliente ", new_client_name)
                client = self.clients[new_client_name]
                client.notify(self.signed_token, self.decrypted_token)
                self.start_time_1 = time.time()
                self.client_on_resource_1 = name
                self.is_resource_1_used = True
            else:
                self.client_on_resource_1 = ''
                self.is_resource_1_used = False
        elif(self.client_on_resource_2 == name):
            print("Liberando recurso 2")
            if(len(self.fila2) > 0):
                new_client_name = self.fila2.pop(0)
                client = self.clients[new_client_name]
                print("Recusto agora com cliente ", new_client_name)
                client.notify(self.signed_token, self.decrypted_token)
                self.start_time_2 = time.time()
                self.client_on_resource_2 = name
                self.is_resource_2_used = True
            else:
                self.client_on_resource_2 = ''
                self.is_resource_2_used = False
            return


Pyro4.Daemon.serveSimple({Server: "example.CentralServer"}, ns=True)
ns = Pyro4.locateNS()
uri = Daemon.register()
