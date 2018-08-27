# coding=utf-8
import socket
import sys
import time
from threading import Thread
import copy
import random
from dhtApi import ArmazenamentoLocal, DhtApi


class Dht(DhtApi):
	def __init__(self):
		self.conectado = False
		self.addr = '127.0.0.1'
		self.port = 9999
		self.id = self.get_id(5)
		self.sucessor = None
		self.predecessor = None
		self.sendSocket = socket.socket()
		self.recvSocket = socket.socket()
		# Armazenamento:
		self.armazenamento = ArmazenamentoLocal()
		# Hashes:
		self.hash_proprio = self.hash_de(id)
		self.hash_sucessor = None
		self.hash_predecessor = None
		
	def get_id(self, n):
		num = -1
		#Uso apenas para teste, nao producao, uma maneira rapida de garantir 
		#que os numeros nao se choquem
		#Problema de escrita e leitura ao mesmo tempo
		#Leitura da lista crescendo linearmente, podendo perjudicar performance
		#E so funciona rodando diversos do mesmo diretorio
		current_nums = [] 
		with open("nums.txt", "r") as r:
			for line in r:
				current_nums.append(int(line.strip("\n")))
		aux = random.getrandbits(n)
		while num == -1:
			if aux in current_nums:
				aux = random.getrandbits(n)
			else:
				with open("nums.txt", "a+") as w:
					w.write(str(aux)+'\n')
				return aux

	def remove_number(self):
		current_nums = [] 
		with open("nums.txt", "r") as r:
			for line in r:
				current_nums.append(int(line.strip("\n")))
		current_nums.remove(self.id)
		with open("nums.txt", "w") as w:
			for n in current_nums:
				w.write(str(n)+'\n')

	def join(self, listaDePossiveisHosts, port):
		self.port = port
		#self.id = id_this
		self.sendSocket = socket.socket()
		self.recvSocket = socket.socket()
		self.recvSocket.bind((self.addr, self.port))
		#Inicio do join, checa a lista dos possíveis hosts e conecta no primeiro que conseguir 
		found = False
		for host in listaDePossiveisHosts:
			try:
				self.sendSocket.connect(host)
				msg = "JOIN {} {} {} \n".format(self.id,
																		 		self.addr,
																		 		self.port)
				self.sendSocket.send(msg.encode())
				print("Mandei isso: ", msg.replace("\n", ""))
				found = True
				self.sendSocket.close()
				break
			except ConnectionRefusedError as conerr:
				print("Nao foi possivel conectar no endereco: {} {}".format(host[0], host[1]))

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
			print("Criando nova DHT")
			#Caso seja o primeiro elemento, seu sucessor e predecessor e ele mesmo
			thisNode = (self.id, self.addr, self.port)
			self.sucessor = self.predecessor = thisNode
		print("Meu ID é: ", self.id)
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
			# Transfere seus itens para seu SUCESSOR:
			#self.transfer_leave() # <- Para a execução até a transferencia estar completa 

			#Mandando mensagem para o seu sucessor com a operacao de saida e o endereco de seu
			#predecessor para atualizacao
			self.sendSocket = socket.socket()
			self.sendSocket.connect((self.sucessor[1], self.sucessor[2]))
			msg = "LEAVE {} {} {} \n".format(self.predecessor[0],
																			 self.predecessor[1],
																			 self.predecessor[2])
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()
			print("Mandei isso: ", msg.replace("\n", ""))

			#Mandando mensagem para o seu predecessor com a operacao de saida e o endereco de seu
			#sucessor para atualizacao
			self.sendSocket = socket.socket()

			self.sendSocket.connect((self.predecessor[1], self.predecessor[2]))
			msg = "NODE_GONE {} {} {} \n".format(self.sucessor[0],
																			 self.sucessor[1],
																			 self.sucessor[2])
			
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()
			print("Mandei isso: ", msg.replace("\n", ""))
			self.recvSocket.close()
			self.conectado = False
			
			#self.remove_number()

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
					
			except Exception as err:
				stop = True

	def listening_new(self, conn):
		#Funcionamento da subthread para tratamento da requisicao recebida
		while 1:
			try:
				data = conn.recv(1024)
				if not data:
					break
				cmd = self.decode_mensagem_recebida(data.decode())
				print("Recebi: ", cmd)

				if cmd[0] == "LEAVE":
					id_new = int(cmd[1])
					ip_new = cmd[2]
					port_new = int(cmd[3])
					print("AA")
					self.predecessor = (id_new, ip_new, port_new)

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
						# EFETUANDO TRANSFERENCIA PARA O NOVO PREDECESSOR
						#self.transfer_novo_predecessor()
					s.close()


				#Caso de entrada ou saida de um no, apenas para atualizar 
				#o predecessor do mesmo
				elif cmd[0] == "NEW_NODE" or "NODE_GONE":
					id_new = int(cmd[1])
					ip_new = cmd[2]
					port_new = int(cmd[3])

					self.sucessor = (id_new, ip_new, port_new)
					

				#Ao receber LEAVE ele atualiza o predecessor



				#Comando de teste
				elif cmd[0] == "STOP":
					stop = True	

				else:
					if not cmd[0] == "LEAVE":
						self.process_other_messages(cmd, conn)

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

		elif cmd[0] == "TRANSFER_OK":
			self.processTRANSFER_OK(cmd)
		# Remove um elemento da lista. A mensagem é encaminhada até
		# o responsável, que responderá diretamente ao solicitante.
		elif cmd[0] == "REMOVE":
			self.processREMOVE(cmd)	


	def store(self, chave, valor):
		if self.responsavel_pela_chave(chave):
			self.armazenamento.store(chave, valor)
		else:
			comando = ("STORE", chave, valor, self.addr, self.port)
			self.encaminhaSucessor(comando)
			resposta = self.aguardaResposta()
			if resposta[0] == "ERROR":
				raise Exception("Erro ao adicionar valor: "+resposta[1])
	
	def retrieve(self, chave):
		if self.responsavel_pela_chave(chave):
			return self.armazenamento.retrieve(chave)
		else:
			comando = ("RETRIEVE", chave, self.addr, self.port)
			self.encaminhaSucessor(comando)	
			
			resposta = self.aguardaResposta()
			if resposta[0] == "ERROR":
				raise Exception("Erro ao adicionar valor: "+resposta[1])
			else:
				return resposta[1]

	def remove(self, chave):
		if self.responsavel_pela_chave(chave):
			return self.armazenamento.remove(chave)
		else:
			comando = ("RETRIEVE", chave, self.addr, self.port)
			self.encaminhaSucessor(comando)	
			
			resposta = self.aguardaResposta()
			if resposta[0] == "ERROR":
				raise Exception("Erro ao adicionar valor: "+resposta[1])
			else:
				return resposta[1]

	def transfer_leave(self):
		# Transfere os itens armazenados para o sucessor, 
		# quando receber a resposta TRANSFER_OK, removerá os itens do
		# armazenamento.	
		itens_a_enviar = copy.deepcopy(self.armazenamento.usuarios)
		for chave, valor in itens_a_enviar:
			comando = ("TRANSFER", chave, valor, self.addr, self.port)
			self.encaminhaSucessor(comando)
		del itens_a_enviar
		# Aguarda remover o ultimo item do armazenamento
		# while(len(self.armazenamento.usuarios) > 0):
			# time.sleep(0.01)

	def transfer_novo_predecessor(self):
		# Verifica quais itens armazenados devem ser transferidos para
		# o predecessor, e os transfere.
		itens_a_enviar = copy.deepcopy(self.armazenamento.usuarios)
		for chave, valor in itens_a_enviar:
			hash_chave = self.hash_de(chave)
			hash_antecessor = self.hash_de(predecessor[0])
			
			if (hash_chave < hash_antecessor):	
				comando = ("TRANSFER", chave, valor, self.addr, self.port)
				self.encaminhaSucessor(comando)
		del itens_a_enviar
	
	'''def transfer_novo_sucessor(self):'''
		# Desnecessário. Quando um novo sucessor entra, não há itens que são
		# transferidos de um antecessor para ele. Cada nó só administra itens
		# MENORES que ele mesmo.

	# FUNCOES DE PROCESSO
	def processSTORE(self, cmd):
		self.assert_comando(cmd, "STORE")
		
		if self.responsavel_pela_resposta(cmd):
			chave_a_armazenar = cmd[1]
			valor_a_armazenar = cmd[2]
			ip_solicitante = cmd[3]
			porta_solicitante = cmd[4]
			resposta = self.armazenamento.store(chave_a_armazenar, valor_a_armazenar)
			self.enviaResposta("OK", resposta, ip_solicitante, porta_solicitante)
			# Temos que avisar o solicitante que o armazenamento ocorreu?
		else:
			self.encaminhaSucessor(cmd)


	def processRETRIEVE(self, cmd):
		self.assert_comando(cmd, "RETRIEVE")
		
		if self.responsavel_pela_resposta(cmd):
			chave_a_recuperar = cmd[1]
			ip_solicitante = cmd[2]
			porta_solicitante = cmd[3]
			
			resposta = self.armazenamento.retrieve(chave_a_recuperar)
			self.enviaResposta("OK", resposta, ip_solicitante, porta_solicitante)
		else:
			self.encaminhaSucessor(cmd)

	def processREMOVE(self, cmd):
		self.assert_comando(cmd, "REMOVE")
		
		if self.responsavel_pela_resposta(cmd):
			chave_a_remover = cmd[1]
			ip_solicitante = cmd[2]
			porta_solicitante = cmd[3]
			resposta = self.armazenamento.remove(chave_a_remover);	
			self.enviaResposta("OK", resposta, ip_solicitante, porta_solicitante)	
		else:
			self.encaminhaSucessor(cmd)

	def processTRANSFER(self, cmd):
		self.assert_comando(cmd, "TRANSFER")	

		# O comando transfer não analisa se o alvo é ou não responsável
		# pelas chaves. Assume-se que o nó que transfere os arquivos está
		# enviando os dados ao nó correto.
		chave_a_armazenar = cmd[1]
		valor_a_armazenar = cmd[2]
		ip_solicitante = cmd[3]
		porta_solicitante = cmd[4]
		self.armazenamento.store(chave_a_armazenar, valor_a_armazenar);
		self.enviaResposta("TRANSFER_OK", chave_a_armazenar, ip_solicitante, porta_solicitante)
		
	def processTRANSFER_OK(self, cmd):
		# O comando TRANSFER_OK só é recebido após uma requisição de TRANSFER
		# ser enviada, por isso não se checa se o receptor é ou não responsável
		# pela chave.
		self.assert_comando(cmd[0], "TRANSFER_OK")	
		self.armazenamento.remove(cmd[1])

		
	
	
	# FUNCOES AUXILIARES ==================================================

	def assert_comando(self, cmd, comando_esperado):
		if not (cmd[0] == comando_esperado):
			raise Exception(
				"Process {} deve receber um cmd '{}', foi recebido {}\n".format(
					comando_esperado, comando_esperado, cmd[0]))

	def responsavel_pela_chave(self, chave):
		hash_proprio = self.hash_proprio
		hash_predecessor = self.hash_de(self.predecessor[0])
		hash_sucessor = self.hash_de(self.sucessor[0])	
		hash_chave = self.hash_de(chave)
		
		predecessor_menor_que_self = hash_predecessor < hash_proprio
		chave_menor_que_self = hash_chave < hash_proprio
		chave_maior_que_antecessor = hash_chave > hash_antecessor

		if hash_predecessor == hash_proprio and hash_sucessor == hash_proprio:
			# Só há um nó na rede.
			True
		if not predecessor_menor_que_self: 
			# deu a volta
			return chave_maior_que_antecessor or chave_menor_que_self
		else:
			return chave_maior_que_antecessor and chave_menor_que_self
	
	def responsavel_pela_resposta(self, cmd):
		return self.responsavel_pela_chave(cmd[1])

	def encaminhaSucessor(self, cmd):
		lista = list(cmd)
		msg = ' '.join(str(i) for i in lista)+" \n"
		print("Encaminhando: {}\n".format(msg))
		
		#TODO: Enviar para o sucessor.
		try:
			self.sendSocket = socket.socket()
			self.sendSocket.connect((self.sucessor[1], self.sucessor[2]))
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()
		except Exception as err:
			error_msg = "Não foi possível encaminhar uma resposta ao sucessor de {}\n".format(id)
			solicitante = self.obtem_solicitante(cmd)
			self.enviaResposta("ERROR", error_msg, solicitante[0], solicitante[1])
		return msg

	def enviaResposta(self, tipo_resp, conteudo, ip_solicitante, porta_solicitante):
		msg = (tipo_resp, conteudo)
		lista = list(msg)
		msg = ' '.join(str(i) for i in lista)+" \n"
		
		print("Encaminhando: {}\n".format(msg))
		
		# TODO: Enviar para ip_solicitante, porta_solicitante.
		try:
			self.sendSocket = socket.socket()
			self.sendSocket.connect((ip_solicitante, porta_solicitante))
			self.sendSocket.send(msg.encode())
			self.sendSocket.close()
		except Exception as err:
			if tipo_resp == "ERROR":
				print(err)
			else:
				error_msg = "Não foi possível encaminhar uma resposta ao sucessor de {}\n".format(id)
				self.enviaResposta("ERROR", error_msg, ip_solicitante, porta_solicitante)
		return msg
		
	def decode_mensagem_recebida(self, texto):
		#print("Decodificando: {}".format(texto))
		cmd = texto.split(" ")
		tipo = cmd[0]
		if (tipo=="JOIN" or tipo=="JOIN_OK" or tipo=="LEAVE" or tipo=="NODE_GONE" or
			tipo=="NEW_NODE"):
			return cmd

		elif (tipo=="REMOVE" or tipo=="RETRIEVE"):
			return cmd

		elif(tipo=="STORE" or tipo=="TRANSFER" or tipo=="TRANSFER_OK"):
			
			resposta = (cmd[0],)
			dados_usuario = re.split("({.*?})",texto)[1]
			chave = cmd[1]
			endereco = re.split("({.*?})",texto)[2].split(" ")
			ip = endereco[1]
			porta = endereco[2]

			return resposta + (chave, dados_usuario, ip, porta)
			
		elif(tipo=="OK"):
			resposta = (cmd[0],)
			dados_usuario = re.split("({.*?})",texto)[1]
			endereco = re.split("({.*?})",texto)[2].split(" ")
			ip = endereco[1]
			porta = endereco[2]
			return resposta + (dados_usuario, ip, porta)
		return ("ERRO", "Não foi possível interpretar a mensagem recebida.")
		
	def aguardaResposta(self):
		#TODO: Aguarda resposta
		# resposta = ...(algo recebido pela rede, no formato acima: tupla (tipo, conteudo)
		# Sempre que o cliente envia uma solicitação que exige resposta para a rede, por exemplo,
		# quando ele pede para recuperar alguma chave, ele chama essa função. A resposta será enviada
		# usando a função enviaResposta, e terá formato, +- assim ("OK", conteudo), ou ("ERRO", msg erro)
		# Essa resposta será interpretada pela função que iniciou o contato, e exibida no navegador do
		# usuário.

		# Exemplo: 
		# 	1) usuario clica em localizar "andre".
		# 	2) No main.py, será chamado dhtRepo.retrieve("andre")
		#	3a) Se a função precisar consultar a rede:
		# 	 		3.1) enviará uma mensagem ao sucessor 
		# 			3.2) aguardará a resposta
		#	4) Ao receber a resposta, irá retornar, main.py receberá as informações e exibirá no navegador.

		return reposta
	
	def obtem_solicitante(self, cmd):
		if cmd[0]=="STORE" or cmd[0]=="TRANSFER":
			return (cmd[3], cmd[4])
		if cmd[0]=="RETRIEVE" or cmd[0]=="REMOVE":
			return (cmd[2], cmd[3])
		else:
			return (self.addr, self.port)


if __name__ == "__main__":
	#Para executar como main e necessario o seguinte comando
	#python dhtfirst.py [porta] [id]
	hosts = [('127.0.0.1', 7001)]
	d = Dht()
	d.join(hosts, int(sys.argv[1]), int(sys.argv[2]))

