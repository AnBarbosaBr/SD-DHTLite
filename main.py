from flask import Flask, request, render_template
from jinja2 import Template
import sys
from dhtFirst import Dht
import dhtApi
import argparse

app = Flask(__name__)

default_address = '0.0.0.0/9000'

parser = argparse.ArgumentParser()
parser.add_argument("--port", 
										help="Server port",
										type=int, 
										default=9000)
args = parser.parse_args()
port = args.port

# Criamos uma instância do adaptador da API:
dhtRepo = dhtApi.FakeApi()
dhtRepo.join(["endereco ficticio de servidor 1", "end fic 2", "end fic 3"])

usuarios = {}
conectado = False

dht = Dht()

def render_home():
	estou_conectado = dht.conectado
	my_ip=dht.addr
	my_porta=dht.port
	suc_ip  = "Nao definido."
	pred_ip = "Nao definido."
	suc_port = "Nao definida"
	pred_port = "Nao definida"
	if dht.predecessor:
		suc_ip=dht.sucessor[1]
		suc_port=dht.sucessor[2]
	if dht.sucessor:
		pred_ip=dht.predecessor[1]
		pred_port=dht.predecessor[2]

	return render_template('home.html', conectado=estou_conectado, 
								ip=my_ip, 
								porta=str(my_porta),
								ip_suc=suc_ip,
								ip_pred=pred_ip,
								porta_suc=str(suc_port),
								porta_pred=str(pred_port))

@app.route("/", methods=['GET'])
def root():
	return render_home()

@app.route("/connect", methods=['POST'])
def connect():
	if request.method == 'POST':
		try:
			dht.conectado = False
			ip = request.form['ip']
			port = request.form['port']
			ip_target = request.form['ip_target']
			port_target = request.form['port_target']
			print(ip, port, ip_target, port_target)
			hosts = [(ip_target, int(port_target))]
			## Incluindo chamado à API.
			dht.join(hosts, int(port))
			dhtRepo.join([str(ip)+str(port)])
			conectado = True
			#conectar com o node do ip e port indicados
			#else
		except Exception as err:
			print(err)
		
		return render_home()	
		

@app.route("/dc", methods=['GET'])
def dc():
	## Incluindo chamado à API.
	dht.leave()
	#metodo de desconectar do node
	conectado = False
	return render_home()

@app.route("/add", methods=['GET','POST'])
def add():
	try:
		username = request.form['usuario']
		name = request.form['nome']
		email = request.form['email']
		
		
		#Incluído chamado à API.
		#dhtRepo.store(username, {'nome':name , 'email': email})
		dht.store(username,  {'nome':name , 'email': email})
#   usuarios[username] = {
#     'nome' : name,
#     'email': email
#   }
#   print(usuarios)
		#print(dhtRepo.usuarios)
		s_m = ["{} adicionado com sucesso".format(username)]


		#metodo de adicionar contato na rede
		return render_template('sucess.html', success_message=s_m)

	except Exception as err:
		 return render_template('failure.html', failure_message=str(err))

@app.route("/delete", methods=['POST'])
def delete():
	try:
		username = request.form['usuario']
		
		#if username not in usuarios:
		# raise Exception("Nome de usuario não cadastrado")
		#del usuarios[username]
				
		
	#	if not dhtRepo.remove(username):
		if not dht.remove(username):
			raise Exception("Nome de usuario não cadastrado") 
		
		s_m = ["{} apagado com sucesso".format(username)]
		#metodo de deletar contato da rede
		return render_template('sucess.html', success_message=s_m)
	except Exception as err:
		 return render_template('failure.html', failure_message=str(err))

@app.route("/search", methods=['POST'])
def search():
	try:
		username = request.form['usuario']
		
#   if username not in usuarios:
		#usuarioEncontrado = dhtRepo.retrieve(username)
		usuarioEncontrado = dht.retrieve(username)
		if not usuarioEncontrado:
			raise Exception("Nome de usuario não cadastrado")
		#name = usuarios[username]['nome']
		#email = usuarios[username]['email']
		name = usuarioEncontrado['nome']
		email = usuarioEncontrado['email']
		
		s_m = ['Usuario: ' + username, "Nome: " + name, "Email: " + email]
		return render_template('sucess_search.html', username=username, nome=name, email=email)
	except Exception as err:
		 return render_template('failure.html', failure_message=str(err))

	#metodo de buscar pelo username
	

#@app.route("")

if __name__ == "__main__":
	app.run(host='127.0.0.1', port=port)
