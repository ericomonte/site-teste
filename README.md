# Data Forest Bot #

Bem vindo ao Data Forest, bot criado no Telegram para automatizar o acesso à API de dados de monitoramento de focos de incêndio nas últimas 48 realizado pelo **Instituto Nacional de Pesquisas Espaciais (INPE)**, no seu [Programa Queimadas - Dados Abertos](https://queimadas.dgi.inpe.br/queimadas/dados-abertos).

Se você chegou até aqui, deve estar preocupado com a conservação de nossas florestas e as cada vez mais frequentes queimadas.

O [Data Forest Bot](https://web.telegram.org/k/#@data_forest_bot) acessa os dados do INPE com registros de focos de incêndio nas últimas 48h e calcula quão próximo você está de uma possível queimada. Além de compilar dados de focos de incêndio por estados e por biomas.

### Código

- O arquivo app.py contém código python que:
  - Usa **Flask** para acessar hospedagem em nuvem - **[Render](https://render.com/)**
  - Acessa API do Telegram e lista comandos para o bot
- O arquivo requirements contém as bibliotecas utilizadas
