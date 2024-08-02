import socket
import threading
from queue import Queue

PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
FORMAT = "utf-8"
ADDR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen(5)

all_connections = []
all_address = []
NUMBER_OF_THREADS = 3
JOB_NUMBER = [1, 2, 3]
queue = Queue()


def accepting_connections():
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]

    while True:
        try:
            conn, address = server.accept()
            conn.setblocking(1)  # prevents timeout

            all_connections.append(conn)
            all_address.append(address)

            print("Connection has been established: " + address[0])

        except Exception as e:
            print("Error accepting connections:", str(e))


def handle_client(conn, addr):
    def read_data(conn, addr):
        print(f"[Reading from] {addr} device ")

        connected = True
        while connected:
            try:
                msg = conn.recv(2040).decode(FORMAT)
                if msg == 'Disconnected':
                    connected = False
                elif msg:
                    print(f"{addr}: {msg}")

            except Exception as e:
                print(f"Error reading data from {addr}: {str(e)}")
                connected = False

        conn.close()

    def write_data(data, conn):
        try:
            data = data.encode(FORMAT)
            conn.send(data)
        except Exception as e:
            print(f"Error sending data to {addr}: {str(e)}")

    read_thread = threading.Thread(target=read_data, args=(conn, addr))
    read_thread.start()

    # Example of writing data, can be replaced with actual logic
    write_thread = threading.Thread(target=write_data, args=("DONE", conn))
    write_thread.start()


def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


def work():
    while True:
        x = queue.get()
        if x == 1:
            accepting_connections()
        if x == 2:
            for conn in all_connections:
                handle_client(conn, all_address[all_connections.index(conn)])
        if x == 3:
            # Example: Sending data to all connected clients
            for conn in all_connections:
                handle_client(conn, all_address[all_connections.index(conn)])
        queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)

    queue.join()


create_workers()
create_jobs()
