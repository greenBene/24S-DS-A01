import socket
import time
import threading
import logging
from clock import VectorClock

HOST='server'
PORT=5050

ROUND_DURATION_IN_SECONDS=5
NUMBER_OF_CLIENTS=3
ROUND_COUNT=5

latest_id=1
id_lock = threading.Lock()
vector_clock = VectorClock(NUMBER_OF_CLIENTS + 1, 0)

connections = set()
results = dict()
results_lock = threading.Lock()

last_start_time = list()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s server %(levelname)s: %(message)s')

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        vector_clock.tick()
        server.bind((HOST, PORT))
        server.listen(100)
        accepting = threading.Thread(target=accept_new_connections, args=(server,))
        accepting.start()

        time.sleep(ROUND_DURATION_IN_SECONDS)
        counter=0
        while counter<ROUND_COUNT:
            start_voting()
            time.sleep(ROUND_DURATION_IN_SECONDS)

            end_voting()
            
            determine_winner()
            time.sleep(1)
            counter+=1


def accept_new_connections(server:socket.socket):
    global latest_id
    while latest_id <= NUMBER_OF_CLIENTS:
        try:
            (conn, add) = server.accept()
        except Exception:
            logging.info(f"Exception in accepting connection")
            break
        logging.info(f"Incomming connection from {add}")

        with id_lock:
            vector_clock.tick()
            conn.sendall(f"INIT {latest_id} {vector_clock.serialize()}".encode())
            latest_id = latest_id+1
        threading.Thread(target=incomming_message_handler, args=(conn, add, )).start()
        connections.add((conn,add))
    logging.info("Stop accepting new connections")


def incomming_message_handler(conn: socket.socket, add):
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                logging.info(f'received EOF from {add}')
                break
        except Exception:
            logging.info(f'Error in connection {add}')
            break
        res = data.decode().split(' ')
        
        # WURF [CLIENT] [RESULT] [CLOCK]
        if(res[0] == 'WURF'):
            logging.info(f'Received WURF from {res[1]} with value {res[2]} at {res[3]}')
            with results_lock:
                if vector_clock.before(res[3]):
                    logging.info(f'Accepted WURF from {res[1]} because it depends on last start time {last_start_time[-1]}')
                    vector_clock.tick()
                    vector_clock.update(res[3])
                    results[res[1]] = int(res[2])
                else:
                    logging.info(f'Reject WURF from {res[1]} because it doe not depend on last start time {last_start_time[-1]}')
            

def start_voting():
    logging.info(f'Sending START ({len(connections)} clients)')
    vector_clock.tick()
    with results_lock:
        last_start_time.clear()
        last_start_time.append(vector_clock.local_time)
        results.clear()
    for (conn, _) in connections:
        conn.sendall(f'START {vector_clock.serialize()}'.encode())


def end_voting():
    logging.info('Sending STOP')
    vector_clock.tick()
    for (conn, _) in connections:
        conn.sendall(f'STOP {vector_clock.serialize()}'.encode())


def determine_winner():
    results_lock.acquire()
    vector_clock.tick()
    if(len(results)>0):
        key = max(results, key = lambda x:results[x])
        logging.info(f'Client \'{key}\' won with the value {results[key]}')
    else:
        logging.info('No votes received')
    results_lock.release()

if __name__ == '__main__':
    main()