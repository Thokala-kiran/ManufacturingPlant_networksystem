import socket
import threading
from queue import Queue

# Server configuration
PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
FORMAT = "utf-8"
ADDR = (HOST, PORT)

# Initialize server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen(5)  # Server listens for incoming connections

# Lists to keep track of all active connections and their addresses
all_connections = []
all_address = []

# Thread and job configurations
NUMBER_OF_THREADS = 3
JOB_NUMBER = [1, 2, 3]
queue = Queue()

# Function to accept incoming connections
def accepting_connections():
    # Close existing connections and clear the lists
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_address[:]

    while True:
        try:
            conn, address = server.accept()  # Accept new connection
            conn.setblocking(1)  # Prevents timeout
            all_connections.append(conn)  # Add connection to the list
            all_address.append(address)  # Add address to the list
            print("Connection has been established: " + address[0])
        except Exception as e:
            print("Error accepting connections:", str(e))

# Function to handle a client connection
def handle_client(conn, addr):
    # Function to read data from the client
    def read_data(conn, addr):
        print(f"[Reading from] {addr} device ")
        connected = True
        while connected:
            try:
                msg = conn.recv(2040).decode(FORMAT)  # Receive message from client
                if msg == 'Disconnected':
                    connected = False  # Disconnect if client sends 'Disconnected'
                elif msg:
                    print(f"{addr}: {msg}")  # Print the received message
            except Exception as e:
                print(f"Error reading data from {addr}: {str(e)}")
                connected = False
        conn.close()  # Close connection when done

    # Function to write data to the client
    def write_data(data, conn):
        try:
            data = data.encode(FORMAT)  # Encode the data
            conn.send(data)  # Send the data to the client
        except Exception as e:
            print(f"Error sending data to {addr}: {str(e)}")

    # Start threads for reading and writing data
    read_thread = threading.Thread(target=read_data, args=(conn, addr))
    read_thread.start()

    
    write_thread = threading.Thread(target=write_data, args=("DONE", conn))
    write_thread.start()

# Function to create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

# Function to define the work done by each thread
def work():
    while True:
        x = queue.get()
        if x == 1:
            accepting_connections()  # Accept connections if job number is 1
        if x == 2:
            for conn in all_connections:
                handle_client(conn, all_address[all_connections.index(conn)])  # Read data from clients if job number is 2
        if x == 3:
            # Example: Sending data to all connected clients
            for conn in all_connections:
                handle_client(conn, all_address[all_connections.index(conn)])  # Write data to clients if job number is 3
        queue.task_done()

# Function to create jobs and add them to the queue
def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)  # Add job to the queue
    queue.join()  # Wait until all tasks in the queue have been processed

# Start worker threads and create jobs
create_workers()
create_jobs()
