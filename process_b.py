import time

from main import process

process_b = process('127.0.0.1', 3001, 'process_b')
# process_b.set_remote('127.0.0.1', 3000)
# process_b.set_remote('127.0.0.1', 3002)
# time.sleep(3)
# process_b.getMutex()
# time.sleep(5)
# process_b.releaseMutex()
# time.sleep(3)
