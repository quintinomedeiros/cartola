import requests
import pandas as pd

ref = 'api.cartolafc.globo.com/atletas/pontuados'

url = f'https://{ref}'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print('Erro ao obter os dados da API: {}'.format(response.text))

df_atletas = pd.DataFrame(data)
pd.set_option('display.max_colwidth', 10)
print(df_atletas)
