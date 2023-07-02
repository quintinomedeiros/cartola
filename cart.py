import pandas as pd
import requests
import json
from datetime import datetime

# Obter a quantidade total de rodadas
url_rodadas = 'https://api.cartolafc.globo.com/rodadas'
resposta_rodadas = requests.request("GET", url_rodadas)
rodadas = json.loads(resposta_rodadas.text)
quantidade_rodadas = 12

# Criar uma lista vazia para armazenar os DataFrames de cada rodada
dataframes = []

# Iterar sobre as rodadas e buscar a pontuação
for rodada in range(1, quantidade_rodadas + 1):
    url = f'https://api.cartola.globo.com/atletas/pontuados/{rodada}'
    resposta = requests.request("GET", url)
    objetos = json.loads(resposta.text)
    df = pd.json_normalize(objetos['atletas'].values())
    dataframes.append(df)

# Combinar os DataFrames de cada rodada em um único DataFrame
df_combined = pd.concat(dataframes)

# Substituir campos vazios (NaN) por 0
df_combined = df_combined.fillna(0)

# Obter a data e hora atual
data_hora_atual = datetime.now().strftime("%Y%m%d%H%M%S")

# Gerar o nome do arquivo com o momento da criação
nome_arquivo = f"relatorio_cartola_{data_hora_atual}.csv"

# Modificar os valores do campo 'foto' para incluir os links
df_combined['foto'] = '<a href="' + df_combined['foto'] + '">link</a>'

# Salvar o DataFrame como um arquivo CSV
df_combined.to_csv(nome_arquivo, index=False)
