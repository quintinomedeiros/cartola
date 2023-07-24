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

# Função para calcular a pontuação ponderada dos scouts
def calcular_pontuacao_scout(scouts, scouts_pesos):
    if scouts is None:
        return {f'pt_scout_{scout}': 0 for scout in scouts_pesos.keys()}

    scout_values = get_scout_values(scouts, scouts_pesos.keys())
    scouts_ponderados = {f'pt_scout_{scout}': valor * scouts_pesos[scout] for scout, valor in scout_values.items()}

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
