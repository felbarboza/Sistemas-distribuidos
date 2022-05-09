import sys
import threading
import time
import tkinter as tk
from base64 import b64decode, b64encode

import Pyro4
import Pyro4.util
from Crypto import Random
from Crypto.Hash import SHA384
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

# faz aparecer as msg de erro do servidor
sys.excepthook = Pyro4.util.excepthook


window = tk.Tk()

address_a_label = tk.Label(text="Cliente")
entry_a_address = tk.Entry()
address_a_label.grid(column=0, row=0)
entry_a_address.grid(column=0, row=1)


class cliente_callback(object):
    def __init__(self, name):
        self.server = Pyro4.core.Proxy("PYRONAME:example.CentralServer")
        self.name = name
        self.server_public_key = ''
        self.abort = 0
        loop = threading.Thread(target=self.loop)
        loop.start()

    @Pyro4.expose
    def setPublicKey(self, public_key):
        #  armazena a chave publica do servidor que sera usada para
        #  verificar a assinatura
        self.server_public_key = b64decode(public_key['data'])

    @Pyro4.expose
    def notify(self, signed_token, token):
        print(signed_token, token)
        # metodo chamado pelo getToken do servidor quando um processo libera um recurso
        print("callback recebido do servidor!")

        signed_token = b64decode(signed_token['data'])
        token = SHA384.new(bytes(token, encoding='utf-8'))

        # verificacao da assinatura digital do servidor
        try:
            pkcs1_15.new(RSA.importKey(self.server_public_key)
                         ).verify(token, signed_token)
            print("assinatura digital valida")
        except:
            print("assinatura digital invalida")

    def loopThread(self, daemon):
        daemon.requestLoop()

    def getToken(self):
        # recupera o token
        name = self.name
        self.server.getToken(name, self)

    def loop(self):
        while(1):
            time.sleep(0.1)

    @Pyro4.expose
    def releaseToken(self):
        # libera o processo (concessao do Token)
        self.server.releaseToken(self.name)

    def setName(self):
        # grava o nome do client
        self.name = entry_a_address.get()


class DaemonThread(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client
        self.setDaemon(True)

    def run(self):
        with Pyro4.core.Daemon() as daemon:
            daemon.register(self.client)
            daemon.requestLoop(lambda: not self.client.abort)


s = cliente_callback(' ')
daemonthread = DaemonThread(s)
daemonthread.start()


button = tk.Button(
    text="Setar nome",
    command=s.setName
).grid(column=0, row=2)

button = tk.Button(
    text="Entrar na SC",
    command=s.getToken
).grid(column=0, row=3)


button = tk.Button(
    text="Sair da SC",
    command=s.releaseToken
).grid(column=0, row=4)

window.mainloop()
