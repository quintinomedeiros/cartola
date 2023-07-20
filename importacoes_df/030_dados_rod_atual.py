import pandas as pd
import requests
from datetime import datetime

# Faz a requisição para a API
url = 'https://api.cartola.globo.com/atletas/mercado'
response = requests.get(url)
data_atletas = response.json()

# Converte os dados em um DataFrame do pandas
df_atletas = pd.DataFrame(data_atletas['atletas'])

# Desmembrar o campo "scout"
df_scout = pd.json_normalize(df_atletas['scout'])
df_scout.columns = 'sc_' + df_scout.columns

# Desmembrar o campo "gato_mestre"
df_gato_mestre = pd.json_normalize(df_atletas['gato_mestre'])
df_gato_mestre.columns = 'gm_' + df_gato_mestre.columns

# Concatenar os DataFrames resultantes
df_atletas = pd.concat([df_atletas, df_scout, df_gato_mestre], axis=1)

# Remover as colunas scout e gato_mestre com as listas originais
df_atletas = df_atletas.drop(['scout', 'gato_mestre'], axis=1)

# Remover as colunas slug, apelido_abreviado, nome e foto
df_atletas = df_atletas.drop(['slug', 'apelido_abreviado', 'nome', 'foto'], axis=1)

# Renomear a coluna apelido para atleta_apelido
df_atletas = df_atletas.rename(columns={'apelido': 'atleta_apelido', 'clube_id': 'time_id'})

# Reordenar as colunas
colunas = ['atleta_id', 'atleta_apelido', 'rodada_id', 'time_id'] + [coluna for coluna in df_atletas.columns if coluna not in ['atleta_id', 'atleta_apelido', 'rodada_id', 'time_id']]
df_atletas = df_atletas.reindex(columns=colunas)

# Preenchimento de campos ausentes
df_atletas.fillna(value=0, inplace=True)  # Substitui campos ausentes por 0. Altere o valor conforme a estratégia desejada.

# Conversão de valores numéricos
df_atletas = df_atletas.applymap(lambda x: x.replace(',', '.') if isinstance(x, str) else x)  # Substitui vírgula por ponto nos valores numéricos
numeric_columns = ['pontos_num', 'preco_num', 'variacao_num', 'media_num', 'jogos_num', 'minimo_para_valorizar']
df_atletas[numeric_columns] = df_atletas[numeric_columns].astype(float)

# Obter os destaques
url_destaque = 'https://api.cartola.globo.com/mercado/destaques'
response = requests.get(url_destaque)
data_destaque = response.json()

if data_destaque:
    # Criar um dicionário com os IDs dos atletas em destaque e o total de escalações
    destaques_info = {item['Atleta']['atleta_id']: item['escalacoes'] for item in data_destaque}

    # Adicionar as colunas "atleta_dest" e "atleta_esc" ao DataFrame dos atletas atuais
    df_atletas['atleta_dest'] = df_atletas['atleta_id'].apply(lambda x: True if x in destaques_info else False)
    df_atletas['atleta_esc'] = df_atletas['atleta_id'].map(destaques_info).fillna(0).astype(int)

    # Ordenar o DataFrame pelos atletas mais escalados
    df_atletas = df_atletas.sort_values(by='atleta_esc', ascending=False)

    # Obter o momento de gravação do arquivo
    agora = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Nomear o arquivo com o momento de gravação
    nome_arquivo = f'dados_mercado_{agora}.xlsx'

    # Exportar o DataFrame para o arquivo Excel
    df_atletas.to_excel(nome_arquivo, index=False)

    print("Dados dos atletas foram obtidos, as colunas 'atleta_dest' e 'atleta_esc' foram adicionadas e o DataFrame foi ordenado pelo número de escalações.")
else:
    print("Não foi possível obter os dados dos destaques.")
