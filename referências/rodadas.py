import pandas as pd
import requests
import json
from datetime import datetime

# Obter a quantidade total de rodadas
url_rodadas = 'https://api.cartolafc.globo.com/pos-rodada/destaques'
resposta_rodadas = requests.request("GET", url_rodadas)
rodadas = json.loads(resposta_rodadas.text)
quantidade_rodadas = len(rodadas)

print(quantidade_rodadas)