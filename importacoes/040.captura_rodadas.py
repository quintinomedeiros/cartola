import requests
import pandas as pd

ref = 'api.cartolafc.globo.com/rodadas'

url = f'https://{ref}'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print('Erro ao obter os dados da API: {}'.format(response.text))

df_rodadas = pd.json_normalize(data)

# Obter a data atual
data_atual = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")

# Gerar o nome do arquivo com o momento da criação
nome_arquivo = f'dados_rodadas_{data_atual}.xlsx'

# Salvar o DataFrame como um arquivo Excel
df_rodadas.to_excel(nome_arquivo, index=False)
