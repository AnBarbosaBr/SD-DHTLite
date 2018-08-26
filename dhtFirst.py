from dhtApi import DhtApi
from threading import Thread
import time
import sys
import socket

class Dht(DhtApi):
	def __init__(self, port, id_this):
		self.conectado = False
		self.addr = '127.0.0.1'
		self.port = port
		self.id = id_this
		self.sucessor = None
		self.predecessor = None
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

		if found:
			self.recvSocket.listen()
			conn, addr = self.recvSocket.accept()
			with conn:
				data = conn.recv(1024)
				cmd = data.decode().split(" ")

			if cmd[0] == "JOIN_OK":
				self.sendSocket = socket.socket()
				self.sucessor = (int(cmd[1]), cmd[2], int(cmd[3]))
				self.predecessor = (int(cmd[4]), cmd[5], int(cmd[6]))
				#time.sleep(5)
				self.sendSocket.connect((self.predecessor[1], self.predecessor[2]))

				msg = "NEW_NODE {} {} {}".format(self.id, 
																		  self.addr,
																		  self.port)
				self.sendSocket.send(msg.encode())
				#self.sendSocket.close()
				#self.sendSocket.send(msg.encode())
				print("Mandei isso: ", msg)
				print("Meu predecessor: ", self.predecessor, " Meu sucessor: ", self.sucessor)
				

		else:
			thisNode = (self.id, self.addr, self.port)
			self.sucessor = self.predecessor = thisNode

		self.conectado = True
		thread = Thread(target=self.listen)
		thread.start()
		self.sendSocket.close()

		return self.conectado

	def leave(self):
		if not self.conectado:
			return "Nao conectado ainda"
		try:
			self.sendSocket = socket.socket()
			self.sendSocket.connect((self.sucessor[1], self.sucessor[2]))
			msg = "LEAVE {} {} {} \n".format(self.predecessor[0][0],
																			 self.predecessor[0][1],
																			 self.predecessor[0][2])
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()

			self.sendSocket = socket.socket()

			self.sendSocket.connect((self.predecessor[1], self.predecessor[2]))
			msg = "NODE_GONE {} {} {} \n".format(self.sucessor[0],
																			 self.sucessor[1],
																			 self.sucessor[2])
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()

		except Exception as err:
			print(err)

	def listeningNew(self, conn):
		while 1:
			try:
				data = conn.recv(1024)
				if not data:
					break
				cmd = data.decode().split(" ")
				print("Recebi: ", cmd)


				if cmd[0] == "JOIN":
					id_new = int(cmd[1])
					ip_new = cmd[2]
					port_new = int(cmd[3])
					s = socket.socket()

					if self.id < id_new and self.predecessor[0] < self.id:
						s.connect((self.sucessor[1], self.sucessor[2]))
						msg = "JOIN {} {} {} \n".format(id_new,
																				 		ip_new,
																				 		port_new)
						#self.sendSocket.send(msg.encode())
						#self.sendSocket.close()
						print("Enviei: ", msg)
						s.send(msg.encode())

					else:
						s.connect((ip_new, port_new))
						msg = "JOIN_OK {} {} {} {} {} {}".format(self.id, 
																	  self.addr,
																	  self.port,
																	  self.predecessor[0],
																	  self.predecessor[1],
																	  self.predecessor[2])
						print("Enviei: ", msg)
						s.send(msg.encode())
						#self.sendSocket.close()
						#time.sleep(2)
						#conn.send(msg.encode())
						#if self.sucessor == (self.id, self.addr, self.port):
						#	self.sucessor = (id_new, ip_new, port_new)
						self.predecessor = (id_new, ip_new, port_new)


				elif cmd[0] == "NEW_NODE" or "NODE_GONE":
					id_new = int(cmd[1])
					ip_new = cmd[2]
					port_new = int(cmd[3])

					self.sucessor = (id_new, ip_new, port_new)

				elif cmd[0] == "LEAVE":
					id_new = int(cmd[1])
					ip_new = cmd[2]
					port_new = int(cmd[3])

					self.predecessor = (id_new, ip_new, port_new)

				elif cmd[0] == "STOP":
					stop = True	

				else:
					print(cmd)

				print("Meu predecessor: ", self.predecessor, " Meu sucessor: ", self.sucessor)

			except Exception as err:
				break
				print(err)
		conn.close()


	def listen(self):
		self.recvSocket.listen()
		stop = False
		while not stop:
			try:
				conn, addr = self.recvSocket.accept()
				thread = Thread(target=self.listeningNew, args=(conn,))
				thread.start()
					
			except ValueError as err:
				stop = True
				print(err)

	def store(self, chave, valor):
		pass

	def retrieve(self, chave):
		pass
		
	def remove(self, chave):
		pass	

hosts = [ 
				 ('127.0.0.1', 7001)]
d = Dht(int(sys.argv[1]), int(sys.argv[2]))
d.join(hosts)

