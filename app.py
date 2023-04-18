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
sheet_municipios = planilha.worksheet("municipios")
municipios = sheet_municipios.col_values(2)
# acessa a api do Programa Queimadas do INPE com os dados de novos focos de incêndio nas últimas 48h
inpe_focos48h_url = 'https://queimadas.dgi.inpe.br/home/download?id=focos_brasil&time=48h&outputFormat=csv&utm_source=landing-page&utm_medium=landing-page&utm_campaign=dados-abertos&utm_content=focos_brasil_48h'
foco_atual = pd.read_csv(inpe_focos48h_url)
# remove acentos
foco_atual['nome'] = foco_atual['municipio'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
app = Flask(__name__)

@app.route("/telegram-bot", methods=["POST"])
def telegram_bot():
  update = request.json
  chat_id = update["message"]["chat"]["id"]
  message = update["message"]["text"]
  
  message = unidecode(message)
  message = message.lower()

  if message in ("/start", "start", "oi", "ola", "bom dia", "boa tarde", "boa noite", "opa"):
    texto_resposta = "Olá! Seja bem-vindo(a). Se você chegou aqui está preocupado com o avanço dos incêndios florestais. Envie o nome de sua cidade para saber se você está próximo(a) a focos de incêndio:"
  
  elif message in municipios:
    # procura a cidade na planilha do sheets onde consta a base de municipios do IBGE + respectivas coordenadas de latitude e longitude
    cell = sheet_municipios.find(message)
    # obtém as coordenadas da célula encontrada e caprura os dados nas colunas à direita
    row = cell.row
    col = cell.col
    latitude = sheet_municipios.cell(row, col+1).value
    longitude = sheet_municipios.cell(row, col+2).value
    cidade_bot_coord = (float(latitude), float(longitude))

    # captura as cordenadas dos focos na base do INPE, cruza com as coordenadas da cidade indicada pelo usuário, calculando a distância entre os pontos. Seleciona a menor distância e retorna o valor.
    coordenadas = []
    distancia = []
    for x, y in zip(foco_atual.latitude.values, foco_atual.longitude.values):
      lat_long = (x, y)
      coordenadas.append(lat_long)
    for n in coordenadas:
      km = haversine(cidade_bot_coord, n)
      distancia.append(km)
    foco_atual['distancia_km'] = distancia
    foco_incendio = int(foco_atual['distancia_km'].min())

    texto_resposta = (f"O foco de incêndio mais próximo detectado pelo Inpe, nas últimas 48h, encontra-se a {foco_incendio}km de você.")
  
  elif:
    message == "biomas"
    biomas = foco_atual['bioma'].value_counts()
    texto_resposta = (f'Nas últimas 48h o satéite do INPE registrou focos de incêndios nos biomas:\n{biomas}')
  
  # caso a palavra não seja um município
  else:
    texto_resposta = f"Desculpe, {message} não é uma cidade válida. Envie o nome de sua cidade para saber se você está próximo(a) a focos de incêndio:"
  
  nova_mensagem = {
    "chat_id": chat_id,
    "text": texto_resposta,
    "parse_mode": "HTML",
  }  
  
  resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
  print(resposta.text)
  return "ok"


@app.route("/")
def index():
  return "Olá, mundo! Essa é a página do Data Forest bot. As queimadas estão se alastrando pelo país. Vou te ajudar a descobrir quão próximo você está de uma queimada, acessando os dados do INPE."
