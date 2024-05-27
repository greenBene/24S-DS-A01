import socket
import time
import threading
import logging

HOST='server'
PORT=5050


ROUND_DURATION_IN_SECONDS=5
ROUND_COUNT=3

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

        round=0
        while round < ROUND_COUNT:
            start_voting()
            time.sleep(ROUND_DURATION_IN_SECONDS)

            end_voting()
            
            determine_winner()
            time.sleep(1)
            
            round+=1
        
        close_connections()
        server.close()
        logging.info("End of programm")


def accept_new_connections(server:socket.socket):
    while True:
        try:
            (conn, add) = server.accept()
        except Exception:
            logging.info(f"Exception in accepting connection")
            break
        logging.info(f"Incomming connection from {add}")
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

def close_connections():
    global active
    active=False
    for (conn, _) in connections:
        conn.sendall(b"CLOSE")
        conn.close()

if __name__ == '__main__':
    main()