import time

from main import process

process_a = process('127.0.0.1', 3000, 'process_a')
# process_a.set_remote('127.0.0.1', 3001) setando b
# process_a.set_remote('127.0.0.1', 3002) setando c
# time.sleep(3)
# process_a.getMutex() //entrando sc
# time.sleep(5)
# process_a.releaseMutex() saindo SC
# time.sleep(3)
