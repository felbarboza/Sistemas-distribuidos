import threading

import Pyro4
import Pyro4.util
from Crypto import Random
from Crypto.Hash import SHA384
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


@Pyro4.expose
@Pyro4.callback
class cliente_callback(object):
    def __init__(self, name):
        self.server = Pyro4.core.Proxy("PYRONAME:CentralServer")
        self.name = name
        self.server_public_key = ''

        return

    def notify(self, token, assinatura):

        print("callback recebido do servidor!")

    def loopThread(daemon):
        daemon.requestLoop()

    def getToken(self):
        self.server_public_key = self.server.getToken(self.name, self)


def main():

    ns = Pyro4.locateNS()
    uri = ns.lookup("CentralServer")
    servidor = Pyro4.Proxy(uri)
    # ... servidor.metodo() —> invoca método no servidor
    daemon = Pyro4.core.Daemon()
    callback = cliente_callback()
    daemon.register(callback)
    thread = threading.Thread(target=callback.loopThread, args=(daemon, ))
    thread.daemon = True
    thread.start()


main()
