# coding:utf-8
import abc
import hashlib
	
class DhtApi(object):

	def hash_de(self, chave):
		"""
		Converte a chave dada num hash sha1, utiliza apenas os primeiros 5
		valores e converte o hexadecimal restante num int. Dispersão do Hash: 16^5
		"""
		print("Recebendo chave {}\n".format(chave))
		hash_longo = hashlib.sha1(str(chave).encode('utf-8')).hexdigest()
		hash_curto = hash_longo[:5]
		return int(hash_curto, 16)

	
	def join(self, listaDePossiveisHosts):
		pass
		
	def leave(self):
		pass
		
		
	def store(self, chave, valor):
		pass
	
	def retrieve(self, chave):
		pass
		
	def remove(self, chave):
		pass	
		

class FakeApi(DhtApi):	
	
	def __init__(self):
		self.usuarios = {};
		self.conectado = False;
		self.sucessor = None;
		self.predecessor = None;
		
	def join(self, listaDePossiveisHosts):
		self.conectado = True
		return self.conectado
	
	def leave(self):
		self.usuarios  = {};
		self.conectado = False;
		return True;
		
	def store(self, chave, valor):
		if(self.conectado):
			self.usuarios[chave] = valor
		else:
			raise Exception("Você não está conectado.");
			
	def retrieve(self, chave):
		if(self.conectado):
			if(len(self.usuarios)>0):
				return self.usuarios[chave];
			else:
				return None;
		else:
			raise Exception("Você não está conectado.");
	
	def remove(self, chave):
		if chave not in self.usuarios:
			return False;
		else:
			del self.usuarios[chave]
			return True;

	def __enderecos_validos(self, lista_de_enderecos):
		if len(lista_de_enderecos) == 0:
			return False;
		
		for endereco in lista_de_enderecos:
			if not isinstance(endereco, tuple):
				return False;
			if not isinstance(endereco[0], str):
				return False;
			if not isinstance(endereco[1], int):
				return False;
		return True;		



class ArmazenamentoLocal(object):	
	
	def __init__(self):
		self.usuarios = {}

	def store(self, chave, valor):
		overwrite = False
		if chave in self.usuarios:
			overwrite = True
		self.usuarios[chave] = valor
		return overwrite
		
			
	def retrieve(self, chave):
		if chave in self.usuarios:
			return self.usuarios[chave];
		else:
			return None;
		
	def remove(self, chave):
		if chave not in self.usuarios:
			return False;
		else:
			del self.usuarios[chave]
			return True;