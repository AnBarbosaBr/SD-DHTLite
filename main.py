from flask import Flask, request, render_template
from jinja2 import Template

app = Flask(__name__)

default_address = '0.0.0.0/9000'

@app.route("/", methods=['GET'])
def root():
	return render_template('home.html', conectado=True, 
																			enderco_next_node="",
																			enderco_previous_node="")

@app.route("/connect", methods=['GET', 'POST'])
def connect():
	if request.method == 'POST':
		ip = request.form['ip']
		port = request.form['port']
		print(ip, port)
		#conectar com o node do ip e port indicados
	#else
		#conectar com o endereço default

	return "Conectado"

@app.route("/dc", methods=['GET'])
def dc():
	#metodo de desconectar do node
	return "Desconectado"

@app.route("/add", methods=['GET','POST'])
def add():
	username = request.form['usuario']
	name = request.form['nome']
	email = request.form['email']
	s_m = "{} adicionado com sucesso".format(username)
	print(s_m)

	#metodo de adicionar contato na rede
	return render_template('sucess.html', sucess_message=s_m)

@app.route("/delete", methods=['POST'])
def delete():
	username = request.form['username']

	#metodo de deletar contato da rede
	return "{} apagado com sucesso".format(username)

@app.route("/search", methods=['GET'])
def search():
	username = request.form['username']

	#metodo de buscar pelo username

#@app.route("")

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=9000)