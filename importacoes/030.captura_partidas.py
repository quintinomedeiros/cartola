import pandas as pd
import requests
from datetime import datetime

# Ler o arquivo Excel com as informações das rodadas
df_rodadas = pd.read_excel('base/dados_rodadas.xlsx')

# Obter a data atual
data_atual = datetime.now()

# Converter a coluna "rodada_fim" para o tipo datetime
df_rodadas['rodada_fim'] = pd.to_datetime(df_rodadas['rodada_fim'])

# Filtrar as rodadas que já terminaram antes da data atual
rodadas_realizadas = df_rodadas[df_rodadas['rodada_fim'] < data_atual]

# Inicializar a lista de partidas
partidas = []

# Iterar sobre as rodadas realizadas
for _, rodada in rodadas_realizadas.iterrows():
    rodada_id = rodada['rodada_id']

    # Construir a URL das partidas da rodada
    url_partidas = f'https://api.cartolafc.globo.com/partidas/{rodada_id}'

    # Fazer a requisição para obter os dados das partidas
    response = requests.get(url_partidas)

    if response.status_code == 200:
        data = response.json()
        for partida in data['partidas']:
            # Extrair as informações da partida
            info_partida = {
                'rodada_id': rodada_id,
                'vis_aprov': ', '.join(partida['aproveitamento_visitante']),
                'mand_aprov': ', '.join(partida['aproveitamento_mandante']),
                'part_data': partida['partida_data'],
                'vis_plac': partida['placar_oficial_visitante'],
                'mand_plac': partida['placar_oficial_mandante'],
                'partida_id': partida['partida_id'],
                'vis_pos': partida['clube_visitante_posicao'],
                'vis_id': partida['clube_visitante_id'],
                'mand_pos': partida['clube_casa_posicao'],
                'mand_id': partida['clube_casa_id']
            }
            partidas.append(info_partida)
    else:
        print('Erro ao obter os dados da API para a rodada {}: {}'.format(rodada_id, response.text))

# Obter a rodada atual
rodada_atual = df_rodadas[df_rodadas['rodada_fim'] >= data_atual].iloc[0]
rodada_atual_id = rodada_atual['rodada_id']

# Construir a URL das partidas da rodada atual
url_partidas_atual = f'https://api.cartolafc.globo.com/partidas/{rodada_atual_id}'

# Fazer a requisição para obter os dados das partidas da rodada atual
response_atual = requests.get(url_partidas_atual)

if response_atual.status_code == 200:
    data_api_atual = response_atual.json()
    for partida in data_api_atual['partidas']:
        # Extrair as informações da partida da rodada atual
        info_partida_atual = {
            'rodada_id': rodada_atual_id,
            'vis_aprov': ', '.join(partida['aproveitamento_visitante']),
            'mand_aprov': ', '.join(partida['aproveitamento_mandante']),
            'part_data': partida['partida_data'],
            'vis_plac': partida['placar_oficial_visitante'],
            'mand_plac': partida['placar_oficial_mandante'],
            'partida_id': partida['partida_id'],
            'vis_pos': partida['clube_visitante_posicao'],
            'vis_id': partida['clube_visitante_id'],
            'mand_pos': partida['clube_casa_posicao'],
            'mand_id': partida['clube_casa_id']
        }
        partidas.append(info_partida_atual)
else:
    print('Erro ao obter os dados da API para a rodada {}: {}'.format(rodada_atual_id, response_atual.text))

# Criar o DataFrame com as informações das partidas
df_partidas = pd.DataFrame(partidas)

# Reordenar as colunas do DataFrame
df_partidas = df_partidas.reindex(columns=[
    'rodada_id',
    'vis_aprov',
    'mand_aprov',
    'part_data',
    'vis_plac',
    'mand_plac',
    'partida_id',
    'vis_pos',
    'vis_id',
    'mand_pos',
    'mand_id'
])

# Gerar o nome do arquivo com o momento da criação
data_atual_str = datetime.now().strftime("%Y%m%d%H%M%S")
nome_arquivo = f'dados_partidas_{data_atual_str}.xlsx'

# Salvar o DataFrame como um arquivo Excel
df_partidas.to_excel(nome_arquivo, index=False)
