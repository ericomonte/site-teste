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


@app.route("/telegram-bot", methods=["POST"])
def telegram_bot():
  update = request.json
  chat_id = update["message"]["chat"]["id"]
  message = update["message"]["text"]
  nova_mensagem = {"chat_id": chat_id, "text": message}
  requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
                       
  update_id = update["update_id"]
  
  if message == "/start":
    texto_resposta = "Olá! Seja bem-vinda(o). Se você chegou aqui está preocupado com o avanço dos incêndios florestais. Envie o nome de sua cidade para saber se está próximo a focos de incêndio:"
  else:
    cidade_bot = message
    # recebe a cidade pelo bot do telegram
    cidade_bot = unidecode(cidade_bot)
    cidade_bot = cidade_bot.lower()

  try:  
    cell = sheet_municipios.find(cidade_bot)

    # Obter as coordenadas da célula encontrada
    row = cell.row
    col = cell.col

    # Selecionar a célula imediatamente à direita
    latitude = sheet_municipios.cell(row, col+1).value
    longitude = sheet_municipios.cell(row, col+2).value

    cidade_bot_coord = (float(latitude), float(longitude))

    inpe_focos48h_url = 'https://queimadas.dgi.inpe.br/home/download?id=focos_brasil&time=48h&outputFormat=csv&utm_source=landing-page&utm_medium=landing-page&utm_campaign=dados-abertos&utm_content=focos_brasil_48h'
    foco_atual = pd.read_csv(inpe_focos48h_url)

    # Remove algumas colunas
    foco_atual = foco_atual[['latitude', 'longitude',	'estado', 'municipio', 'municipio_id',	'estado_id', 'bioma']]
    # Coloca em maiúsculas
    foco_atual['municipio'] = [x.upper() for x in foco_atual['municipio']]
    # remove acentos
    foco_atual['nome'] = foco_atual['municipio'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    coordenadas = []
    distancia = []
    for x, y in zip(foco_atual.latitude.values, foco_atual.longitude.values):
      lat_long = (x,y)
      coordenadas.append(lat_long)
    for n in coordenadas:
      km = haversine(cidade_bot_coord, n)
      distancia.append(km)
    foco_atual['distancia_km'] = distancia
    foco_incendio = int(foco_atual['distancia_km'].min())
    #print(f'O foco de incêndio mais próximo, detectado pelo Inpe nas últimas 48h, encontra-se a {foco_incendio}km de você.')
    texto_resposta = (f"O foco de incêndio mais próximo, detectado pelo Inpe nas últimas 48h, encontra-se a {foco_incendio}km de você.") 
  
  # Pega na planilha do sheets o último update_id
#update_id = int(sheet.get("A1")[0][0])

update = request.json
chat_id = update["message"]["chat"]["id"]
message = update["message"]["text"]
nova_mensagem = {"chat_id": chat_id, "text": message}
requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)

for x in update:
  update_id = update["update_id"]
  # Extrai dados para mostrar mensagem recebida
  first_name = update["message"]["from"]["first_name"]
  sender_id = update["message"]["from"]["id"]
  if "text" not in update["message"]:
    continue  # Essa mensagem não é um texto!
    message = update["message"]["text"]
    chat_id = update["message"]["chat"]["id"]
    datahora = str(datetime.datetime.fromtimestamp(update["message"]["date"]))
    if "username" in update["message"]["from"]:
      username = update["message"]["from"]["username"]
    else:
      username = "[não definido]"
    print(f"[{datahora}] Nova mensagem de {first_name} @{username} ({chat_id}): {message}")
    mensagens.append([datahora, "recebida", username, first_name, chat_id, message])

  # Define qual será a resposta e envia
    if message == "/start":
      texto_resposta = "Olá! Seja bem-vinda(o). Se você chegou aqui está preocupado com o avanço dos incêndios florestais. Envie o nome de sua cidade para saber se está próximo a focos de incêndio:"
    else:
      cidade_bot = message
      # recebe a cidade pelo bot do telegram
      cidade_bot = unidecode(cidade_bot)
      cidade_bot = cidade_bot.lower()

    try:
      cell = sheet_municipios.find(cidade_bot)

      # Obter as coordenadas da célula encontrada
      row = cell.row
      col = cell.col

      # Selecionar a célula imediatamente à direita
      latitude = sheet_municipios.cell(row, col+1).value
      longitude = sheet_municipios.cell(row, col+2).value

      cidade_bot_coord = (float(latitude), float(longitude))

      inpe_focos48h_url = 'https://queimadas.dgi.inpe.br/home/download?id=focos_brasil&time=48h&outputFormat=csv&utm_source=landing-page&utm_medium=landing-page&utm_campaign=dados-abertos&utm_content=focos_brasil_48h'
      foco_atual = pd.read_csv(inpe_focos48h_url)

      # Remove algumas colunas
      foco_atual = foco_atual[['latitude', 'longitude',	'estado', 'municipio', 'municipio_id',	'estado_id', 'bioma']]
      # Coloca em maiúsculas
      foco_atual['municipio'] = [x.upper() for x in foco_atual['municipio']]
      # remove acentos
      foco_atual['nome'] = foco_atual['municipio'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

      coordenadas = []
      distancia = []
      for x, y in zip(foco_atual.latitude.values, foco_atual.longitude.values):
        lat_long = (x,y)
        coordenadas.append(lat_long)
      for n in coordenadas:
        km = haversine(cidade_bot_coord, n)
        distancia.append(km)
      foco_atual['distancia_km'] = distancia
      foco_incendio = int(foco_atual['distancia_km'].min())
      #print(f'O foco de incêndio mais próximo, detectado pelo Inpe nas últimas 48h, encontra-se a {foco_incendio}km de você.')
      texto_resposta = (f"O foco de incêndio mais próximo, detectado pelo Inpe nas últimas 48h, encontra-se a {foco_incendio}km de você.") 
  
    except gspread.exceptions.CellNotFound:
    # Envia mensagem de erro para o usuário
      texto_resposta = "Desculpe, não foi possível encontrar a cidade que você digitou. Por favor, tente novamente usando o comando /start."

  nova_mensagem = {"chat_id": chat_id, "text": texto_resposta}
  requests.post(f"https://api.telegram.org./bot{token}/sendMessage", data=nova_mensagem)
  mensagens.append([datahora, "enviada", username, first_name, chat_id, texto_resposta])
# Atualiza planilha do sheets com último update processado
sheet.append_rows(mensagens)
sheet.update("A1", update_id)
  nova_mensagem = {"chat_id": chat_id, "text": texto_resposta}
  requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
  sheet.update("A1", update_id)
  return "Ok"

menu = """
<a href="/">Página inicial</a> 
"""

@app.route("/")
def hello_world():
  return menu + "Olá, mundo! Essa é a página do Data Forest bot. As queimadas estão se alastrando pelo país. Vou te ajudar a descobrir quão próximo você está de uma queimada, acessando os dados do INPE."
