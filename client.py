import socket
import threading

def receive_messages(client_socket):
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if data.startswith("CONNECT:"):
            print(f"[*] Connection established with Client {data.split(':')[1]}")
            start_chat(client_socket)
            break
        elif data == "INVALID_CONNECTION_REQUEST":
            print("[*] Invalid connection request. Please try again.")
            break
        elif data.startswith("ConnectionRequest:"):
            response = input(f"{data} Accept? (y/n): ")
            if response.lower() == 'y':
                client_socket.send(f"ConnectResponse:y:{data.split()[1]}".encode('utf-8'))
                print("[*] Sent connection response to accept to Server")
            else:
                client_socket.send(f"ConnectResponse:n:{data.split()[1]}".encode('utf-8'))
                print("[*] Sent connection response to decline to Server")
        else:
            print(data)

def start_chat(client_socket):
    while True:
        message = input("Enter a message (or 'exit' to quit): ")
        if message.lower() == 'exit':
            client_socket.close()
            break
        client_socket.send(message.encode('utf-8'))

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 5555))

    client_id = int(client.recv(1024).decode('utf-8').split()[3])
    print(f"[*] Your assigned ID is: {client_id}")

    while True:
        command = input("Enter a command (e.g., 'connect <id>', 'exit'): ")
        if command.lower() == 'exit':
            break
        elif command.startswith('connect'):
            try:
                peer_id = int(command.split()[1])
                client.send(f"ConnectRequest:{peer_id}".encode('utf-8'))
                print("[*] Sent connection request to Server")
            except (IndexError, ValueError):
                print("[*] Invalid command. Usage: 'connect <id>'")
        else:
            print("[*] Invalid command. Please try again.")

    client.close()

if __name__ == "__main__":
    start_client()
