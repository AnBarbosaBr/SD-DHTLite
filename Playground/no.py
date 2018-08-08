class No(object):
    
    def __init__(self, identificador, antecessor, sucessor):
        self.identificador = identificador
        self.antecessor = antecessor
        self.sucessor = sucessor

    def _changeSucessor(self, id, endereco):
        raise NotImplementedError
    def _changeAntecesessor(self, id, endereco):
        raise NotImplementedError
        
    def ReceiveMessage(self, message):
        raise NotImplementedError
        
    def SendMessageAntecessor(self, type, id, endereco):
    def SendMessageSucessor(self, type, id, endereco):
        raise NotImplementedError
    def ProcessJoin(self, idEntrando, enderecoEntrando):
        if(idEntrando > self.antecessor.identifcador and idEntrando < self.identifcador):
            self.SendMessageAntecessor("ChangeSucessor" ,idEntrando, enderecoEntrando) # A ordem importa
            self.ChangeAntecessor(idEntrando, enderecoEntrando) # A ordem importa. 
        else if(idEntrando > self.identificador):
            self.SendMessageSucessor("ProcessJoin", idEntrando, enderecoEntrando)
        else if (idEntrando < self.identificador):
            self.SendMessageAntecessor("ProcessJoin", idEntrando, enderecoEntrando)

    def ProcessChangeAntecedor(self, idEntrando, enderecoEntrando):
        raise NotImplementedError
    def ProcessChangeSucessor(self, idEntrando, enderecoEntrando):
        raise NotImplementedError
        
    def Store(self, hash, conteudo): #o conteudo pode ser uma array de bytes
        if(hash > self.antecessor.identificador and hash < self.identificador): # extrair esse if para uma função.
            self._storeHere(hash, conteudo)
        else:
            SendMessageSucessor("Store", hash, conteudo)
    
    def _storeHere(self, hash, conteudo):
        raise NotImplementedError
        
    def _retrieveFromHere(self, hash):
        raise NotImplementedError
    
    def ProcessRetrieve(self, hash, solicitante): # Retorna o conteudo armazenado or Store
        raise NotImplementedError
      
    def ProcessTransfer(self, no, hash): # REDEFINIR
        raise NotImplementedError
    
    