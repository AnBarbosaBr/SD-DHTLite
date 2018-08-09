from flask import Flask, request

app = Flask(__name__, static_url_path='static')

default_address = '0.0.0.0/9000'

@app.route("/", methods=['GET'])
def root():
	return app.send_static_file('index.html')

@app.route("/connect", methods=['GET', 'POST'])
def connect():
	if request.method == 'POST':
		ip = request.form['ip']
		port = request.form['port']
		#conectar com o node do ip e port indicados
	else
		#conectar com o endereço default

	return "Conectado"

@app.route("/dc", method=['GET'])
def dc():
	#metodo de desconectar do node
	return "Desconectado"

@app.route("/add", methods=['POST'])
def add():
	username = request.form['username']
	name = request.form['name']
	email = request.form['email']

	#metodo de adicionar contato na rede
	return "{} adicionado com sucesso".format(username)

@app.route("/delete", methods=['POST'])
def delete():
	username = request.form['username']

	#metodo de deletar contato da rede
	return "{} apagado com sucesso".format(username)

@app.route("/search", methods=['GET'])
def search():
	username = request.form['username']

	#metodo de buscar pelo username

@app.route("")

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8080)