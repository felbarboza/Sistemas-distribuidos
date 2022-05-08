# -*- coding: utf-8 -*-
import threading
import tkinter as tk

from main import process

window = tk.Tk()

# Processo A
address_a = '127.0.0.1'
port_a = 3000
address_a_label = tk.Label(text="Endereço A")
entry_a_address = tk.Label(text=address_a)
address_a_label.grid(column=0, row=0)
entry_a_address.grid(column=0, row=1)

port_a_label = tk.Label(text="Porta A")
entry_a_port = tk.Label(text=port_a)
port_a_label.grid(column=1, row=0)
entry_a_port.grid(column=1, row=1)

# Processo B
address_b = '127.0.0.1'
port_b = 3001
address_b_label = tk.Label(text="Endereço B")
entry_b_address = tk.Label(text=address_b)
address_b_label.grid(column=0, row=2)
entry_b_address.grid(column=0, row=3)

port_b_label = tk.Label(text="Porta B")
entry_b_port = tk.Label(text=port_b)
port_b_label.grid(column=1, row=2)
entry_b_port.grid(column=1, row=3)

# Processo C
address_c = '127.0.0.1'
port_c = 3002
address_c_label = tk.Label(text="Endereço C")
entry_c_address = tk.Label(text=address_c)
address_c_label.grid(column=0, row=4)
entry_c_address.grid(column=0, row=5)

port_c_label = tk.Label(text="Porta C")
entry_c_port = tk.Label(text=port_c)
port_c_label.grid(column=1, row=4)
entry_c_port.grid(column=1, row=5)

# Processos
process_a = process('127.0.0.1', 3000, 'process_a')
process_b = process('127.0.0.1', 3001, 'process_b')
process_c = process('127.0.0.1', 3002, 'process_c')

# Metodos


def set_a_values():
    global address_a
    address_a = entry_a_address.get()
    global port_a
    port_a = int(entry_a_port.get())
    process_a.set_address(address_a)
    process_a.set_port(port_a)


def set_b_values():
    global address_b
    address_b = entry_b_address.get()
    global port_b
    port_b = int(entry_b_port.get())
    process_b.set_address(address_b)
    process_b.set_port(port_b)


def set_c_values():
    global address_c
    address_c = entry_a_address.get()
    global port_c
    port_c = int(entry_a_port.get())
    process_c.set_address(address_c)
    process_c.set_port(port_c)


def set_remotes():
    process_a.set_remote(address_b, port_b)
    process_a.set_remote(address_c, port_c)

    process_b.set_remote(address_a, port_a)
    process_b.set_remote(address_c, port_c)

    process_c.set_remote(address_a, port_a)
    process_c.set_remote(address_b, port_b)


def entry_a_SC():
    process_a_thread = threading.Thread(target=process_a.getMutex)
    process_a_thread.start()


def exit_a_SC():
    process_a.releaseMutex()


def entry_b_SC():
    process_b_thread = threading.Thread(target=process_b.getMutex)
    process_b_thread.start()


def exit_b_SC():
    process_b.releaseMutex()


def entry_c_SC():
    process_c_thread = threading.Thread(target=process_c.getMutex)
    process_c_thread.start()


def exit_c_SC():
    process_c.releaseMutex()


button = tk.Button(
    text="Entrar na SC - A",
    command=entry_a_SC
).grid(column=0, row=6)

button = tk.Button(
    text="Sair da SC - A",
    command=exit_a_SC
).grid(column=1, row=6)

button = tk.Button(
    text="Entrar na SC - B",
    command=entry_b_SC
).grid(column=0, row=7)

button = tk.Button(
    text="Sair da SC - B",
    command=exit_b_SC
).grid(column=1, row=7)

button = tk.Button(
    text="Entrar na SC - C",
    command=entry_c_SC
).grid(column=0, row=8)

button = tk.Button(
    text="Sair da SC - C",
    command=exit_c_SC
).grid(column=1, row=8)


logs = 'Logs'
logs_label = tk.Label(text=logs)
logs_label.grid(column=0, row=9)


def print_logs(self, new_log):
    global logs
    global logs_label
    logs = logs + '\n' + new_log
    logs_label.config(text=logs)


set_remotes()
window.mainloop()