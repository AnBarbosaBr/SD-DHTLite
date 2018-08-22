from flask import Flask, request, render_template
from jinja2 import Template
import sys
import dhtApi

app = Flask(__name__)

default_address = '0.0.0.0/9000'

# Criamos uma instância do adaptador da API:
dhtRepo = dhtApi.FakeApi();
dhtRepo.join(["endereco ficticio de servidor 1", "end fic 2", "end fic 3"]);

usuarios = {}

@app.route("/", methods=['GET'])
def root():
	return render_template('home.html', conectado=True, 
																			endereco_next_node="ds",
																			endereco_previous_node="da")

@app.route("/connect", methods=['GET', 'POST'])
def connect():
	if request.method == 'POST':
		try:
			ip = request.form['ip']
			port = request.form['port']
			print(ip, port)
			s_m = ["Conectado!"]
			
			## Incluindo chamado à API.
			dhtRepo.join([str(ip)+str(port)]);
			#conectar com o node do ip e port indicados
			#else
			#conectar com o endereço default
			return render_template('sucess.html', success_message=s_m)

		except Exception as err:
		 return render_template('failure.html', failure_message=str(err))
		

@app.route("/dc", methods=['GET'])
def dc():
	## Incluindo chamado à API.
	dhtRepo.leave()
	#metodo de desconectar do node
	return "Desconectado"

@app.route("/add", methods=['GET','POST'])
def add():
	try:
		username = request.form['usuario']
		name = request.form['nome']
		email = request.form['email']
		
		
		#Incluído chamado à API.
		dhtRepo.store(username, {'nome':name , 'email': email})
		
#		usuarios[username] = {
#			'nome' : name,
#			'email': email
#		}
#		print(usuarios)
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
		#	raise Exception("Nome de usuario não cadastrado")
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
		
#		if username not in usuarios:
		usuarioEncontrado = dhtRepo.retrieve(username)
		if not usuarioEncontrado:
			raise Exception("Nome de usuario não cadastrado")
		#name = usuarios[username]['nome']
		#email = usuarios[username]['email']
		name = usuarioEncontrado['nome']
		email = usuarioEncontrado['email']
		
		s_m = ['Usuario: ' + username, "Nome: " + name, "Email: " + email]
		return render_template('sucess.html', success_message=s_m)
	except Exception as err:
		 return render_template('failure.html', failure_message=str(err))

	#metodo de buscar pelo username


#@app.route("")

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=9000)
