import pandas as pd
import requests
from datetime import datetime

# Faz a requisição para a API
url = 'https://api.cartola.globo.com/atletas/mercado'
response = requests.get(url)
data = response.json()

# Converte os dados em um DataFrame do pandas
df = pd.DataFrame(data['atletas'])

# Desmembrar o campo "scout"
df_scout = pd.json_normalize(df['scout'])
df_scout.columns = 'sc_' + df_scout.columns

# Desmembrar o campo "gato_mestre"
df_gato_mestre = pd.json_normalize(df['gato_mestre'])
df_gato_mestre.columns = 'gm_' + df_gato_mestre.columns

# Concatenar os DataFrames resultantes
df = pd.concat([df, df_scout, df_gato_mestre], axis=1)

# Remover as colunas scout e gato_mestre com as listas originais
df = df.drop(['scout', 'gato_mestre'], axis=1)

# Remover as colunas slug, apelido_abreviado, nome e foto
df = df.drop(['slug', 'apelido_abreviado', 'nome', 'foto'], axis=1)

# Renomear a coluna apelido para atleta_apelido
df = df.rename(columns={'apelido': 'atleta_apelido', 'clube_id': 'time_id'})

# Reordenar as colunas
colunas = ['atleta_id', 'atleta_apelido', 'rodada_id', 'time_id'] + [coluna for coluna in df.columns if coluna not in ['atleta_id', 'atleta_apelido', 'rodada_id', 'time_id']]
df = df.reindex(columns=colunas)

# Preenchimento de campos ausentes
df.fillna(value=0, inplace=True)  # Substitui campos ausentes por 0. Altere o valor conforme a estratégia desejada.

# Conversão de valores numéricos
df = df.applymap(lambda x: x.replace(',', '.') if isinstance(x, str) else x)  # Substitui vírgula por ponto nos valores numéricos
numeric_columns = ['pontos_num', 'preco_num', 'variacao_num', 'media_num', 'jogos_num', 'minimo_para_valorizar']
df[numeric_columns] = df[numeric_columns].astype(float)

# Obter o momento de gravação do arquivo
agora = datetime.now().strftime('%Y%m%d_%H%M%S')

# Nomear o arquivo com o momento de gravação
nome_arquivo = f'dados_mercado_{agora}.xlsx'

# Exportar o DataFrame para o arquivo Excel
df.to_excel(nome_arquivo, index=False)
