from socket import socket, AF_INET, SOCK_STREAM
import sys
from threading import Thread

# Global Constants
# TODO: maybe we do something more elegant later
LOOPBACK_ADDR = '127.0.0.1'
PORT = 3000
BUFFER = bytearray(4096)
EXIT_STRING = "EXIT\n"
# Prints the provided warning, provides proper command usage, sys exits, refuses to eloborate.
def print_cmd_usage_warning(warning = "Invalid Arguments") -> None:
    print(warning)
    print("usage: python Talk.py [hostname | IPaddress] [-p portnumber]")
    sys.exit()
    return # Linter is complaining about not having a return, but it's return type None :(

# Generic warning printer.
def print_runtime_error(warning = "Talk.py has encountered an unrecoverable issue.") -> None:
    raise RuntimeError(warning)

def init_server(ip_address: str, port: int) -> None:
    server_socket = socket(AF_INET, SOCK_STREAM)
    client_closed = False
    try:
        server_socket.bind((ip_address, port))
    except OSError:
        print_runtime_error("Server unable to listen on specified port.")
    Listening = True
    server_socket.listen(1) # 1 specifies the maximum number of clients that can connect to this socket.

    while Listening: # Listening mode :)
        client_socket, client_address = server_socket.accept()
        # client_address -> (hostname, port)
        # client_socket -> socket.socket

        print (f"Connection Initiated by {client_address} on port {PORT}")

        Thread(target=generic_receive, args=(ip_address, port, client_socket, client_closed), daemon=True).start()
        generic_send(ip_address, port, client_socket, client_closed)


def generic_send(ip_address: str, port: int, client_socket: socket, client_closed: bool) -> None:
    Sending = True

    while Sending and not client_closed:
        message = sys.stdin.readline()
        sent_exit = (message == EXIT_STRING)

        print(client_closed)
        if message and sent_exit and not client_closed:
            client_socket.send(EXIT_STRING.encode())
            Sending = False
        elif message:
            client_socket.send(f"{message}".encode())

        if client_closed:
            Sending = False


def generic_receive(ip_address: str, port: int, client_socket: socket, client_closed: bool) -> None:
    Connected = True

    while Connected:
        try:
            message = client_socket.recv(4096) # Message Buffer Length: 4096 Bytes
            if message and message.decode() == EXIT_STRING:
                Connected = False
                client_closed = True
                client_socket.close()
            elif message:
                print(f"[remote] {message.decode()}")
        except ConnectionResetError:
            Connected = False
        except ConnectionAbortedError:
            Connected = False


def init_client(ip_address: str, port: int) -> None:
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect((ip_address, port))
    except ConnectionRefusedError:
        print_runtime_error("Client unable to communicate with server.")

    Thread(target=generic_receive, args=(ip_address, port, client_socket, False), daemon=True).start()
    generic_send(ip_address, port, client_socket, False) # Changed this to not thread
    




if __name__ == "__main__":
    sys.argv = sys.argv[1:] # Strip 'Talk.py' from argv

    # Check that the input is good
    # Note: Bad arguments are an exit condition.
    #       We don't proceed after bad args.
    args_not_provided = (len(sys.argv) == 0)
    is_server = (sys.argv[0]=="-s") if not args_not_provided else False
    is_client = (sys.argv[0]=='-h') if not args_not_provided else False

    if is_server:
        port_provided = (len(sys.argv) == 3) and not args_not_provided and sys.argv[1] == "-p"
        if port_provided:
            try:
                PORT = int(sys.argv[2])
            except ValueError:
                print_runtime_error("Invalid Port.")
        init_server(LOOPBACK_ADDR, PORT)

    elif is_client:
        host_provided = len(sys.argv) >= 2 and sys.argv[1] != "-p"
        LOOPBACK_ADDR = sys.argv[1] if host_provided else LOOPBACK_ADDR
        # Port Logic
        host_provided_and_port_provided = host_provided and len(sys.argv) == 4
        not_host_provided_and_port_provided = not host_provided and len(sys.argv) == 3 and sys.argv[1] == "-p"
        
        if host_provided_and_port_provided:
            try:
                PORT = int(sys.argv[3])
            except ValueError:
                print_runtime_error("Invalid Port.")

        elif not_host_provided_and_port_provided:
            try:
                PORT = int(sys.argv[2])
            except ValueError:
                print_runtime_error("Invalid Port.")          

        init_client(LOOPBACK_ADDR, PORT)

    else:
        print("This shouldn't happen, check for semantic error.")

    
    

    
    

