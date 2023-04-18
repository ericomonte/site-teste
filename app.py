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
  first_name = update["message"]["from"]["first_name"]
  
  message = unidecode(message)
  message = message.lower()

  if message in ("/start", "start", "oi", "ola", "bom dia", "boa tarde", "boa noite", "opa", 0):
    texto_resposta = f'''Olá! Seja bem-vindo(a), {first_name}. \nEstamos preocupados com o avanço de queimadas no país. Só nas últimas 48h o INPE observou {len(foco_atual)} focos de incêndios florestais \U0001F525.\n\n\U0001F3D8 Digite o nome de sua cidade para saber se você está próximo(a) a focos de incêndio.\n\nOu digite um número abaixo e veja a quantidade de focos em: \n1 - Estados; \n2 - Biomas.'''
    #texto_resposta = f'''Olá! Seja bem-vindo(a), {first_name}. \nSe você chegou aqui, está preocupado(a) com o avanço queimadas. \nSó nas últimas 48h o satélite \U0001F4E1 do INPE observou {len(foco_atual)} focos de incêndios florestais no Brasil. \nEnvie o nome de sua cidade para saber se você está próximo(a) a focos de incêndio \U0001F525:'''
  
  elif message == "1":
    estados = foco_atual['estado'].value_counts().to_dict()
    estados_lista = ''
    for key, value in estados.items():
      estados_lista += f"{key}: {value}\n"
    texto_resposta = f'''Nas últimas 48h o satélite do INPE registrou focos de incêndios florestais nos estados:\n{estados_lista}\n\n Digite 0 para voltar ao menu inicial.'''
   
  elif message == "2":
    texto_resposta = f'''Nas últimas 48h o satélite do INPE registrou {len(foco_atual)} focos de incêndios florestais nos biomas:\n
Amazônia: {len(foco_atual[foco_atual['bioma'].str.contains('Amazônia')])}
Caatinga: {len(foco_atual[foco_atual['bioma'].str.contains('Caatinga')])}
Cerrado: {len(foco_atual[foco_atual['bioma'].str.contains('Cerrado')])}
Mata Atlântica: {len(foco_atual[foco_atual['bioma'].str.contains('Mata Atlântica')])}
Pampa: {len(foco_atual[foco_atual['bioma'].str.contains('Pampa')])}\n\n Digite 0 para voltar ao menu inicial.
'''  
  
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

    texto_resposta = (f"O foco de incêndio mais próximo detectado pelo Inpe, nas últimas 48h, encontra-se a {foco_incendio}km de você. \n\n Digite 0 para voltar ao menu inicial.")
    
  # caso a palavra não seja um município
  else:
    texto_resposta = f"Desculpe, {message} não é uma cidade válida. \n\nEnvie o nome de sua cidade para saber se você está próximo(a) a focos de incêndio. \n\n Ou digite 0 para voltar ao menu inicial."
  
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
