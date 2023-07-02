import requests
import pandas as pd
import pandas.io.formats.style

ref = 'api.cartolafc.globo.com/clubes'

url = f'https://{ref}'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print('Erro ao obter os dados da API: {}'.format(response.text))

df_clubes = pd.DataFrame(data)
pandas.io.formats.style.display_dataframe(df_clubes)
