import pandas as pd
import requests
from datetime import datetime

# Função para extrair os valores dos scouts
def get_scout_values(scouts, scout_keys):
    if isinstance(scouts, dict):
        scout_values = {scout: scouts.get(scout, 0) for scout in scout_keys}
        return scout_values
    else:
        return {scout: 0 for scout in scout_keys}
    
# Função para calcular a pontuação ponderada dos scouts
def calcular_pontuacao_scout(atleta_data, scouts_pesos):
    if 'scout' not in atleta_data:
        return 0

    scout_values = get_scout_values(atleta_data['scout'], scouts_pesos.keys())
    pontuacao = sum(scouts_pesos.get(scout, 0) * valor for scout, valor in scout_values.items())
    return pontuacao

# Dicionário com os pesos dos scouts
scouts_pesos = {
    'ds': 1.2, 'fc': -0.3, 'gc': -3.0, 'ca': -1.0, 'cv': -3.0, 'sg': 5.0, 'dp': 7.0, 'gs': -1.0,
    'pc': -1.0, 'fs': 0.5, 'a': 5.0, 'ft': 3.0, 'fd': 1.2, 'ff': 0.8, 'g': 8.0, 'i': -0.1,
    'pp': -4.0, 'ps': 1.0
}

# Função para calcular a pontuação ponderada dos scouts
def calcular_pontuacao_scout(atleta_data, scouts_pesos):
    if 'scout' not in atleta_data:
        return 0

    scout_values = get_scout_values(atleta_data['scout'], scouts_pesos.keys())
    pontuacao = sum(scouts_pesos.get(scout, 0) * valor for scout, valor in scout_values.items())
    return pontuacao

# URL da API do Cartola FC
url_base = 'https://api.cartolafc.globo.com'

# Obter informações das rodadas
url_rodadas = f'{url_base}/rodadas'
resposta_rodadas = requests.get(url_rodadas)
dados_rodadas = resposta_rodadas.json()

# Encontrar a última rodada finalizada
ultima_rodada_finalizada = None
for rodada in dados_rodadas:
    fim_rodada = datetime.strptime(rodada['fim'], "%Y-%m-%d %H:%M:%S")
    if fim_rodada <= datetime.now():
        ultima_rodada_finalizada = rodada['rodada_id']
    else:
        break

# Verificar se encontramos a última rodada finalizada
if ultima_rodada_finalizada is not None:
    print(f"A última rodada finalizada é a {ultima_rodada_finalizada}.")
else:
    print("Nenhuma rodada finalizada encontrada antes da data atual.")

# Lista para armazenar os atributos dos atletas pontuados
atletas_pontuados_dados = []

# Lista para armazenar os atributos das partidas
partidas_dados = []

# Iterar sobre as rodadas finalizadas
for rodada_id in range(1, ultima_rodada_finalizada + 1):
    print(f"Processando rodada {rodada_id}...")
    # Obter informações dos atletas pontuados na rodada
    url_pontuados = f'{url_base}/atletas/pontuados/{rodada_id}'
    resposta_pontuados = requests.get(url_pontuados)
    data_pontuados = resposta_pontuados.json()

    # Verificar se a resposta é válida e se contém os atletas pontuados
    if isinstance(data_pontuados, dict) and 'atletas' in data_pontuados:
        atletas_pontuados = data_pontuados['atletas']
        for atleta_id, atleta_data in atletas_pontuados.items():
            # Verificar se o atleta possui informações de scouts na rodada
            if 'scout' in atleta_data:
                pontuacao_scout = calcular_pontuacao_scout(atleta_data, scouts_pesos)
            else:
                pontuacao_scout = 0

            atleta_pontuado = {
                'atleta_id': int(atleta_id),
                'posicao_id': atleta_data['posicao_id'],
                'clube_id': atleta_data['clube_id'],
                'pontuacao': atleta_data['pontuacao'],
                'entrou_em_campo': atleta_data.get('entrou_em_campo', False),
                'rodada_id': rodada_id,
                'pt_scout': pontuacao_scout,  # Adicionar a pontuação ponderada no DataFrame
                **get_scout_values(atleta_data.get('scout'), scouts_pesos.keys())  # Adicionar os scouts no DataFrame
            }
            atletas_pontuados_dados.append(atleta_pontuado)
    else:
        print(f"Resposta inválida da API de jogadores pontuados na rodada {rodada_id}.")

    # Obter informações das partidas na rodada
    url_partidas = f'{url_base}/partidas/{rodada_id}'
    resposta_partidas = requests.get(url_partidas)
    data_partidas = resposta_partidas.json()
    
    # Verificar se a resposta é válida e se contém as partidas
    if isinstance(data_partidas, dict) and 'partidas' in data_partidas:
        partidas = data_partidas['partidas']
        for partida in partidas:
            partida_data = {
                'partida_id': partida['partida_id'],
                'clube_casa_id': partida['clube_casa_id'],
                'clube_visitante_id': partida['clube_visitante_id'],
                'placar_oficial_mandante': partida['placar_oficial_mandante'],
                'placar_oficial_visitante': partida['placar_oficial_visitante'],
                'rodada_id': rodada_id
            }
            partidas_dados.append(partida_data)
    else:
        print("Resposta inválida da API de partidas.")

# Criar DataFrame com os atributos dos atletas pontuados
df_atletas_pontuados = pd.DataFrame(atletas_pontuados_dados)
df_partidas = pd.DataFrame(partidas_dados)

# Print dos 10 primeiros registros do DataFrame df_atletas_pontuados após importar da API
print("\nPrimeiros 10 registros do DataFrame 'atletas_pontuados' após importar da API:")
print(df_atletas_pontuados[df_atletas_pontuados['rodada_id'] == ultima_rodada_finalizada].head())

# Calcular a pontuação ponderada para todas as rodadas e preencher as colunas correspondentes
for idx, row in df_atletas_pontuados.iterrows():
    if row['rodada_id'] <= ultima_rodada_finalizada:
        df_atletas_pontuados.at[idx, 'pt_scout'] = calcular_pontuacao_scout(row, scouts_pesos)

# Print dos 10 primeiros registros do DataFrame df_atletas_pontuados após calcular a pontuação ponderada
print("\nPrimeiros 10 registros do DataFrame 'atletas_pontuados' após calcular a pontuação ponderada:")
print(df_atletas_pontuados[df_atletas_pontuados['rodada_id'] == ultima_rodada_finalizada].head(10))

# Criar colunas "pt_scout_<scout>" e preenchê-las com as pontuações ponderadas
for scout in scouts_pesos.keys():
    df_atletas_pontuados[f'pt_scout_{scout}'] = df_atletas_pontuados.apply(
        lambda row: row['pt_scout'] if row['rodada_id'] == ultima_rodada_finalizada else 0, axis=1
    )

# Remover colunas de scouts não utilizadas no DataFrame df_atletas_pontuados
scouts_nao_utilizados = set(df_atletas_pontuados.columns) - set(['atleta_id', 'posicao_id', 'clube_id', 'pontuacao', 'entrou_em_campo', 'rodada_id', 'pt_scout'])
df_atletas_pontuados.drop(columns=scouts_nao_utilizados, inplace=True)

# Print dos 10 primeiros registros do DataFrame df_atletas_pontuados após preencher as colunas com pontuação ponderada
print("\nPrimeiros 10 registros do DataFrame 'atletas_pontuados' após preencher as colunas com pontuação ponderada:")
print(df_atletas_pontuados[df_atletas_pontuados['rodada_id'] == ultima_rodada_finalizada].head(10))

# Gerar o nome do arquivo com o momento da criação
data_atual_str = datetime.now().strftime("%Y%m%d%H%M%S")
nome_arquivo_atletas_pontuados = f'atletas_pontuados_{data_atual_str}.xlsx'
nome_arquivo_partidas = f'partidas_{data_atual_str}.xlsx'

# Salvar os DataFrames como arquivos Excel
df_atletas_pontuados.to_excel(nome_arquivo_atletas_pontuados, index=False)
df_partidas.to_excel(nome_arquivo_partidas, index=False)
