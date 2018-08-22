
import abc

class DhtApi(object, metaclass=abc.ABCMeta):

	@abc.abstractmethod
	def join(self, listaDePossiveisHosts):
		pass
		
	@abc.abstractmethod
	def leave(self):
		pass
		
		
	@abc.abstractmethod
	def store(self, chave, valor):
		pass
	
	@abc.abstractmethod
	def retrieve(self, chave):
		pass
		
	@abc.abstractmethod
	def remove(self, chave):
		pass	
		

class FakeApi(DhtApi):	
	
	def __init__(self):
		self.usuarios = {};
		self.conectado = False;
		
	def join(self, listaDePossiveisHosts):
		if(len(listaDePossiveisHosts)>0):
			self.conectado = True;
			return True;
		else:
			return False;
	
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
			raise Excetion("Você não está conectado.");
	
	def remove(self, chave):
		if chave not in self.usuarios:
			return False;
		else:
			del self.usuarios[chave]
			return True;

	
