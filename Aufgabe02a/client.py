import socket
import coolname
import time
import random
import logging

HOST='server'
PORT=5050

PLAYER_LATENCY_IN_SECONDS=10

name = coolname.generate_slug(2)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s ' + name + ' %(levelname)s: %(message)s')


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))
    client.sendall(f'INIT {name} {time.time()}'.encode())

    while True:
        data = client.recv(1024)
        if not data:
            break
        command = data.decode()
        res = command.split(' ')

        if res[0] == 'START':
            logging.info('Received START command')
            wait = random.random() * PLAYER_LATENCY_IN_SECONDS
            wurf = random.randint(1, 100)
            logging.info(f'Waiting {wait}s to send result {wurf}')
            time.sleep(wait)
            logging.info(f'Sending result {wurf}')
            client.sendall(f'WURF {name} {wurf}'.encode())
        if res[0] == 'CLOSE':
            logging.info("Received CLOSE command")
            break