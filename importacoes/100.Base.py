import requests
import pandas as pd
import openpyxl

def obter_dados_api(url, arquivo_excel):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Gera uma exceção se ocorrer um erro na requisição
        data = response.json()
        df_clubes = pd.DataFrame(data)
        pd.set_option('display.max_colwidth', 10)
        df_clubes.to_excel(arquivo_excel, sheet_name='Dados')
    except requests.exceptions.RequestException as e:
        print('Erro ao obter os dados da API:', str(e))

ref = 'api.cartolafc.globo.com/mercado/destaques'
url = f'https://{ref}'

obter_dados_api(url, 'dados.xlsx')
