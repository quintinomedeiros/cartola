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

# Criar listas vazias para armazenar os atributos dos atletas
atletas_dados = []

# Iterar sobre as rodadas e buscar a pontuação
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
                'atleta_apelido': atleta['apelido'],
                'posicao_id': atleta['posicao_id'],
                'time_id': atleta['clube_id'],
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
                'scout_ds': scouts.get('DS', 0) if scouts is not None else 0,
                'scout_sg': scouts.get('SG', 0) if scouts is not None else 0,
                'scout_gc': scouts.get('GC', 0) if scouts is not None else 0,
                'scout_gs': scouts.get('GS', 0) if scouts is not None else 0,
                'scout_ps': scouts.get('PS', 0) if scouts is not None else 0,
                'scout_pc': scouts.get('PC', 0) if scouts is not None else 0,
                'scout_a': scouts.get('A', 0) if scouts is not None else 0,
                'scout_fd': scouts.get('FD', 0) if scouts is not None else 0,
                'scout_pp': scouts.get('PP', 0) if scouts is not None else 0
            })

# Criar DataFrame com os atributos dos atletas
df_combined = pd.DataFrame(atletas_dados)

# Calcular campos multiplicando a pontuação de cada scout pelo seu respectivo peso
for scout, peso in scouts_pesos.items():
    campo_scout = 'scout_' + scout
    campo_pontuacao = 'pt_' + campo_scout
    df_combined[campo_pontuacao] = df_combined[campo_scout] * peso

# Obter informações das partidas
partidas_dados = []

# Iterar sobre as rodadas realizadas
for rodada_id in rodadas_filtradas:
    url_partidas = f'https://api.cartolafc.globo.com/partidas/{rodada_id}'
    resposta_partidas = requests.get(url_partidas)
    if resposta_partidas.status_code == 200:
        data_partidas = resposta_partidas.json()
        if 'partidas' in data_partidas:
            for partida in data_partidas['partidas']:
                mandante_id = partida['clube_casa_id']
                visitante_id = partida['clube_visitante_id']
                for index, row in df_combined.iterrows():
                    if row['time_id'] == mandante_id and row['rodada_id'] == rodada_id:
                        part_data = partida['partida_data']
                        clube_aprov = ', '.join(partida['aproveitamento_mandante'])
                        clube_pos = partida['clube_casa_posicao']
                        vis_plac = partida['placar_oficial_visitante']
                        mand_plac = partida['placar_oficial_mandante']
                        valida = partida['valida']
                        clube_mand = True
                        partidas_dados.append([row['atleta_id'], row['atleta_apelido'], row['posicao_id'],
                                              row['time_id'], row['pontuacao'], row['entrou_em_campo'],
                                              row['rodada_id'], row['scout_ca'], row['scout_cv'], row['scout_dp'],
                                              row['scout_fc'], row['scout_ff'], row['scout_fs'], row['scout_ft'],
                                              row['scout_g'], row['scout_i'], row['scout_ds'], row['scout_sg'],
                                              row['scout_gc'], row['scout_gs'], row['scout_ps'], row['scout_pc'],
                                              row['scout_a'], row['scout_fd'], row['scout_pp'],
                                              row['pt_scout_ca'], row['pt_scout_cv'], row['pt_scout_dp'],
                                              row['pt_scout_fc'], row['pt_scout_ff'], row['pt_scout_fs'],
                                              row['pt_scout_ft'], row['pt_scout_g'], row['pt_scout_i'],
                                              row['pt_scout_ds'], row['pt_scout_sg'], row['pt_scout_gc'],
                                              row['pt_scout_gs'], row['pt_scout_ps'], row['pt_scout_pc'],
                                              row['pt_scout_a'], row['pt_scout_fd'], row['pt_scout_pp'],
                                              clube_mand, partida['partida_id'], part_data, clube_aprov, clube_pos,
                                              vis_plac, mand_plac, valida])
                    elif row['time_id'] == visitante_id and row['rodada_id'] == rodada_id:
                        part_data = partida['partida_data']
                        clube_aprov = ', '.join(partida['aproveitamento_visitante'])
                        clube_pos = partida['clube_visitante_posicao']
                        vis_plac = partida['placar_oficial_visitante']
                        mand_plac = partida['placar_oficial_mandante']
                        valida = partida['valida']
                        clube_mand = False
                        partidas_dados.append([row['atleta_id'], row['atleta_apelido'], row['posicao_id'],
                                              row['time_id'], row['pontuacao'], row['entrou_em_campo'],
                                              row['rodada_id'], row['scout_ca'], row['scout_cv'], row['scout_dp'],
                                              row['scout_fc'], row['scout_ff'], row['scout_fs'], row['scout_ft'],
                                              row['scout_g'], row['scout_i'], row['scout_ds'], row['scout_sg'],
                                              row['scout_gc'], row['scout_gs'], row['scout_ps'], row['scout_pc'],
                                              row['scout_a'], row['scout_fd'], row['scout_pp'],
                                              row['pt_scout_ca'], row['pt_scout_cv'], row['pt_scout_dp'],
                                              row['pt_scout_fc'], row['pt_scout_ff'], row['pt_scout_fs'],
                                              row['pt_scout_ft'], row['pt_scout_g'], row['pt_scout_i'],
                                              row['pt_scout_ds'], row['pt_scout_sg'], row['pt_scout_gc'],
                                              row['pt_scout_gs'], row['pt_scout_ps'], row['pt_scout_pc'],
                                              row['pt_scout_a'], row['pt_scout_fd'], row['pt_scout_pp'],
                                              clube_mand, partida['partida_id'], part_data, clube_aprov, clube_pos,
                                              vis_plac, mand_plac, valida])

# Criar DataFrame com os atributos dos atletas e informações das partidas
df_combined = pd.DataFrame(partidas_dados, columns=[
    'atleta_id', 'atleta_apelido', 'posicao_id', 'time_id', 'pontuacao', 'entrou_em_campo', 'rodada_id',
    'scout_ca', 'scout_cv', 'scout_dp', 'scout_fc', 'scout_ff', 'scout_fs', 'scout_ft', 'scout_g', 'scout_i',
    'scout_ds', 'scout_sg', 'scout_gc', 'scout_gs', 'scout_ps', 'scout_pc', 'scout_a', 'scout_fd', 'scout_pp',
    'pt_scout_ca', 'pt_scout_cv', 'pt_scout_dp', 'pt_scout_fc', 'pt_scout_ff', 'pt_scout_fs', 'pt_scout_ft',
    'pt_scout_g', 'pt_scout_i', 'pt_scout_ds', 'pt_scout_sg', 'pt_scout_gc', 'pt_scout_gs', 'pt_scout_ps',
    'pt_scout_pc', 'pt_scout_a', 'pt_scout_fd', 'pt_scout_pp', 'clube_mand', 'partida_id', 'part_data',
    'clube_aprov', 'clube_pos', 'vis_plac', 'mand_plac', 'valida'
])

# Calcular a pontuação do time na rodada
df_combined['pt_time'] = df_combined.groupby(['rodada_id', 'time_id'])['pontuacao'].transform('sum')

# Calcular a média da pontuação dos atletas na rodada
df_combined['md_time'] = df_combined.groupby(['rodada_id', 'time_id'])['pontuacao'].transform('mean')

# Gerar o nome do arquivo com o momento da criação
data_atual_str = datetime.now().strftime("%Y%m%d%H%M%S")
nome_arquivo = f'jogadores_e_partidas_{data_atual_str}.xlsx'

# Salvar o DataFrame como um arquivo Excel
df_combined.to_excel(nome_arquivo, index=False)
