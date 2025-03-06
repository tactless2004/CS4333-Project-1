# CS-4333-Project-1

## USAGE

**Client Mode**

```python Talk.py -h [hostname|ipaddress] [-p portnumber]```

Client mode attempts to connect to a ```Talk.py``` server running on the chosen ```hostname:port```. If there is no server running it will exit with a ```python.RuntimeError``` **Client unable to communicate with server**.

**Server Mode**

```python Talk.py -s [-p portnumber]```

Server mode attempts to bind to a socket to listen/accept at most one client connection. If the server cannot bind to the port it will raise a ```python.RuntimeError``` **Server unable to listen on specified port**.

**Auto Mode**

```python Talk.py -a [hostname|ipaddress] [-p portnumber]```

Auto mode attempts to connect to a server running on ```hostname:port```, if this fails it will attempt to become the server running on that port.

**Help Mode**

```python Talk.py [-h]```

Help mode prints a help message which consists of the usage information above.

## Reserved Messages

```QUIT``` will not be printed, on the other end of the communication link, but instead will either perform a client or a server exit.
- Server Exit: Closes the server and the client.
- Client Exit: Closes the client and puts the server into listening mode.

```STATUS``` returns the connection status for the client or server, and will not be transmitted.
- Example: ```[STATUS] Client: 127.0.0.1:2048, Server: 127.0.0.1:4096```

## Project Requirements


- [x] Bind a server socket to eithe the default host and port or a specified host and port
- [x] Return the status of both an unbound and a bound socket (does not need to print yet)
- [x] Print help instructions (help mode)
- [x] Should be able to close and free ports
- [x] Have a server socket listen for incoming connections (server mode)
- [x] Connect a client socket to the server socket (client mode)
- [x] Return the status of a connected socket (does not need to print yet)
- [x] Close both the server socket and client socket upon connection close or exit
- [x] Communicate messages from STDIN across a socket to a remote host
- [x] Communicate messages from a remote host to STDOUT
- [x] Communications should be asynchronous (threads are not required)
- [x] Complete auto mode
- [x] Print connection status upon command STATUS
- [x] Close the connection upon command QUIT
- [ ] Finish SocketWrapper
    - I used Python instead of Java, so this will not be completed.
- [ ] Write report
    - Report forthcoming.

## Acknowledgements/Guidelines

This project was specified by [Dr. Ian Riley]("https://github.com/isr413"). The code was written by Leyton McKinney.

This code is free to use and modfiy for personal projects, but not copy in an attempt to represent this as one's own work, especially in an academic context.