# coding=utf-8
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
conectado = [False]

dht = Dht()

@app.route("/", methods=['GET'])
def root():
	ip_pred = ""
	porta_pred = ""
	ip_suc = ""
	porta_suc = ""
	ip = "127.0.0.1"
	port = 0
	id_mine = 0
	id_pred = 0
	id_suc = 0
	if conectado[0]:
		 ip = dht.addr
		 port = str(dht.port)
		 id_mine = str(dht.id)
		 ip_pred=dht.predecessor[1]
		 porta_pred=str(dht.predecessor[2])
		 id_pred = str(dht.predecessor[0])
		 ip_suc=dht.sucessor[1]
		 porta_suc=str(dht.sucessor[2])
		 id_suc = str(dht.predecessor[0])

	return render_template('home.html', conectado=conectado[0],
		porta=port, ip=ip,
		ip_pred=ip_pred, porta_pred=porta_pred,
		ip_suc=ip_suc, porta_suc=porta_suc,
		id_mine=id_mine, id_pred=id_pred, id_suc=id_suc)

@app.route("/connect", methods=['GET', 'POST'])
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
			conectado[0] = True
			#conectar com o node do ip e port indicados
			#else
			#conectar com o endereço default
			return render_template('home.html', conectado=True, 
																			ip=ip,
																			porta=port,
																			ip_pred=dht.predecessor[1],
																			porta_pred=str(dht.predecessor[2]),
																			ip_suc=dht.sucessor[1],
																			porta_suc=str(dht.sucessor[2]),
																			id_mine = str(dht.id),
																			id_pred = str(dht.predecessor[0]),
																			id_suc = str(dht.predecessor[0]))

		except Exception as err:
			print(err)
			return render_template('home.html', conectado=False)
		

@app.route("/dc", methods=['GET'])
def dc():
	## Incluindo chamado à API.
	dht.leave()
	dhtRepo.leave()
	#metodo de desconectar do node
	conectado[0] = False
	return render_template('home.html', conectado=conectado[0])

@app.route("/add", methods=['GET','POST'])
def add():
	try:
		username = request.form['usuario']
		name = request.form['nome']
		email = request.form['email']
		
		
		#Incluído chamado à API.
		dhtRepo.store(username, {'nome':name , 'email': email})
		
#   usuarios[username] = {
#     'nome' : name,
#     'email': email
#   }
#   print(usuarios)
		print(dhtRepo.usuarios)
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
				
		
		if not dhtRepo.remove(username):
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
		usuarioEncontrado = dhtRepo.retrieve(username)
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
	app.run(host='0.0.0.0', port=port)
