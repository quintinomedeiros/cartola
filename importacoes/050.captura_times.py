import pandas as pd
import requests
from datetime import datetime

# Obter os dados dos clubes
url_clubes = 'https://api.cartolafc.globo.com/clubes'
resposta_clubes = requests.get(url_clubes)
clubes = resposta_clubes.json()

# Criar DataFrame com os dados dos clubes
dados_times = []
for clube in clubes.values():
    dados_times.append([
        clube['escudos']['60x60'],
        clube['escudos']['45x45'],
        clube['escudos']['30x30'],
        clube['nome'],
        clube['abreviacao'],
        clube['slug'],
        clube['apelido'],
        clube['nome_fantasia'],
        clube['id'],
        clube['url_editoria']
    ])

colunas = ['time_escudo_60x60', 'time_escudo_45x45', 'time_escudo_30x30', 'time_nome', 'time_abreviacao', 'time_slug', 'time_apelido', 'time_nome_fantasia', 'time_id', 'time_url_editorial']
df_times = pd.DataFrame(dados_times, columns=colunas)

# Ordenar as colunas na ordem desejada
ordem_colunas = ['time_id', 'time_nome', 'time_abreviacao', 'time_slug', 'time_apelido', 'time_nome_fantasia', 'time_url_editorial', 'time_escudo_60x60', 'time_escudo_45x45', 'time_escudo_30x30']
df_times = df_times[ordem_colunas]

# Obter a data e hora atual
data_hora_atual = datetime.now().strftime("%Y%m%d%H%M%S")

# Gerar o nome do arquivo com o momento da criação
nome_arquivo = f"dados_times_{data_hora_atual}.xlsx"

# Salvar o DataFrame como um arquivo Excel
df_times.to_excel(nome_arquivo, index=False)
