import os

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
api = gspread.authorize(conta)
planilha = api.open_by_key("1RAvxiZG3f-WhfnX2I7XgyB6TKhyVxuJT5vVAMzO45_U")
sheet = planilha.worksheet("municipios")
app = Flask(__name__)

@app.route("/telegram-bot", methods=["POST"])
def telegram_bot():
  update = request.json
  chat_id = update["message"]["chat"]["id"]
  message = update["message"]["text"]

  
  if message in ("/start", "oi", "Olá", "ola", "Ola", "Oi", "Olá!", "olá", "Oi!", "Bom dia", "Boa tarde", "Boa noite" "Opa", "Opa!", "opa", "oi!"):
    texto_resposta = "Olá! Seja bem-vinda(o). Se você chegou aqui está preocupado com o avanço dos incêndios florestais. Envie o nome de sua cidade para saber se está próximo a focos de incêndio:"
  
  else:
    # recebe a cidade pelo bot do telegram retira acentos e transforma em caixa baixa
    message = unidecode(message)
    message = message.lower()
    
    # procura a cidade na planilha do sheets onde consta a base de municipios do IBGE + respectivas coordenadas de latitude e longitude
    cell = sheet.find(message)
    
    # obtém as coordenadas da célula encontrada e caprura os dados nas colunas à direita
    row = cell.row
    col = cell.col
    latitude = sheet.cell(row, col+1).value
    longitude = sheet.cell(row, col+2).value
    message_coord = (float(latitude), float(longitude))
    
    # acessa a api do Programa Queimadas do INPE com os dados de novos focos de incêndio nas últimas 48h
    inpe_focos48h_url = 'https://queimadas.dgi.inpe.br/home/download?id=focos_brasil&time=48h&outputFormat=csv&utm_source=landing-page&utm_medium=landing-page&utm_campaign=dados-abertos&utm_content=focos_brasil_48h'
    foco_atual = pd.read_csv(inpe_focos48h_url)
    
    # padroniza em caixa alta e remove acentos
    foco_atual['municipio'] = [x.upper() for x in foco_atual['municipio']]
    foco_atual['nome'] = foco_atual['municipio'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    
    # captura as cordenadas dos focos na base do INPE, cruza com as coordenadas da cidade indicada pelo usuário, calculando a distância entre os pontos. Seleciona a menor distância e retorna o valor.
    coordenadas = []
    distancia = []
    for x, y in zip(foco_atual.latitude.values, foco_atual.longitude.values):
      lat_long = (x,y)
      coordenadas.append(lat_long)
    for n in coordenadas:
      km = haversine(message_coord, n)
      distancia.append(km)
    foco_atual['distancia_km'] = distancia
    foco_incendio = int(foco_atual['distancia_km'].min())
    
    texto_resposta = (f"O foco de incêndio mais próximo, detectado pelo Inpe nas últimas 48h, encontra-se a {foco_incendio}km de você.")
    
    #else:
      #texto_resposta = "Olá, não entendi o que você quis dizer. Se você chegou aqui está preocupado com o avanço dos incêndios florestais. Envie o nome de sua cidade para saber se está próximo a focos de incêndio:"
  
  nova_mensagem = {
    "chat_id": chat_id,
    "text": texto_resposta,
    "parse_mode": "HTML",
  }  
  
  resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
  print(resposta.text)
  return "ok"



menu = """
<a href="/">Página inicial</a> | <a href="/sobre">Sobre</a> | <a href="/contato">Contato</a>
<br>
"""

@app.route("/")
def index():
  return menu + "Olá, mundo! Esse é meu site. (Érico Monte)"


@app.route("/dedoduro")
def dedoduro():
  mensagem = {"chat_id": TELEGRAM_ADMIN_ID, "text": "Alguém acessou a página dedo duro!"}
  resposta = requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage", data=mensagem)
  return f"Mensagem enviada. Resposta ({resposta.status_code}): {resposta.text}"


@app.route("/dedoduro2")
def dedoduro2():
  sheet.append_row(["xx", "xx", "a partir do Flask"])
  return "Planilha escrita!"
