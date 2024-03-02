import socket
import threading
from multiprocessing import Value

def handle_client(client_socket, address, clients, client_id_counter, client_connections):
    with client_id_counter.get_lock():
        client_id = client_id_counter.value
        client_id_counter.value += 1

    print(f"[*] Client {client_id} connected from {address[0]}:{address[1]}")

    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break

        if data.startswith("ConnectRequest:"):
            try:
                peer_id = int(data.split(":")[1])
                if peer_id in client_connections and client_connections[peer_id] is None:
                    print(f"[*] Client {client_id} sent a connection request to Client {peer_id}")
                    clients[peer_id - 1].send(f"ConnectionRequest:{client_id}".encode('utf-8'))
                else:
                    print(f"[*] Invalid connection request from Client {client_id} to Client {peer_id}")
                    client_socket.send("INVALID_CONNECTION_REQUEST".encode('utf-8'))
            except (IndexError, ValueError):
                print(f"[*] Invalid connection request from Client {client_id}")
                client_socket.send("INVALID_CONNECTION_REQUEST".encode('utf-8'))
        elif data.startswith("ConnectResponse:"):
            try:
                response = data.split(":")[1]
                peer_id = int(data.split(":")[2])
                if response == 'y':
                    client_connections[client_id] = peer_id
                    print(f"[*] Client {client_id} accepted the connection request from Client {peer_id}")
                    client_socket.send(f"CONNECT:{peer_id}".encode('utf-8'))
                    clients[peer_id - 1].send(f"CONNECT:{client_id}".encode('utf-8'))
                elif response == 'n':
                    print(f"[*] Client {client_id} declined the connection request from Client {peer_id}")
                    client_socket.send("Connection declined.".encode('utf-8'))
            except (IndexError, ValueError):
                print(f"[*] Invalid connection response from Client {client_id}")
                client_socket.send("INVALID_CONNECTION_RESPONSE".encode('utf-8'))
        else:
            print(f"Received message from Client {client_id}: {data}")

            # Broadcast the message to all connected clients except the sender
            for client in clients:
                if client != client_socket:
                    try:
                        client.send(f"Client {client_id}: {data}".encode('utf-8'))
                    except socket.error:
                        # Remove broken connections
                        clients.remove(client)

    print(f"[*] Client {client_id} disconnected")
    client_socket.close()
    if client_id in client_connections:
        del client_connections[client_id]

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5555))
    server.listen(2)
    print("[*] Server listening on 127.0.0.1:5555")

    clients = []
    client_id_counter = Value('i', 1)
    client_connections = {}

    while True:
        client, addr = server.accept()
        print(f"[*] Assigned Client ID {client_id_counter.value} to {addr[0]}:{addr[1]}")
        client.send(f"Your ID is {client_id_counter.value}".encode('utf-8'))

        clients.append(client)
        client_handler = threading.Thread(target=handle_client, args=(client, addr, clients, client_id_counter, client_connections))
        client_handler.start()

if __name__ == "__main__":
    start_server()
