from flask import Flask

app = Flask(__name__)

menu = """
<a href="/">Página inicial</a>  | <a href="/sobre">Sobre</a>  | <a href="/contato">Contato</a>
"""

@app.route("/")
def hello_world():
  return menu + "Olá, mundo! Esse é meu site. (Érico Monte)"

@app.route("/sobre")
def sobre():
  return menu + "Aqui vai o conteúdo da página sobre"

@app.route("/contato")
def contato():
  return menu + "Aqui vai o conteúdo da página contato"
