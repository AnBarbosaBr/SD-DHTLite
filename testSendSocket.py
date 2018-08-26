import socket
s = socket.socket()
s.connect(('127.0.0.1',7001))
msg = "AA"
s.send(msg.encode())