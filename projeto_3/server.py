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

fila1 = []
fila2 = []

is_resource_1_used = False
is_resource_2_used = False
client_on_resource_1 = ''
client_on_resource_2 = ''

# para fazer a liberacao automatica dos recursos apos um tempo t
start_time_1 = time.time()
start_time_2 = time.time()


def verifyResourceTime():
    # loop que irá liberar recursos em uso pelos processos caso passem do tempo limite
    global is_resource_1_used, is_resource_2_used, start_time_1, start_time_2, client_on_resource_1, client_on_resource_2, fila1, fila2
    while(1):

        if(is_resource_1_used == True):
            if((start_time_1+20) < time.time()):
                releaseToken(client_on_resource_1)
        if(is_resource_2_used == True):
            if((start_time_2+20) < time.time()):
                releaseToken(client_on_resource_2)
        time.sleep(0.1)


@app.route('/resource', methods=['POST'])
def post():
    requestParser = reqparse.RequestParser()

    requestParser.add_argument('name', required=True)
    requestParser.add_argument('resource', required=True)

    arguments = requestParser.parse_args()
    print(arguments)
    getToken(arguments['name'], int(arguments['resource']))

    # sucesso da request
    return 200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Headers': 'Access-Control-Allow-Origin: *'
    }


@app.route('/resource', methods=['PUT'])
def put():
    requestParser = reqparse.RequestParser()

    requestParser.add_argument('name', required=True)
    arguments = requestParser.parse_args()

    return releaseToken(
        arguments['name'])


def getToken(name, resource):
    global is_resource_1_used, is_resource_2_used, start_time_1, start_time_2, client_on_resource_1, client_on_resource_2, fila1, fila2
    # metodo que gerencia as filas de uso dos recursos
    # e aloca recursos para os processos que os requisitam

    print("cliente ", name, "requisitou o token")

    if(resource == 1):
        if(is_resource_1_used):
            print("recurso 1 em uso, adicionando na fila")
            fila1.append(name)
            return 200
        else:
            print("usando recurso 1")
            is_resource_1_used = True
            client_on_resource_1 = name
            notify_client('concedeu', name, "1")
            start_time_1 = time.time()
            return 200
    elif (resource == 2):
        if(is_resource_2_used):
            print("recurso 2 em uso, adicionando na fila")
            fila2.append(name)
            return 200
        else:
            print("usando recurso 2")
            is_resource_2_used = True
            client_on_resource_2 = name
            notify_client('concedeu', name, "2")
            start_time_2 = time.time()
            return 200


def releaseToken(name):
    global is_resource_1_used, is_resource_2_used, start_time_1, start_time_2, client_on_resource_1, client_on_resource_2, fila1, fila2
    # metodo para liberacao dos recursos usados pelos clients
    print("Cliente", name, "removeu o acesso")
    if(client_on_resource_1 == name):
        print("Liberando recurso 1")
        if(len(fila1) > 0):
            # se existiam processos na fila de uso do recurso 1, notifica o client
            new_client_name = fila1.pop(0)
            print("Recurso agora com cliente ", new_client_name)

            notify_client('liberou', client_on_resource_1, "1")
            notify_client('concedeu', new_client_name, "1")
            start_time_1 = time.time()
            client_on_resource_1 = new_client_name
            is_resource_1_used = True
            return 200
        else:
            # se nao ha nenhum client esperando, apenas reseta as variaveis
            notify_client('liberou', client_on_resource_1, "1")
            client_on_resource_1 = ''
            is_resource_1_used = False
            return 200
    elif(client_on_resource_2 == name):
        print("Liberando recurso 2")
        if(len(fila2) > 0):
            # se existiam processos na fila de uso do recurso 2, notifica o client
            new_client_name = fila2.pop(0)

            print("Recurso agora com cliente ", new_client_name)
            notify_client('liberou', client_on_resource_2, "2")
            notify_client('concedeu', new_client_name, "2")
            start_time_2 = time.time()
            client_on_resource_2 = new_client_name
            is_resource_2_used = True
            return 200
        else:
            # se nao ha nenhum client esperando, apenas reseta as variaveis
            notify_client('liberou', client_on_resource_2, "2")
            client_on_resource_2 = ''
            is_resource_2_used = False
            return 200


def notify_client(modo, nome, recurso):
    with app.app_context():
        sse.publish({"modo": modo, "nome": nome,
                    "recurso": recurso}, type='message')
        print("Evento publicado as ", datetime.now())
    return


if __name__ == '__main__':

    verifyTime = threading.Thread(target=verifyResourceTime)
    verifyTime.start()
    # inicializa o server
    app.run(host='0.0.0.0', port=8000)
