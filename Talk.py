from socket import socket, AF_INET, SOCK_STREAM
import sys
from threading import Thread

# Global Constants
# TODO: maybe we do something more elegant later
LOOPBACK_ADDR = '127.0.0.1'
PORT = 500
BUFFER = bytearray(4096)

# Prints the provided warning, provides proper command usage, sys exits, refuses to eloborate.
def print_cmd_usage_warning(warning = "Invalid Arguments") -> None:
    print(warning)
    print("usage: python Talk.py [hostname | IPaddress] [-p portnumber]")
    sys.exit()
    return # Linter is complaining about not having a return, but it's return type None :(

# Generic warning printer.
def print_runtime_warning(warning = "Talk.py has encountered an unrecoverable issue.") -> None:
    print(warning)
    sys.exit()

def init_server(ip_address: str, port: int) -> None:
    server_socket = socket(AF_INET, SOCK_STREAM)
    try:
        server_socket.bind((ip_address, port))
    except OSError:
        print_runtime_warning("Server unable to listen on specified port.")
    Listening = True
    server_socket.listen(1) # 1 specifies the maximum number of clients that can connect to this socket.

    while Listening: # Listening mode :)
        client_socket, client_address = server_socket.accept()
        # client_address -> (hostname, port)
        # client_socket -> socket.socket
        print (f"Connection Initiated by {client_address} on port {PORT}")
 
        # client_socket.send('Ping from server'.encode()) 
        Thread(target=generic_receive, args=(ip_address, port, client_socket), daemon=True).start()
        Thread(target=generic_send, args=(ip_address, port, client_socket), daemon=True).start()

def generic_send(ip_address: str, port: int, client_socket: socket):
    Sending = True

    while Sending:
        message = sys.stdin.readline()
        if message:
            client_socket.send(f"{message}".encode())

def generic_receive(ip_address: str, port: int, client_socket: socket):
    Connected = True

    while Connected:
        try:
            message = client_socket.recv(64)
            if len(message)>0:
                print(message)
                break
        except KeyboardInterrupt:
            sys.exit()

def init_client(ip_address: str, port: int) -> None:
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect((ip_address, port))
    except ConnectionRefusedError:
        print_runtime_warning("Client unable to communicate with server.")

    Thread(target=generic_receive, args=(ip_address, port, client_socket), daemon=True).start()
    Thread(target=generic_send, args=(ip_address, port, client_socket), daemon=True).start()
    




if __name__ == "__main__":
    sys.argv = sys.argv[1:]
    # Check that the input is good
    # Note: Bad arguments are an exit condition.
    #       We don't proceed after bad args.
    args_not_provided = (len(sys.argv) == 0)
    port_provided = (len(sys.argv) >= 4) and not args_not_provided and sys.argv[2] == "-p"
    is_server = (sys.argv[0]=="-s") if not args_not_provided else False
    is_client = (sys.argv[0]=='-h') if not args_not_provided else False

    if args_not_provided:
        print_cmd_usage_warning()

    elif sys.argv[0] != "-h":
        print_cmd_usage_warning("Please provide a hostname/IP Address.")

    elif port_provided:
        try:
            PORT = int(sys.argv[2])
        except ValueError:
            print_cmd_usage_warning("Invalid Port.")
    
    ip_addr = sys.argv[1] if sys.argv[1] else LOOPBACK_ADDR
    
    if is_server:
        init_server(ip_addr, PORT)
    elif is_client:
        init_client(ip_addr, PORT)
    else:
        print("This shouldn't happen, check semantic logic.")
    
    

    
    

