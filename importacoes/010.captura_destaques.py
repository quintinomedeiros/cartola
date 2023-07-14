import requests
import pandas as pd
import openpyxl
import datetime


def obter_dados_api(url, arquivo_excel):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Gera uma exceção se ocorrer um erro na requisição
        data = response.json()

        # Criar uma nova lista com os dados ajustados
        dados_ajustados = []
        for item in data:
            atleta = item.get('Atleta', {})
            if atleta:
                dados_ajustados.append({
                    'atleta_id': atleta.get('atleta_id'),
                    'atleta_apelido': atleta.get('apelido'),
                    'posicao_abreviacao': item.get('posicao_abreviacao'),
                    'time_abreviacao': item.get('clube'),
                    'time_id': item.get('clube_id'),
                    'escalacoes': item.get('escalacoes'),
                    'preco_editorial': atleta.get('preco_editorial')
                })

        # Criar o DataFrame com os dados ajustados
        df_clubes = pd.DataFrame(dados_ajustados, columns=['atleta_id', 'atleta_apelido', 'posicao_abreviacao',
                                                           'time_abreviacao', 'time_id', 'escalacoes', 'preco_editorial'])

        # Salvar os dados no arquivo Excel
        df_clubes.to_excel(arquivo_excel, sheet_name='Dados', index=False)
    except requests.exceptions.RequestException as e:
        print('Erro ao obter os dados da API:', str(e))


ref = 'api.cartolafc.globo.com/mercado/destaques'
url = f'https://{ref}'

agora = datetime.datetime.now()
momento_geracao = agora.strftime('%Y%m%d%H%M%S')
nome_arquivo = f'dados_destaque_{momento_geracao}.xlsx'

obter_dados_api(url, nome_arquivo)
