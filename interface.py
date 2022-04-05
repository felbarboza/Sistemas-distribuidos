import tkinter as tk
from main import process

window = tk.Tk()


processALabel = tk.Label(
    text="Processo A",
    foreground="white",  # Set the text color to white
    background="purple",  
    width=10,
    height=5
).pack()

address_a_label = tk.Label(text="Endereço A")
entry_a = tk.Entry()

address_a_label.pack()
entry_a.pack()

process_a = process('', 0, 'process_a')

def entry_a_SC():
    address_a = entry_a.get()
    print(address_a)
    process_a.set_address(address_a)
    print(process_a.address)


button = tk.Button(
    text="Entrar na SC",
    command=entry_a_SC
).pack()


window.mainloop()