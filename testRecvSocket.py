import socket
import time

HOST = '127.0.0.1'
PORT = 7000 
sS = socket.socket()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind((HOST, PORT))
	s.listen()
	conn, addr = s.accept()
	with conn:
		print('Connected by', addr)
		while True:
			data = conn.recv(1024)
			if not data:
				break
			print(data)
	msg = "JOIN_OK {} {} {} {} {} {} \n".format(2,
															 '127.0.0.1',
															 7000,
															 3,
															 '127.0.0.1',
															 7001,
															 )
	time.sleep(1)
	sS.connect(('127.0.0.1', 7001))
	sS.send(msg.encode())
	print("sent", msg)