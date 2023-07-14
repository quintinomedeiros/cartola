import pandas as pd
import requests
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")  # Ignorar mensagens de aviso

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
atletas_ids = []
atletas_apelidos = []
posicoes_ids = []
clubes_ids = []
pontuacoes = []
entrou_em_campos = []
rodada_ids = []
scout_ca = []
scout_cv = []
scout_dp = []
scout_fc = []
scout_ff = []
scout_fs = []
scout_ft = []
scout_g = []
scout_i = []
scout_ds = []
scout_sg = []
scout_gc = []
scout_gs = []
scout_ps = []
scout_pc = []
scout_a = []
scout_fd = []
scout_pp = []

# Iterar sobre as rodadas e buscar a pontuação
for rodada_id in rodadas_filtradas:
    url = f'https://api.cartola.globo.com/atletas/pontuados/{rodada_id}'
    resposta = requests.get(url)
    objetos = resposta.json()
    if 'atletas' in objetos:
        atletas = objetos['atletas']
        for atleta_id, atleta in atletas.items():
            # Coletar atributos dos atletas
            atletas_ids.append(atleta_id)
            atletas_apelidos.append(atleta['apelido'])
            posicoes_ids.append(atleta['posicao_id'])
            clubes_ids.append(atleta['clube_id'])
            pontuacoes.append(atleta['pontuacao'])
            entrou_em_campos.append(atleta['entrou_em_campo'])
            rodada_ids.append(rodada_id)
            scout = atleta.get('scout', {})
            scout_ca.append(scout.get('CA', 0))
            scout_cv.append(scout.get('CV', 0))
            scout_dp.append(scout.get('DP', 0))
            scout_fc.append(scout.get('FC', 0))
            scout_ff.append(scout.get('FF', 0))
            scout_fs.append(scout.get('FS', 0))
            scout_ft.append(scout.get('FT', 0))
            scout_g.append(scout.get('G', 0))
            scout_i.append(scout.get('I', 0))
            scout_ds.append(scout.get('DS', 0))
            scout_sg.append(scout.get('SG', 0))
            scout_gc.append(scout.get('GC', 0))
            scout_gs.append(scout.get('GS', 0))
            scout_ps.append(scout.get('PS', 0))
            scout_pc.append(scout.get('PC', 0))
            scout_a.append(scout.get('A', 0))
            scout_fd.append(scout.get('FD', 0))
            scout_pp.append(scout.get('PP', 0))

# Criar DataFrame com os atributos dos atletas
data = {
    'atleta_id': atletas_ids,
    'atleta_apelido': atletas_apelidos,
    'posicao_id': posicoes_ids,
    'time_id': clubes_ids,
    'pontuacao': pontuacoes,
    'entrou_em_campo': entrou_em_campos,
    'rodada_id': rodada_ids,
    'scout_ca': scout_ca,
    'scout_cv': scout_cv,
    'scout_dp': scout_dp,
    'scout_fc': scout_fc,
    'scout_ff': scout_ff,
    'scout_fs': scout_fs,
    'scout_ft': scout_ft,
    'scout_g': scout_g,
    'scout_i': scout_i,
    'scout_ds': scout_ds,
    'scout_sg': scout_sg,
    'scout_gc': scout_gc,
    'scout_gs': scout_gs,
    'scout_ps': scout_ps,
    'scout_pc': scout_pc,
    'scout_a': scout_a,
    'scout_fd': scout_fd,
    'scout_pp': scout_pp
}
df_combined = pd.DataFrame(data)

# Calcular campos multiplicando a pontuação de cada scout pelo seu respectivo peso
for scout, peso in scouts_pesos.items():
    campo_scout = 'scout_' + scout
    campo_pontuacao = 'pt_' + campo_scout
    df_combined[campo_pontuacao] = df_combined[campo_scout] * peso

# Adicionar a coluna 'time_nome' com o nome do time
url_clubes = 'https://api.cartolafc.globo.com/clubes'
resposta_clubes = requests.get(url_clubes)
dados_clubes = resposta_clubes.json()

# Criar um dicionário com o nome dos clubes
clubes_nomes = {clube['id']: clube['nome'] for clube in dados_clubes.values()}

df_combined['time_nome'] = df_combined['time_id'].map(clubes_nomes)

# Reordenar as colunas
colunas = ['atleta_id', 'atleta_apelido', 'time_id', 'time_nome', 'posicao_id', 'pontuacao', 'entrou_em_campo',
           'rodada_id', 'scout_ca', 'pt_scout_ca', 'scout_cv', 'pt_scout_cv', 'scout_dp', 'pt_scout_dp',
           'scout_fc', 'pt_scout_fc', 'scout_ff', 'pt_scout_ff', 'scout_fs', 'pt_scout_fs', 'scout_ft',
           'pt_scout_ft', 'scout_g', 'pt_scout_g', 'scout_i', 'pt_scout_i', 'scout_ds', 'pt_scout_ds',
           'scout_sg', 'pt_scout_sg', 'scout_gc', 'pt_scout_gc', 'scout_gs', 'pt_scout_gs', 'scout_ps',
           'pt_scout_ps', 'scout_pc', 'pt_scout_pc', 'scout_a', 'pt_scout_a', 'scout_fd', 'pt_scout_fd',
           'scout_pp', 'pt_scout_pp']
df_combined = df_combined[colunas]

# Calcular a pontuação do time na rodada
df_combined['pt_time'] = df_combined.groupby(['rodada_id', 'time_id'])['pontuacao'].transform('sum')

# Calcular a média da pontuação dos atletas na rodada
df_combined['md_time'] = df_combined.groupby(['rodada_id', 'time_id'])['pontuacao'].transform('mean')

# Obter o número da última rodada consultada
ultima_rodada = rodadas_filtradas[-1]

# Obter o momento da gravação
momento_gravacao = datetime.now().strftime("%Y%m%d%H%M%S")

# Gerar o nome do arquivo
nome_arquivo = f"jogadores_pontuacao_{momento_gravacao}.xlsx"

# Salvar o relatório no arquivo Excel
df_combined.to_excel(nome_arquivo, index=False)
