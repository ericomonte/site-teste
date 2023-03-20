from flask import Flask
from tchan import ChannelScraper

app = Flask(__name__)



def ultimas_promocoes():
  scraper = ChannelScraper()
  contador = 0
  resultado = []
  for message in scraper.messages("promocoeseachadinhos"):
    contador += 1
    texto = message.text.strip().splitlines()[0]
    resultado.append(f"{message.created_at} {texto}")
    if contador == 10:
      return resultado

    
menu = """
<a href="/">Página inicial</a>  | <a href="/promocoes">PROMOÇÕES</a> |  <a href="/sobre">Sobre</a>  | <a href="/contato">Contato</a>
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



@app.route("/promocoes")
def promocoes():
  conteudo = menu + """
  Encontrei as seguintes promoções no <a href="https://t.me/promocoeseachadinhos">@promocoeseachadinhos</a>:
  <br>
  <ul>
  """
  for promocao in ultimas_promocoes():
    conteudo += f"<li>{promocao}</li>"
  return conteudo + "</ul>"
