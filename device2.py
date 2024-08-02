import socket

# Configuration
HOST = socket.gethostbyname(socket.gethostname())  # Get the local host IP
PORT = 9999  # Port number must be an integer
FORMAT = 'utf-8'

# Initialize client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client.connect((HOST, PORT))

def send(msg):
    # Encode the message and send it to the server
    client.send(msg.encode(FORMAT))
    # Receive the server's response and decode it
    print(client.recv(2048).decode(FORMAT))

# Sending messages to the server
send("Hello")
send("I am Device 2")
send("Here is the required data for the next process")
send("data")
send("Disconnected")

# Close the client connection
client.close()
