import socket
import coolname
import time
import random
import logging

from clock import VectorClock

HOST='server'
PORT=5050

NUMBER_OF_CLIENTS=3

PLAYER_LATENCY_IN_SECONDS=10

name = coolname.generate_slug(2)
local_id: int
vector_clock: VectorClock

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s ' + name + ' %(levelname)s: %(message)s')


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))

    while True:
        data = client.recv(1024)
        if not data:
            break
        command = data.decode()
        res = command.split(' ')

        if res[0] == 'INIT':
            logging.info(f"Received INIT commat at {res[2]}. This client is assinged number {res[1]}.")
            local_id = int(res[1])
            vector_clock = VectorClock(NUMBER_OF_CLIENTS + 1, local_id)
            vector_clock.tick()
            vector_clock.update(res[2])


        if res[0] == 'START':
            logging.info(f'Received START command at {res[1]}.')
            vector_clock.tick()
            vector_clock.update(res[1])

            wait = random.random() * PLAYER_LATENCY_IN_SECONDS
            wurf = random.randint(1, 100)
            logging.info(f'Waiting {wait}s to send result {wurf}.')
            time.sleep(wait)
            logging.info(f'Sending result {wurf}')
            vector_clock.tick()
            client.sendall(f'WURF {name} {wurf} {vector_clock.serialize()}'.encode())

        
        if res[0] == 'CLOSE':
            logging.info("Received CLOSE command")
            break