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

# Dicionário com os pesos dos scouts
scouts_pesos = {
    'ds': 1.2, 'fc': -0.3, 'gc': -3.0, 'ca': -1.0, 'cv': -3.0, 'sg': 5.0, 'dp': 7.0, 'gs': -1.0,
    'pc': -1.0, 'fs': 0.5, 'a': 5.0, 'ft': 3.0, 'fd': 1.2, 'ff': 0.8, 'g': 8.0, 'i': -0.1,
    'pp': -4.0, 'ps': 1.0
}

# Função para calcular a pontuação ponderada dos scouts
def calcular_pontuacao_scout(atleta_id, rodada_id, scouts_pesos):
    # URL da API para obter as informações dos scouts do atleta para a rodada
    url_scouts = f'{url_base}/atletas/{atleta_id}/pontuacao/{rodada_id}'
    resposta_scouts = requests.get(url_scouts)
    data_scouts = resposta_scouts.json()

    if 'scout' in data_scouts:
        scouts_atleta = data_scouts['scout']
        scouts_frequencias = {scout: scouts_atleta.get(scout, 0) for scout in scouts_pesos.keys()}
    else:
        scouts_frequencias = {scout: 0 for scout in scouts_pesos.keys()}

    scouts_ponderados = {scout: scouts_frequencias[scout] * scouts_pesos[scout] for scout in scouts_pesos.keys()}

    return scouts_ponderados

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
            # Calcular a pontuação ponderada dos scouts para o atleta na rodada
            scouts_ponderados = calcular_pontuacao_scout(atleta_id, rodada_id, scouts_pesos)
            # Atualizar os valores dos scouts ponderados no dicionário do atleta
            atleta_data.update(scouts_ponderados)
            atleta_pontuado = {
                'atleta_id': int(atleta_id),
                'posicao_id': atleta_data['posicao_id'],
                'clube_id': atleta_data['clube_id'],
                'pontuacao': atleta_data['pontuacao'],
                'entrou_em_campo': atleta_data.get('entrou_em_campo', False),
                'rodada_id': rodada_id,
                **calcular_pontuacao_scout(atleta_data.get('scout'), scouts_pesos)
            }
            atletas_pontuados_dados.append(atleta_pontuado)
    else:
        print("Resposta inválida da API de jogadores pontuados.")

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

# Criar DataFrames com os atributos dos atletas pontuados e das partidas
df_atletas_pontuados = pd.DataFrame(atletas_pontuados_dados)
df_partidas = pd.DataFrame(partidas_dados)

# Exibir apenas os 10 primeiros registros do DataFrame df_atletas_pontuados para verificação
print("\nPrimeiros 10 registros do DataFrame 'atletas_pontuados':")
print(df_atletas_pontuados.head(10))

# Exibir apenas os 10 primeiros registros do DataFrame df_partidas para verificação
print("\nPrimeiros 10 registros do DataFrame 'partidas':")
print(df_partidas.head(10))

# Gerar o nome do arquivo com o momento da criação
data_atual_str = datetime.now().strftime("%Y%m%d%H%M%S")
nome_arquivo_atletas_pontuados = f'atletas_pontuados_{data_atual_str}.xlsx'
nome_arquivo_partidas = f'partidas_{data_atual_str}.xlsx'

# Salvar os DataFrames como arquivos Excel
df_atletas_pontuados.to_excel(nome_arquivo_atletas_pontuados, index=False)
df_partidas.to_excel(nome_arquivo_partidas, index=False)
