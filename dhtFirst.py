from dhtApi import DhtApi
import socket

class Dht(DhtApi):
	def __init__(self):
		self.conectado = False
		self.addr = '127.0.0.1'
		self.port = 7001
		self.id = 1
		self.rAndLNodes = [(2,'127.0.0.1', 7005), (3,'127.0.0.1', 7000)]
		self.sendSocket = socket.socket()
		self.recvSocket = socket.socket()
		self.recvSocket.bind((self.addr, self.port))

	def join(self, listaDePossiveisHosts):
		found = False
		for host in listaDePossiveisHosts:
			try:
				self.sendSocket.connect(host)
				msg = "JOIN {} {} {} \n".format(self.id,
																		 		self.addr,
																		 		self.port)
				self.sendSocket.send(msg.encode())
				found = True
				self.sendSocket.close()
				break
			except ConnectionRefusedError as conerr:
				print(conerr)
			except Exception as err:
				print(type(err))

		if found:
			self.recvSocket.listen()
			conn, addr = self.recvSocket.accept()
			with conn:
				data = conn.recv(1024)
				cmd = data.decode().split(" ")
			if cmd[0] == "JOIN_OK":
				sucessor = (int(cmd[1]), cmd[2], int(cmd[3]))
				predecessor = (int(cmd[4]), cmd[5], int(cmd[6]))
				#print(sucessor, predecessor)
				self.rAndLNodes = [predecessor, sucessor]
				self.sendSocket.connect((self.rAndLNodes[0][1], self.rAndLNodes[0][2]))

				msg = "NEW_NODE {} {} {}".format(self.id, 
																		  self.addr,
																		  self.port)
				self.sendSocket.send(msg.encode())
				self.sendSocket.close()

	def leave(self):
		try:
			self.sendSocket.connect((self.rAndLNodes[1][1], self.rAndLNodes[1][2]))
			msg = "LEAVE {} {} {} \n".format(self.rAndLNodes[0][0],
																			 self.rAndLNodes[0][1],
																			 self.rAndLNodes[0][2])
			self.sendSocket.send(msg.encode())
		except Exception as err:
			print(err)

	def store(self, chave, valor):
		pass

	def retrieve(self, chave):
		pass
		
	def remove(self, chave):
		pass	

hosts = [('127.0.0.1', 7000), ('127.0.0.1', 7002)]
d = Dht()
d.join(hosts)

