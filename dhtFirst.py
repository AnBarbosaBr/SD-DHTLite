from dhtApi import DhtApi, ArmazenamentoLocal
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
		# Armazenamento:
		self.armazenamento = ArmazenamentoLocal()
		# Hashes:
		self.hash_proprio = self.hash_de(id)
		self.hash_sucessor = None
		self.hash_predecessor = None

	def join(self, listaDePossiveisHosts):
		#Inicio do join, checa a lista dos possíveis hosts e conecta no primeiro que conseguir 
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

		#Se conseguir significa que ja existe a dht, então precisa se comunicar para entrar
		if found:
			#Esperando o JOIN_OK de algum no do anel
			self.recvSocket.listen()
			conn, addr = self.recvSocket.accept()
			with conn:
				data = conn.recv(1024)
				cmd = data.decode().split(" ")

			if cmd[0] == "JOIN_OK":
				#Ao receber o JOIN_OK ajeita o predecessor e sucessor
				self.sendSocket = socket.socket()

				self.sucessor = (int(cmd[1]), cmd[2], int(cmd[3]))
				self.predecessor = (int(cmd[4]), cmd[5], int(cmd[6]))

				#E envia o seu endereco e id para o predecessor
				self.sendSocket.connect((self.predecessor[1], self.predecessor[2]))

				msg = "NEW_NODE {} {} {}".format(self.id, 
																		  self.addr,
																		  self.port)
				self.sendSocket.send(msg.encode())

				print("Mandei isso: ", msg)
				print("Meu predecessor: ", self.predecessor, " Meu sucessor: ", self.sucessor)
				

		else:
			#Caso seja o primeiro elemento, seu sucessor e predecessor e ele mesmo
			thisNode = (self.id, self.addr, self.port)
			self.sucessor = self.predecessor = thisNode

		#Apos tudo esta conectado na rede
		self.conectado = True

		#Thread para escutar as mensagens que vai recebendo da rede
		#E uma nova thread para poder realizar operacoes ao mesmo tempo
		thread = Thread(target=self.listen)
		thread.start()

		self.sendSocket.close()

		return self.conectado

	def leave(self):
		#Metodo de saida do no da rede

		if not self.conectado:
			return "Nao conectado ainda"

		try:
			#Mandando mensagem para o seu sucessor com a operacao de saida e o endereco de seu
			#predecessor para atualizacao
			self.sendSocket = socket.socket()
			self.sendSocket.connect((self.sucessor[1], self.sucessor[2]))
			msg = "LEAVE {} {} {} \n".format(self.predecessor[0][0],
																			 self.predecessor[0][1],
																			 self.predecessor[0][2])
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()

			#Mandando mensagem para o seu predecessor com a operacao de saida e o endereco de seu
			#sucessor para atualizacao
			self.sendSocket = socket.socket()

			self.sendSocket.connect((self.predecessor[1], self.predecessor[2]))
			msg = "NODE_GONE {} {} {} \n".format(self.sucessor[0],
																			 self.sucessor[1],
																			 self.sucessor[2])
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()

		except Exception as err:
			print(err)

	def listen(self):
		#Handler de novas conexoes, ao receber uma requisicao ele cria uma nova thread
		#para trata-la
		self.recvSocket.listen()
		stop = False
		while not stop:
			try:
				conn, addr = self.recvSocket.accept()
				thread = Thread(target=self.listening_new, args=(conn,))
				thread.start()
					
			except ValueError as err:
				stop = True
				print(err)

	def listening_new(self, conn):
		#Funcionamento da subthread para tratamento da requisicao recebida
		while 1:
			try:
				data = conn.recv(1024)
				if not data:
					break
				cmd = data.decode().split(" ")
				print("Recebi: ", cmd)

				#Se o comando recebido for JOIN, checar a posicao devida na rede
				if cmd[0] == "JOIN":
					id_new = int(cmd[1])
					ip_new = cmd[2]
					port_new = int(cmd[3])
					s = socket.socket()

					#Checando se deve passar ou nao a requisicao do novo no para frente na rede
					#Se nao estiver na posicao certa, e enviado para seu sucessor
					if self.id < id_new and self.predecessor[0] < self.id:
						s.connect((self.sucessor[1], self.sucessor[2]))
						msg = "JOIN {} {} {} \n".format(id_new,
																				 		ip_new,
																				 		port_new)

						print("Enviei: ", msg)
						s.send(msg.encode())

					#Caso contrario manda um JOIN_OK para o novo no com o seu endereco como sucessor,
					#o endereco de seu predecessor e atualiza seu predecessor para o novo no
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
						self.predecessor = (id_new, ip_new, port_new)

				#Caso de entrada ou saida de um no, apenas para atualizar 
				#o predecessor do mesmo
				elif cmd[0] == "NEW_NODE" or "NODE_GONE":
					id_new = int(cmd[1])
					ip_new = cmd[2]
					port_new = int(cmd[3])

					self.sucessor = (id_new, ip_new, port_new)

				#Ao receber LEAVE ele atualiza o predecessor
				elif cmd[0] == "LEAVE":
					id_new = int(cmd[1])
					ip_new = cmd[2]
					port_new = int(cmd[3])

					self.predecessor = (id_new, ip_new, port_new)

				#Comando de teste
				elif cmd[0] == "STOP":
					stop = True	

				else:
					print(cmd)

				print("Meu predecessor: ", self.predecessor, " Meu sucessor: ", self.sucessor)

			except Exception as err:
				break
				print(err)
		conn.close()

	def process_other_messages(self, cmd, conn):
		# Ao receber STORE, ele deve armazenar os valores recebidos
		if cmd[0] == "STORE":	
			self.processSTORE(cmd)
		
		#  Se não for o responsável, deve encaminhar a requisição,
		# junto com o solicitante, até que o responsável receba.
		# O responsável responderá diretamente ao requisitante.
		elif cmd[0] == "RETRIEVE":
			self.processRETRIEVE(cmd)

		# ???
		elif cmd[0] == "TRANSFER":
		self.processTRANSFER(cmd)

		# Remove um elemento da lista. A mensagem é encaminhada até
		# o responsável, que responderá diretamente ao solicitante.
		elif cmd[0] == "REMOVE":
			self.processREMOVE(cmd)	
																			
	def store(self, chave, valor):
		pass

	def retrieve(self, chave):
		pass
		
	def remove(self, chave):
		pass	


if __name__ == "__main__":
	#Para executar como main e necessario o seguinte comando
	#python dhtfirst.py [porta] [id]
	hosts = [('127.0.0.1', 7001)]
	d = Dht(int(sys.argv[1]), int(sys.argv[2]))
	d.join(hosts)

