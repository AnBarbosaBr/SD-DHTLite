# coding:utf-8

import unittest
import dhtApi

dht_under_test = dhtApi.FakeApi()
endereco_valido = [("localhost", 40001), ("localhost", 40002), ("localhost", 40003)]
class TestaDHT_Join(unittest.TestCase):
	# def join(self, listaDePossiveisHosts):
	
	def testaJoin_Sucesso(self):
		# Arrange
		lista_entrada = [("localhost", 40001), ("localhost", 40002), ("localhost", 40003)]
		
		# Act
		resposta_obtida = dht_under_test.join(lista_entrada)
		
		# Assert
		self.assertTrue(resposta_obtida, "Não foi possível criar um novo anel.")

	def testaJoin_Falha(self):
		#Arrange
		lista_entrada = [("localhost, 40001")]
		#Act
		resposta_obtida = dht_under_test.join(lista_entrada)
		#Assert
		self.assertFalse(resposta_obtida, "Foi possível conectar com um endereço inválido. {}".format(str(lista_entrada)))

class TestaDHT_Leave(unittest.TestCase):
	# def leave(self):
	def testaLeave(self):
		# Arrange
		# Act
		resposta_saida = dht_under_test.leave();
		# Assert
		self.assertTrue(resposta_saida);

class TestaDHT_Store(unittest.TestCase):
	#def store(self, chave, valor):
	def testaStore_ChaveNova_NaoConectado(self):
		# Arrange
		# Act
		desconectado = dht_under_test.leave();
	
	
		# Assert
		self.assertTrue(desconectado)
		with self.assertRaises(Exception) as excessao_lancada:
			dht_under_test.store("Andre", "sucesso")

	def testaStore_ChaveNova_Conectado(self):
		# Arrange
		conectado = dht_under_test.join(endereco_valido);
		# Act
		dht_under_test.store("Andre", "sucesso");

		# Assert
		self.assertTrue(conectado)
		# DUVIDA: Como verificar que o item realmente está armazenado sem depender da retrieve?

	def testaStore_ChaveExistente_Conectado(self):
		# Arrange
		conectado = dht_under_test.join(endereco_valido);
		# Act
		dht_under_test.store("Andre3", "primeira vez");
		dht_under_test.store("Andre3", "sucesso");
		# Assert
		self.assertTrue(conectado)
		# DUVIDA: Como verificar que o item realmente está armazenado sem depender da retrieve?

	
	
class TestaDHT_Retrieve(unittest.TestCase):
	#def retrieve(self, chave):
	def passa(self):
		pass
		
class TestaDHT_Remove(unittest.TestCase):
	#def remove(self, chave):
	def passa(self):
		pass

