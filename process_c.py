import time

from main import process

process_c = process('127.0.0.1', 3002, 'process_c')
process_c.set_remote('127.0.0.1', 3000)
process_c.set_remote('127.0.0.1', 3001)
time.sleep(9)
process_c.getMutex()
time.sleep(5)
process_c.releaseMutex()
time.sleep(3)
