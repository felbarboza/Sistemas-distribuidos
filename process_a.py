import threading
import tkinter as tk

from main import process


process_a = process('127.0.0.1', 4444, 'process_a')

process_a.set_remote('127.0.0.1', 4445)
process_a.set_remote('127.0.0.1', 4446)
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

def entry_a_SC():
    process_a_thread = threading.Thread(target=process_a.getMutex)
    process_a_thread.start()


def exit_a_SC():
    process_a.releaseMutex()


button = tk.Button(
    text="Entrar na SC - A",
    command=entry_a_SC
).grid(column=0, row=6)

button = tk.Button(
    text="Sair da SC - A",
    command=exit_a_SC
).grid(column=1, row=6)

# set_remotes()
window.mainloop()
