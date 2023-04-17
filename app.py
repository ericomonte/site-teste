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

app = Flask(__name__)

@app.route("/telegram-bot", methods=["POST"])
def telegram_bot():
  update = request.json
  chat_id = update["message"]["chat"]["id"]
  message = update["message"]["text"]
  nova_mensagem = {
    "chat_id": chat_id,
    "text": f"Você enviou a mensagem: <b>{message}</b>",
    "parse_mode": "HTML",
  }
  # Define qual será a resposta e envia
  if message == "/start":
    texto_resposta = "Olá! Seja bem-vinda(o). Se você chegou aqui está preocupado com o avanço dos incêndios florestais. Envie o nome de sua cidade para saber se está próximo a focos de incêndio:"
  else:
    texto_resposta = "Não entendi."
    nova_mensagem = {"chat_id": chat_id, "text": texto_resposta}
  requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)

  return

menu = """
<a href="/">Página inicial</a> 
"""

@app.route("/")
def hello_world():
  return menu + "Olá, mundo! Essa é a página do Data Forest bot. As queimadas estão se alastrando pelo país. Vou te ajudar a descobrir quão próximo você está de uma queimada, acessando os dados do INPE."
