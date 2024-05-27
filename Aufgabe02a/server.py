import socket
import time
import threading
import logging

HOST='server'
PORT=5050


DAUER_DER_RUNDE=5


connections = set()
results = dict()
results_lock = threading.Lock()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s server %(levelname)s: %(message)s')

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(100)
        accepting = threading.Thread(target=accept_new_connections, args=(server,))
        accepting.start()

        while True:
            start_voting()
            time.sleep(DAUER_DER_RUNDE)

            end_voting()
            
            determine_winner()
            time.sleep(1)


def accept_new_connections(server:socket.socket):
    while True:
        (conn, add) = server.accept()
        threading.Thread(target=incomming_message_handler, args=(conn, )).start()
        connections.add((conn,add))


def incomming_message_handler(conn: socket.socket):
    while True:
        data = conn.recv(1024)
        res = data.decode().split(' ')

        # INIT [CLIENT]
        if(res[0] == 'INIT'):
            logging.info(f'INIT message from {res[1]}')
        
        # WURF [CLIENT] [RESULT]
        if(res[0] == 'WURF'):
            logging.info(f'Received WURF from {res[1]} with value {res[2]}')
            results_lock.acquire()
            results[res[1]] = int(res[2])
            results_lock.release()
            

def start_voting():
    logging.info(f'Sending START ({len(connections)} clients)')
    results.clear()
    for (conn, _) in connections:
        conn.sendall(b'START')


def end_voting():
    logging.info('Sending STOP')
    for (conn, _) in connections:
        conn.sendall(b'STOP')


def determine_winner():
    results_lock.acquire()
    if(len(results)>0):
        key = max(results, key = lambda x:results[x])
        logging.info(f'Client \'{key}\' won with the value {results[key]}')
    else:
        logging.info('No votes received')
    results_lock.release()

if __name__ == '__main__':
    main()