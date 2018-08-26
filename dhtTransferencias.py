# coding:utf-8
from dhtApi import DhtApi, ArmazenamentoLocal
from threading import Thread
import time
import sys
import socket


class Dht(DhtApi):
	def __init__(self, port, id_this):
		self.armazenamento = ArmazenamentoLocal()
		self.conectado = False
		self.addr = '127.0.0.1'
		self.port = port
		self.id = id_this
		self.hash_proprio = self.hash_de(id)
		self.sucessor = None
		self.hash_sucessor = None
		self.predecessor = None
		self.hash_predecessor = None
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
				self.sucessor = (int(cmd[1]), cmd[2], int(cmd[3]))
				self.predecessor = (int(cmd[4]), cmd[5], int(cmd[6]))
				print(self.sucessor, self.predecessor)
				#time.sleep(5)
				self.sendSocket.connect((self.predecessor[1], self.predecessor[2]))

				msg = "NEW_NODE {} {} {}".format(self.id, 
																		  self.addr,
																		  self.port)
				self.sendSocket.send(msg.encode())
				self.sendSocket.close()
				print("Here", self.sucessor, self.predecessor)

		else:
			thisNode = (self.id, self.addr, self.port)
			self.sucessor = self.predecessor = thisNode

		self.conectado = True
		thread = Thread(target=self.listen)
		thread.start()

		return self.conectado

	def leave(self):
		if not self.conectado:
			return "Nao conectado ainda"
		try:
			self.sendSocket.connect((self.sucessor[1], self.sucessor[2]))
			msg = "LEAVE {} {} {} \n".format(self.predecessor[0][0],
																			 self.predecessor[0][1],
																			 self.predecessor[0][2])
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()

			self.sendSocket.connect((self.predecessor[1], self.predecessor[2]))
			msg = "NODE_GONE {} {} {} \n".format(self.sucessor[0],
																			 self.sucessor[1],
																			 self.sucessor[2])
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()
			self.recvSocket.close()

		except Exception as err:
			print(err)

	def listen(self):
		self.recvSocket.listen()
		stop = False
		while not stop:
			try:
				conn, addr = self.recvSocket.accept()
				with conn:
					data = conn.recv(1024)
					if data:
						cmd = data.decode().split(" ")

						if cmd[0] == "JOIN":
							self.processJOIN(cmd)

						elif cmd[0] == "NEW_NODE" or "NODE_GONE":
							self.processNODE_CHANGE(cmd);		

						elif cmd[0] == "LEAVE":
							self.processLEAVE(cmd)

						elif cmd[0] == "STOP":
							self.processSTOP(cmd)

						elif cmd[0] == "STORE":	
							self.processSTORE(cmd)
						
						elif cmd[0] == "RETRIEVE":
							self.processRETRIEVE(cmd)

						elif cmd[0] == "OK":
							self.processOK(cmd)
						
						elif cmd[0] == "NOT_FOUND":
							self.processNOT_FOUND(cmd)
						
						elif cmd[0] == "TRANSFER":
							self.processTRANFER(cmd)

						else:
							print(cmd)

			except ValueError as err:
				stop = True
				print(err)

	def store(self, chave, valor):
		pass

	def retrieve(self, chave):
		pass
		
	def remove(self, chave):
		pass	

	
	def processJOIN(self, cmd):	
		""" Processa um comando JOIN. Deve receber um cmd no formato:
			'JOIN id porta'.
			Retorna uma excessão se o comando recebido não for JOIN."""

		self.rejeitaSeComandoErrado(cmd, "JOIN")
    	
		id_new = int(cmd[1])
		ip_new = cmd[2]
		port_new = int(cmd[3])

		if self.id < id_new and self.predecessor[0] < self.id:
			self.sendSocket.connect((self.sucessor[1], self.sucessor[2]))
			msg = "JOIN {} {} {} \n".format(id_new,
																			ip_new,
																			port_new)
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()

		else:
			self.sendSocket.connect((ip_new, port_new))
			msg = "JOIN_OK {} {} {} {} {} {}".format(self.id, 
															self.addr,
															self.port,
															self.predecessor[0],
															self.predecessor[1],
															self.predecessor[2])
			print(msg)
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()

	def processNODE_CHANGE(self, cmd):
		"""
		Processa um comando NODE_GONE ou NEW_NODE. Deve receber um cmd no formato:
		'{NEW_NODE|NODE_GONE} id_do_novo_node ip_novo_node porta_novo_node'.
		Retorna uma excessão se o comando recebido não for NEW_NODE ou NODE_GONE.
		"""
		
		if not (cmd[0] == "NEW_NODE" or cmd[0] == "NODE_GONE"):
			raise Exception("Process NODE_CHANGE deve receber um cmd 'NEW_NODE' ou 'NODE_GONE'")

		id_new = int(cmd[1])
		ip_new = cmd[2]
		port_new = int(cmd[3])

		self.sucessor = (id_new, ip_new, port_new)
		self.hash_sucessor = self.hash_de(id_new)
	
	def processLEAVE(self, cmd):
		"""
		Processa um Comando LEAVE. O comando deve estar no formato
		'LEAVE id_novo ip_novo porta_nova'
		Dispara uma excessão se recebe um comando que não começa com LEAVE.
		"""
		if not cmd[0]=="LEAVE":
			raise Exception("Process Leave deve receber um cmd 'LEAVE'")
		id_new = int(cmd[1])
		ip_new = cmd[2]
		port_new = int(cmd[3])
		self.predecessor = (id_new, ip_new, port_new)
		self.hash_predecessor = self.hash_de(id_new)

	def processSTOP(self, cmd):
		"""
		 Processa um Comando STOP. O comando deve estar no formato
			'STOP'
		Dispara uma excessão se recebe um comando que não começa com STOP.
		"""
		if not cmd[0]=="STOP":
			raise Exception("Process Stop deve receber um cmd 'STOP'")
		self.processSTOP(cmd)
		stop = True	

	def processSTORE(self, cmd):
		self.rejeitaSeComandoErrado(cmd, "STORE")
		chave_a_armazenar = cmd[1]
		valor_a_armazenar = cmd[2]

		if self.encaminharCmdSeNaoForResponsavel(cmd):
			print("Mensagem encaminhada.")
		else:
			self.armazenamento.store(chave_a_armazenar, valor_a_armazenar);
	
	def processRETRIEVE(self, cmd):
		self.rejeitaSeComandoErrado(cmd, "RETRIEVE")

	def processOK(self, cmd):
		self.rejeitaSeComandoErrado(cmd, "OK")

	def processNOT_FOUND(self, cmd):
		self.rejeitaSeComandoErrado(cmd, "NOT_FOUND")

	def processTRANFER(self, cmd):
		self.rejeitaSeComandoErrado(cmd, "TRANSFER")

	def responsabilidade_do_predecessor(self, chave):
		"""
		Se existe um predecessor, ele é responsável se:
			1) NÃO É O ULTIMO NÓ(seu hash não é maior do que o hash do self)
			2) Hash da chave é menor do que seu hash. Espera-se,
		nesse caso, que ele verifique se algum nó anterior a ele possa ser responsável.	
		
		"""
		if not self.predecessor:
			return False
		
		hash_prede = self.hash_predecessor
		hash_proprio = self.hash_proprio
		hash_chave = self.hash_de(chave)
		if(hash_prede > hash_proprio): 
			# Somo o nó de menor hash. Nosso predecessor é o de maior hash
			if( hash_chave > hash_prede):
				# O hash da chave é MAIOR do que nosso maior nó. 
				# Então ele é responsável.
				return True

		else: # O antecessor tem o hash menor que o nosso.
			if (hash_chave < hash_prede):
				# O hash da chave é menor do que nosso predecessor.
				# Ele irá ser responsável 
				return True
		# Nenhuma das condições anteriores foi verdadeira,o antecessor não é responsável.
		return False

	def responsabilidade_do_sucessor(self, chave):	
		"""
		Se existe um sucessor, ele é responsável em qualquer um desses casos:
			É o primeiro nó, e o hash da chave é menor que seu hash.
			É um nó qualquer, e o hash da chave é maior do que o hash de self. Espera-se,
		nesse caso, que ele verifique se algum nó sucessor a ele possa ser responsável.

		"""
		if not self.sucessor:
			return False

		hash_sucessor = self.hash_sucessor
		hash_proprio = self.hash_proprio
		hash_chave = self.hash_de(chave)

		if hash_sucessor < hash_proprio: 
			# Nosso sucessor é o nó de menor hash. Somos o ultimo nó.
			if(hash_chave < hash_sucessor):
				# A chave tem hash menor que o menor nó, que é nosso sucessor
				# Ele é o responsável
				return True
		else: 
			# Nosso sucessor é um nó maior do que nós.
			if(hash_chave > hash_proprio):
				# Nós só cuidamos de chaves ATÉ nosso próprio hash.
				return True

	def temResponsabilidade(self, chave):
		"""
			Retorna True se ambas as condições abaixo forem verdadeiras:
			  O hash da chave é MAIOR do que o ID do predecessor OU não há PREDECESSOR
			  O hash da chave é MENOR do que o ID desse armazenador OU não há um SUCESSOR
		"""
		if(self.responsabilidade_do_predecessor(chave)):
			return False
		if(self.responsabilidade_do_sucessor(chave)):
			return False
		return True

	def encaminharCmdSeNaoForResponsavel(self, cmd):
		"""
		Encaminha o comando para o antecessor ou para o sucessor, 
		caso esse nó não seja o responsável.
		Retorna True se houve encaminhamento.
		Retorna False se não houve encaminhamento.
		"""
		if(self.responsabilidade_do_predecessor(chave_a_armazenar)):
			self.encaminhaPredecessor(cmd)
			return True
		
		elif(self.responsabilidade_do_sucessor(chave_a_armazenar)):
			self.encaminhaSucessor(cmd)
			return True
		
		return False
		
			
	def encaminhaSucessor(self, msg):
		# Conectamos ao sucessor.
		self.sendSocket.connect((self.sucessor[1], self.sucessor[2]))

		# Enviamos a mensagem:
		self.sendSocket.send(msg.encode())
		print("Mensagem encaminhada para o sucessor. Conteúdo:\n\t{}\n".format(msg))
		# Fechamos a conexão
		self.sendSocket.close()

	def encaminhaPredecessor(self, msg):
		# Conectamos ao predecessor.
		self.sendSocket.connect((self.predecessor[1], self.predecessor[2]))

		# Enviamos a mensagem:
		self.sendSocket.send(msg.encode())
		print("Mensagem encaminhada para o predecessor. Conteúdo:\n\t{}\n".format(msg))
		# Fechamos a conexão
		self.sendSocket.close()
	

	def rejeitaSeComandoErrado(self, cmd, comando_esperado):
		if not (cmd[0] == comando_esperado):
			raise Exception(
				"Process {} deve receber um cmd '{}', recebido {}".format(
					comando_esperado, comando_esperado, cmd[0]))

hosts = [('127.0.0.1', 7000), ('127.0.0.1', 7001)]


porta = 54141
identificador = 2451

if len(sys.argv) == 3:
	porta = int(sys.argv[1])
	identificador = int(sys.argv[2])

d = Dht(porta, identificador)
d.join(hosts)

# d2 = Dht(porta+20, 5147)
# d2.join([('127.0.0.1', porta)])
