import socket
s = socket.socket()
s.connect(('127.0.0.1',7001))
msg = "JOIN_OK {} {} {} {} {} {} \n".format(2,
														 			 '127.0.0.1',
														 			 7004,
														 			 3,
														 			 '127.0.0.1',
														 			 7007,
														 			 )
s.send(msg.encode())