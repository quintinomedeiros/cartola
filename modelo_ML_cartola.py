import pandas as pd
import requests
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")  # Ignorar mensagens de aviso

# Função para calcular a pontuação dos scouts multiplicando pelo peso correspondente
def calcular_pontuacao_scout(scouts, scouts_pesos):
    if scouts is None:
        return 0

    scouts = {scout: scouts.get(scout, 0) for scout in scouts_pesos.keys()}
    pontuacao = sum(valor * scouts_pesos[scout] for scout, valor in scouts.items())
    return pontuacao

# Dicionário com os pesos dos scouts
scouts_pesos = {
    'ds': 1.2, 'fc': -0.3, 'gc': -3.0, 'ca': -1.0, 'cv': -3.0, 'sg': 5.0, 'dp': 7.0, 'gs': -1.0,
    'pc': -1.0, 'fs': 0.5, 'a': 5.0, 'ft': 3.0, 'fd': 1.2, 'ff': 0.8, 'g': 8.0, 'i': -0.1,
    'pp': -4.0, 'ps': 1.0
}

# Obter a quantidade total de rodadas
url_rodadas = 'https://api.cartolafc.globo.com/rodadas'
resposta_rodadas = requests.get(url_rodadas)
rodadas = resposta_rodadas.json()
quantidade_rodadas = len(rodadas)

# Carregar dados do arquivo 'dados_rodadas.xlsx' para obter a última rodada
dados_rodadas = pd.read_excel('base/dados_rodadas.xlsx')

# Converter a coluna "rodada_fim" para o tipo datetime
dados_rodadas['rodada_fim'] = pd.to_datetime(dados_rodadas['rodada_fim'])

# Obter a data e hora atual
ultima_data = datetime.now()

# Filtrar as rodadas até a última
rodadas_filtradas = dados_rodadas[dados_rodadas['rodada_fim'] <= ultima_data]['rodada_id'].tolist()

# Criar listas vazias para armazenar os atributos dos atletas e informações das partidas
atletas_dados = []
partidas_dados = []

# Obter informações dos atletas e das partidas
for rodada_id in rodadas_filtradas:
    url_pontuacoes = f'https://api.cartolafc.globo.com/atletas/pontuados/{rodada_id}'
    resposta_pontuacoes = requests.get(url_pontuacoes)
    objetos_pontuacoes = resposta_pontuacoes.json()
    if 'atletas' in objetos_pontuacoes:
        atletas = objetos_pontuacoes['atletas']
        for atleta_id, atleta in atletas.items():
            # Coletar atributos dos atletas
            scouts = atleta.get('scout')
            pontuacao = calcular_pontuacao_scout(scouts, scouts_pesos)
            atletas_dados.append({
                'atleta_id': atleta_id,
                'posicao_id': atleta['posicao_id'],
                'pontuacao': pontuacao,
                'entrou_em_campo': atleta['entrou_em_campo'],
                'rodada_id': rodada_id,
                'scout_ca': scouts.get('CA', 0) if scouts is not None else 0,
                'scout_cv': scouts.get('CV', 0) if scouts is not None else 0,
                'scout_dp': scouts.get('DP', 0) if scouts is not None else 0,
                'scout_fc': scouts.get('FC', 0) if scouts is not None else 0,
                'scout_ff': scouts.get('FF', 0) if scouts is not None else 0,
                'scout_fs': scouts.get('FS', 0) if scouts is not None else 0,
                'scout_ft': scouts.get('FT', 0) if scouts is not None else 0,
                'scout_g': scouts.get('G', 0) if scouts is not None else 0,
                'scout_i': scouts.get('I', 0) if scouts is not None else 0,
                'scout_pp': scouts.get('PP', 0) if scouts is not None else 0,
                'scout_ps': scouts.get('PS', 0) if scouts is not None else 0,
                'scout_sg': scouts.get('SG', 0) if scouts is not None else 0
            })

            # Obter informações das partidas
            url_partidas = f'https://api.cartolafc.globo.com/partidas/{rodada_id}'
            resposta_partidas = requests.get(url_partidas)
            data_partidas = resposta_partidas.json()
            if 'partidas' in data_partidas:
                for partida in data_partidas['partidas']:
                    mandante_id = partida['clube_casa_id']
                    visitante_id = partida['clube_visitante_id']
                    part_data = partida['partida_data']
                    clube_aprov = ', '.join(partida['aproveitamento_mandante'])
                    clube_pos = partida['clube_casa_posicao']
                    vis_plac = partida['placar_oficial_visitante']
                    mand_plac = partida['placar_oficial_mandante']
                    valida = partida['valida']
                    partidas_dados.append([mandante_id, rodada_id, part_data, clube_aprov, clube_pos, vis_plac, mand_plac, valida])
                    partidas_dados.append([visitante_id, rodada_id, part_data, clube_aprov, clube_pos, vis_plac, mand_plac, valida])

# Criar DataFrame com os atributos dos atletas
df_atletas = pd.DataFrame(atletas_dados)

# Calcular campos multiplicando a pontuação de cada scout pelo seu respectivo peso
for scout, peso in scouts_pesos.items():
    campo_scout = 'scout_' + scout
    campo_pontuacao = 'pt_' + campo_scout
    df_atletas[campo_pontuacao] = df_atletas[campo_scout] * peso

# Criar DataFrame com as informações das partidas
colunas_partidas = ['time_id', 'rodada_id', 'partida_data', 'clube_aprov', 'clube_pos', 'vis_plac', 'mand_plac', 'valida']
df_partidas = pd.DataFrame(partidas_dados, columns=colunas_partidas)

# Calcular a pontuação total do time em cada rodada
df_partidas['pt_time'] = df_partidas.groupby(['rodada_id', 'time_id'])['pontuacao'].transform('sum')

# Combinar os DataFrames para ter as informações dos atletas e das partidas em uma única estrutura
df_combined = pd.merge(df_atletas, df_partidas, on=['time_id', 'rodada_id'], how='left')

# Salvar o DataFrame combinado em um arquivo CSV
df_combined.to_csv('jogadores_partidas.csv', index=False)
