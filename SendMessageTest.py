from socket import socket, AF_INET, SOCK_STREAM

client = socket(AF_INET, SOCK_STREAM)

client.connect(('127.0.0.1', 500))

for i in range(20):
    client.send(f"TEST COMMUNICATION {i}".encode())