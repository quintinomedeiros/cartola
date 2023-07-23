import pandas as pd
import requests
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")  # Ignorar mensagens de aviso

# Função para extrair os valores dos scouts
def get_scout_values(scouts, scout_keys):
    if isinstance(scouts, dict):
        return {scout: scouts.get(scout, 0) for scout in scout_keys}
    else:
        return {scout: 0 for scout in scout_keys}

# Dicionário com os pesos dos scouts
scouts_pesos = {
    'ds': 1.2, 'fc': -0.3, 'gc': -3.0, 'ca': -1.0, 'cv': -3.0, 'sg': 5.0, 'dp': 7.0, 'gs': -1.0,
    'pc': -1.0, 'fs': 0.5, 'a': 5.0, 'ft': 3.0, 'fd': 1.2, 'ff': 0.8, 'g': 8.0, 'i': -0.1,
    'pp': -4.0, 'ps': 1.0
}

# Função para calcular a pontuação dos scouts multiplicando a frequência pelo peso correspondente
def calcular_pontuacao_scout(scouts, scouts_pesos):
    if scouts is None:
        return {f'pt_scout_{scout}': 0 for scout in scouts_pesos.keys()}
    
    scout_values = get_scout_values(scouts, scouts_pesos.keys())
    scouts_ponderados = {f'pt_scout_{scout}': valor * scouts_pesos[scout] for scout, valor in scout_values.items()}
    return scouts_ponderados


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
rodadas_filtradas = dados_rodadas[dados_rodadas['rodada_fim'] <= ultima_data]['rodada_id']

# Lista para armazenar os atributos dos atletas
atletas_dados = []

# Iterar sobre as rodadas e buscar a pontuação
for rodada_id in rodadas_filtradas:
    url_pontuacoes = f'https://api.cartolafc.globo.com/atletas/pontuados/{rodada_id}'
    resposta_pontuacoes = requests.get(url_pontuacoes)
    objetos_pontuacoes = resposta_pontuacoes.json()
    if 'atletas' in objetos_pontuacoes:
        atletas = objetos_pontuacoes['atletas']
        for atleta_id, atleta in atletas.items():
            # Coletar a pontuação do atleta na rodada específica
            pontuacao = atleta.get('pontuacao', 0)
            # Coletar atributos dos atletas
            scouts = atleta.get('scout')
            pontuacao_scouts = calcular_pontuacao_scout(scouts, scouts_pesos)
            atletas_dados.append({
                'atleta_id': atleta_id,
                'posicao_id': atleta['posicao_id'],
                'time_id': atleta['clube_id'],
                'pontuacao': pontuacao,
                'entrou_em_campo': atleta['entrou_em_campo'],
                'rodada_id': rodada_id,
                **pontuacao_scouts
            })

# Criar DataFrame com os atributos dos atletas
df_atletas = pd.DataFrame(atletas_dados)

# Lista para armazenar as informações das partidas
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

                # Filtrar atletas do time mandante na rodada específica
                atletas_mandante = df_atletas[(df_atletas['time_id'] == mandante_id) & (df_atletas['rodada_id'] == rodada_id)]
                if not atletas_mandante.empty:
                    clube_aprov = ', '.join(partida['aproveitamento_mandante'])
                    clube_pos = partida['clube_casa_posicao']
                    vis_plac = partida['placar_oficial_visitante']
                    mand_plac = partida['placar_oficial_mandante']
                    valida = partida['valida']
                    clube_mand = True
                    atletas_mandante['clube_mand'] = clube_mand
                    atletas_mandante['clube_aprov'] = clube_aprov
                    atletas_mandante['clube_pos'] = clube_pos
                    atletas_mandante['vis_plac'] = vis_plac
                    atletas_mandante['mand_plac'] = mand_plac
                    atletas_mandante['valida'] = valida
                    # Adicionar informações dos atletas do time mandante à lista de partidas
                    partidas_dados.extend(atletas_mandante.to_dict(orient='records'))

                # Filtrar atletas do time visitante na rodada específica
                atletas_visitante = df_atletas[(df_atletas['time_id'] == visitante_id) & (df_atletas['rodada_id'] == rodada_id)]
                if not atletas_visitante.empty:
                    clube_aprov = ', '.join(partida['aproveitamento_visitante'])
                    clube_pos = partida['clube_visitante_posicao']
                    vis_plac = partida['placar_oficial_visitante']
                    mand_plac = partida['placar_oficial_mandante']
                    valida = partida['valida']
                    clube_mand = False
                    atletas_visitante['clube_mand'] = clube_mand
                    atletas_visitante['clube_aprov'] = clube_aprov
                    atletas_visitante['clube_pos'] = clube_pos
                    atletas_visitante['vis_plac'] = vis_plac
                    atletas_visitante['mand_plac'] = mand_plac
                    atletas_visitante['valida'] = valida
                    # Adicionar informações dos atletas do time visitante à lista de partidas
                    partidas_dados.extend(atletas_visitante.to_dict(orient='records'))

# Adicionar as informações das partidas ao DataFrame dos atletas
df_combined = pd.DataFrame(partidas_dados, columns=[
    'atleta_id', 'posicao_id', 'time_id', 'pontuacao', 'entrou_em_campo', 'rodada_id',
    *scouts_pesos.keys(), 'clube_mand', 'clube_aprov', 'clube_pos', 'vis_plac', 'mand_plac', 'valida'
])

# Somar as pontuações dos scouts ponderados
df_combined['pt_scouts_total'] = df_combined[[col for col in df_combined.columns if col.startswith('pt_scout_')]].sum(axis=1)

# Calcular a pontuação do time na rodada
df_combined['pt_time'] = df_combined.groupby(['rodada_id', 'time_id'])['pontuacao'].transform('sum')

# Calcular a média da pontuação dos atletas na rodada
df_combined['md_time'] = df_combined.groupby(['rodada_id', 'time_id'])['pontuacao'].transform('mean')

# Gerar o nome do arquivo com o momento da criação
data_atual_str = datetime.now().strftime("%Y%m%d%H%M%S")
nome_arquivo = f'jogadores_e_partidas_{data_atual_str}.xlsx'

# Salvar o DataFrame como um arquivo Excel
df_combined.to_excel(nome_arquivo, index=False)
