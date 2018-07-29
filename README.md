# SD-DHTLite
Uma implementação simplificada de um sistema DHT com topologia em anel(semelhante ao Chord)

## Lite

Essa implementação deve dar suporte a:
 * Entrada e saída de nós da rede.
 * Inclusão, remoção e pesquisa de pares chave-valor
 

Essa implementação *não* precisa se preocupar com:
 * Nós que falhem ou deixem a rede sem aviso.
 * Nós que tentam se conectar ao mesmo tempo e que deixariam a rede em estado inconsistente(caso ambos tivessem o mesmo sucessor, por exemplo).
 * Implementar todo o protocolo Chord.

## Aplicação
O projeto também deve ter uma aplicação que utiliza o sistema criado, utilizando todo o protocolo definido.

Para esta aplicação optou-se por criar uma _agenda telefônica_.

## Orientações quanto a Implementação:
* Cada nó terá apenas dois ponteiros(não será necessário utilizar a *finger table*)
* Cada nó recebe um identificador aleatório de m-bits
* Cada entidade armazenada recebe uma chave de m-bits
* Entidades com chave k estão sob responsábilidade do nó cujo id seja o menor possível tal que id >= k.

## API
Esse sistema DHT é capaz de:

* *join(known-host-list)*: Para se conectar à DHT. Args: known-host-list é uma lista de nós que provavelmente participam da rede atual. A operação deve testar cada nó para verificar se algum possível participante está ativo. Se estiver, ela se conecta a ele. Senão, ela cria uma nova lista DHT.
* *levae()*: A aplicação se desconecta à DHT. 
* *store(key,value)*: Armazena um dado na rede.
* *retrieve(key)*: Efetua uma busca na DHT e devolve o valor 'value', caso esteja na lista. Retorna um elemento nulo caso o valor não seja localizado.

_*RECOMENDACAO*_: Os values podem ser um vetor de bytes, permitindo o armazenamento de qualquer objeto serializado.

## A Aplicação
É importante que a aplicação utilize todas as operações da API


## Protocolo:
Pode ser utilizado tanto Sockets, quanto Chamadas de Métodos Remotos. É interessante que o protocolo utilizado seja capaz de transmitir as seguintes informações:

* JOIN_OK -> (TODO... completar texto)
* NEW_NODE -> (TODO... completar texto)
* LEAVE -> (TODO... completar texto)
* NODE_GONE -> Quando o nó sair da rede.
* STORE -> Quando for necessário armazenar algum valor.
* RETRIEVE -> Quando for necessário recuperar informações armazenadas.
* OK -> Resposta a RETRIEVE.
* NOT_FOUND -> Quando o arquivo não for encontrado.
* TRANSFER -> Transferir a responsabilidade sobre alguns dados para outro nó.

** JOIN, STORE, RETRIEVE : Mensagens roteadas pelo anel
** JOIN_OK, OK, LEAVE, NEW_NODE, NODE_GONE, TRANSFER, NOT_FOUND enviadas diretamnete para o destinatário, sem passar pelo anel.


# Milestones
[ ] Aplicação que utiliza a API totalmente
[ ] Implementar o anel que pode ser criado e mantido. Não se preocupar com chaves, armazenamento e transferencia de dados.
[ ] Implementar armazenamento e recuperação de objetos da DHT.

