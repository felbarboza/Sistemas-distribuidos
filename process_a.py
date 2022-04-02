import time

from main import process

process_a = process('127.0.0.1', 3000, 'process_a')
process_a.set_remote('127.0.0.1', 3001)
process_a.set_remote('127.0.0.1', 3002)
time.sleep(3)
process_a.getMutex()
time.sleep(5)
process_a.releaseMutex()
time.sleep(3)
