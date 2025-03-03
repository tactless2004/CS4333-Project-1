from socket import socket, AF_INET, SOCK_STREAM
import sys
from threading import Thread
from time import sleep
from multiprocessing import Process
import os
import signal
from psutil import pid_exists
# Global Constants
# TODO: maybe we do something more elegant later
LOOPBACK_ADDR = '127.0.0.1'
PORT = 12987    # Default provided by Prof. Riley
BUFFER = bytearray(4096)
EXIT_STRING = "QUIT\n"
STATUS_STRING = "STATUS\n"

# Prints the provided warning, provides proper command usage, sys exits, refuses to eloborate.
def print_cmd_usage_warning(warning = "Invalid Arguments") -> None:
    print(warning)
    print("usage: python Talk.py [hostname | IPaddress] [-p portnumber]")
    sys.exit()
    return # Linter is complaining about not having a return, but it's return type None :(

# Prints the help message, requested by -help arg
def print_help_message() -> None:
    print("Talk.py\n    A commandline peer-to-peer communication app written by Leyton McKinney")
    print("SERVER MODE\n   usage: python Talk.py -s [-p portnumber]")
    print("HOST MODE\n   usage: python Talk.py -h [hostname | IPaddress] [-p portnumber]")
    print("AUTO MODE\n    usage: python Talk.py -a [hostname | IPaddress] [-p portnumber]")

# Generic warning printer.
def print_runtime_error(warning = "Talk.py has encountered an unrecoverable issue.") -> None:
    raise RuntimeError(warning)

def init_server(ip_address: str, port: int, input_handler: Process) -> None:
    server_socket = socket(AF_INET, SOCK_STREAM)

    try:
        server_socket.bind((ip_address, port))
    except OSError:
        print_runtime_error("Server unable to listen on specified port.")

    Listening = True
    server_socket.listen(1) # 1 specifies the maximum number of clients that can connect to this socket.

    while Listening: # Listening mode :)
        if not pid_exists(input_handler.pid): # If we just exitted connecting mode, we need to reinit the nonbound_input_handler
            input_handler = Process(target = nonbound_input_handler, args=(ip_address, port, is_server))
            input_handler.start()

        client_socket, client_address = server_socket.accept()
        # client_address -> (hostname, port)
        # client_socket -> socket.socket
        print (f"Connection Initiated by {client_address} on port {PORT}")
 
        closed_state = [False] # closed_state is a shared boolean that tells generic_send to exit, whenever generic receive gets the EXIT signal.
        if pid_exists(input_handler.pid): # Sometimes the non-bound input handler is already dead, before we hit this point.
            os.kill(input_handler.pid, signal.SIGINT)

        Thread(target=generic_receive, args=(ip_address, port, client_socket, closed_state), daemon=True).start()
        p = Process(target=generic_send, args=(ip_address, port, client_socket, True, client_address, closed_state))
        p.start()
        waitingToKillSender = True
        while waitingToKillSender:
            if closed_state[0]:  # When the generic_recieve() function indiciates that the QUIT message has been received, we want to kill the sender to prevent deadlock
                os.kill(p.pid, signal.SIGINT)
                waitingToKillSender = False
            elif not pid_exists(p.pid) and not closed_state[0]:  # If the generic_send method sends the EXIT message it should exit cleanly, in this case we don't need to close the sender manually
                waitingToKillSender = False
                Listening = False  # If the server sends EXIT, then the server side should close too.

def init_client(ip_address: str, port: int, input_handler: Process) -> None:
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect((ip_address, port))
    except ConnectionRefusedError:
        print_runtime_error("Client unable to communicate with server.")

    server_address = client_socket.getpeername()
    (ip_address, port) = client_socket.getsockname()
    os.kill(input_handler.pid, signal.SIGINT) # Replace the nonbound input handler with a socket bound input handler
    closed_state = [False]
    Thread(target=generic_receive, args=(ip_address, port, client_socket, closed_state), daemon=True).start()
    send = Process(target=generic_send, args=(ip_address, port, client_socket, False, server_address, closed_state)) # Changed this to not thread
    send.start()
    processKilled = False
    while not processKilled:
        if closed_state[0]:
            processKilled = True
            os.kill(send.pid, signal.SIGINT)
        elif not pid_exists(send.pid) and not closed_state[0]:
            processKilled = True

def generic_send(ip_address: str, port: int, client_socket: socket, is_server: bool, client_address: tuple, closed_state: list) -> None:
    Sending = True
    sys.stdin = open(0) # Python multiprocessing.Process changes stdin's fd to some other number, need it to be 0
    while Sending:
        message = sys.stdin.readline()
        sent_exit = (message == EXIT_STRING)
        sent_status = (message.strip() == "STATUS")
        if message and sent_exit:
            closed_state[0] = True
            client_socket.send(EXIT_STRING.encode())
            Sending = False

        elif sent_status:
            if is_server:
                print(f"[STATUS] Client: {client_address[0]}:{client_address[1]}; Server: {ip_address}:{port}")
            else:
                print(f"[STATUS] Client: {ip_address}:{port}; Server: {client_address[0]}:{client_address[1]}")

        elif message:
            client_socket.send(f"{message}".encode())


def generic_receive(ip_address: str, port: int, client_socket: socket, closed_state: list) -> None:
    Connected = True

    while Connected:
        try:
            message = client_socket.recv(4096) # Message Buffer Length: 4096 Bytes
            if message and message.decode() == EXIT_STRING:
                Connected = False
                closed_state[0] = True
                client_socket.close()

            elif message:
                print(f"[remote] {message.decode()}", end="")
        except ConnectionResetError:
            Connected = False
        except ConnectionAbortedError:
            Connected = False
    
def nonbound_input_handler(ip_address: str, port: int, is_server: bool) -> None:
    sys.stdin = open(0) # Python multiprocessing.Process changes stdin's fd to some other number, need it to be 0
    while True:
        message = sys.stdin.readline()
        if message.strip() == "STATUS":
            if is_server:
                print(f"[STATUS] Client: NONE; Server: {ip_address}:{port}\n")
            else:
                print(f"[STATUS] Client: {ip_address}:{port}; Server: NONE\n")
        if message.strip() == "QUIT":
            sys.exit() # I don't think this is a project requirement, but it couldn't hurt to process QUIT while not bound on either end.




if __name__ == "__main__":
    sys.argv = sys.argv[1:] # Strip 'Talk.py' from argv
    # Check that the input is good
    # Note: Bad arguments are an exit condition.
    #       We don't proceed after bad args.
    args_not_provided = (len(sys.argv) == 0)
    is_server = (sys.argv[0]=="-s") if not args_not_provided else False
    is_client = (sys.argv[0]=='-h') if not args_not_provided else False
    is_help = (len(sys.argv) >= 1 and sys.argv[0] == "-help")
    if is_server:
        port_provided = (len(sys.argv) == 3) and not args_not_provided and sys.argv[1] == "-p"
        if port_provided:
            try:
                PORT = int(sys.argv[2])
            except ValueError:
                print_runtime_error("Invalid Port.")
        input_handler = Process(target = nonbound_input_handler, args=(LOOPBACK_ADDR, PORT, is_server))
        input_handler.start()
        init_server(LOOPBACK_ADDR, PORT, input_handler)

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
        input_handler = Process(target = nonbound_input_handler, args=(LOOPBACK_ADDR, PORT, is_server))
        input_handler.start()
        init_client(LOOPBACK_ADDR, PORT, input_handler)
    elif is_help:
        print_help_message()
    else:
        print("This shouldn't happen, check for semantic error.")

    
    

    
    

