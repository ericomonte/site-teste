import os

import datetime
import gspread
import pandas as pd
import requests

from flask import Flask, request
from haversine import haversine
from oauth2client.service_account import ServiceAccountCredentials
from unidecode import unidecode

TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
TELEGRAM_ADMIN_ID = os.environ["TELEGRAM_ADMIN_ID"]
GOOGLE_SHEETS_CREDENTIALS = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
with open("credenciais.json", mode="w") as arquivo:
  arquivo.write(GOOGLE_SHEETS_CREDENTIALS)
conta = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")
api = gspread.authorize(conta) # sheets.new
planilha = api.open_by_key("1RAvxiZG3f-WhfnX2I7XgyB6TKhyVxuJT5vVAMzO45_U")
sheet_municipios = planilha.worksheet("municipios")
sheet = planilha.worksheet("updates")

app = Flask(__name__)













menu = """
<a href="/">Página inicial</a>  | <a href="/promocoes">PROMOÇÕES</a> |  <a href="/sobre">Sobre</a>  | <a href="/contato">Contato</a><br>
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


@app.route("/dedoduro")
def dedoduro():
  mensagem = {"chat_id": TELEGRAM_ADMIN_ID, "text": "Alguém acessou a página dedo duro!"}
  resposta = requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage", data=mensagem)
  return f"Mensagem enviada. Resposta ({resposta.status_code}): {resposta.text}"
  
@app.route("/dedoduro2")
def dedoduro2():
  sheet.append_row(["Érico", "Monte", "a partir do Flask"])
  return "Planilha escrita!"

@app.route("/telegram-bot")
def telegram_bot():
  update = request.json
  message = update["message"]["text"]
  chat_id = update["message"]["chat"]["id"]
  nova_mensagem = {"chat_id": chat_id, "text": message}
  requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
  return "ok"


