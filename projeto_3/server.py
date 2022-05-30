from __future__ import print_function

import ast
import threading
import time
from datetime import datetime

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, json, render_template, request
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse
from flask_sse import sse

# configura server
app = Flask(__name__)
CORS(app)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')
api = Api(app)


class Server(Resource):
    def __init__(self):
        self.clients = {}
        # fila de acesso aos recursos 1 e 2
        self.fila1 = []
        self.fila2 = []

        # Gera public e private keys

        self.is_resource_1_used = False
        self.is_resource_2_used = False
        self.client_on_resource_1 = ''
        self.client_on_resource_2 = ''

        # para fazer a liberacao automatica dos recursos apos um tempo t
        self.start_time_1 = time.time()
        self.start_time_2 = time.time()

        verifyTime = threading.Thread(target=self.verifyResourceTime)
        verifyTime.start()

    def verifyResourceTime(self):
        # loop que irá liberar recursos em uso pelos processos caso passem do tempo limite
        while(1):
            if(self.is_resource_1_used == True):
                if((self.start_time_1+20) < time.time()):
                    self.releaseToken(self.client_on_resource_1)
            if(self.is_resource_2_used == True):
                if((self.start_time_2+20) < time.time()):
                    self.releaseToken(self.client_on_resource_2)
            time.sleep(0.1)

    def post(self):
        print('chegou')
        requestParser = reqparse.RequestParser()

        requestParser.add_argument('name', required=True)
        requestParser.add_argument('resource', required=True)

        arguments = requestParser.parse_args()

        print(arguments)

        self.getToken(arguments['name'], int(arguments['resource']))

        return 200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Headers': 'Access-Control-Allow-Origin: *'
        }

    def put(self):
        requestParser = reqparse.RequestParser()

        requestParser.add_argument('name', required=True)
        arguments = requestParser.parse_args()
        return self.releaseToken(
            arguments['name'])

    def getToken(self, name, resource):
        # metodo que gerencia as filas de uso dos recursos
        # e aloca recursos para os processos que os requisitam

        print("cliente ", name, "requisitou o token")

        if(resource == 1):
            if(self.is_resource_1_used):
                print("recurso 1 em uso, adicionando na fila")
                self.fila1.append(name)
                return 200
            else:
                print("usando recurso 1")
                self.is_resource_1_used = True
                self.client_on_resource_1 = name
                self.notify_client('concedeu', name)
                self.start_time_1 = time.time()
                return 200
        elif (resource == 2):
            if(self.is_resource_2_used):
                print("recurso 2 em uso, adicionando na fila")
                self.fila2.append(name)
                return 200
            else:
                print("usando recurso 2")
                self.is_resource_2_used = True
                self.client_on_resource_2 = name
                self.notify_client('concedeu', name)
                self.start_time_2 = time.time()
                return 200

    def releaseToken(self, name):
        # metodo para liberacao dos recursos usados pelos clients

        print("Cliente", name, "removeu o acesso")
        if(self.client_on_resource_1 == name):
            print("Liberando recurso 1")
            if(len(self.fila1) > 0):
                # se existiam processos na fila de uso do recurso 1, notifica o client
                new_client_name = self.fila1.pop(0)
                print("Recurso agora com cliente ", new_client_name)
                client = self.clients[new_client_name]
                self.notify_client('liberou', self.client_on_resource_1)
                self.notify_client('concedeu', new_client_name)
                self.start_time_1 = time.time()
                self.client_on_resource_1 = new_client_name
                self.is_resource_1_used = True
                return 200
            else:
                # se nao ha nenhum client esperando, apenas reseta as variaveis
                self.notify_client('liberou', self.client_on_resource_1)
                self.client_on_resource_1 = ''
                self.is_resource_1_used = False
                return 200
        elif(self.client_on_resource_2 == name):
            print("Liberando recurso 2")
            if(len(self.fila2) > 0):
                # se existiam processos na fila de uso do recurso 2, notifica o client
                new_client_name = self.fila2.pop(0)
                client = self.clients[new_client_name]
                print("Recurso agora com cliente ", new_client_name)
                self.notify_client('liberou', self.client_on_resource_2)
                self.notify_client('concedeu', new_client_name)
                self.start_time_2 = time.time()
                self.client_on_resource_2 = new_client_name
                self.is_resource_2_used = True
                return 200
            else:
                # se nao ha nenhum client esperando, apenas reseta as variaveis
                self.notify_client('liberou', self.client_on_resource_2)
                self.client_on_resource_2 = ''
                self.is_resource_2_used = False
                return 200

    def notify_client(self, modo, nome):
        with app.app_context():
            sse.publish({"modo": modo, "nome": nome}, type='message')
            print("Evento publicado as ", datetime.now())
        return


api.add_resource(Server, '/resource')

if __name__ == '__main__':
    # inicializa o server
    app.run(host='0.0.0.0', port=8000)
