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
            partida_id = partida['partida_id']
            id_time_mandante = partida['clube_casa_id']
            id_time_visitante = partida['clube_visitante_id']
            gols_mandante = partida['placar_oficial_mandante']
            gols_visitante = partida['placar_oficial_visitante']

            # Determinar o resultado da partida
            if gols_mandante > gols_visitante:
                resultado_mandante = 'VIT'
                resultado_visitante = 'DER'
            elif gols_mandante < gols_visitante:
                resultado_mandante = 'DER'
                resultado_visitante = 'VIT'
            else:
                resultado_mandante = 'EMP'
                resultado_visitante = 'EMP'

            # Adicionar as informações do mandante à lista de partidas
            info_mandante = {
                'rodada_id': rodada_id,
                'partida_id': partida_id,
                'time_id': id_time_mandante,
                'mandante': True,
                'gols_marcados': gols_mandante,
                'gols_sofridos': gols_visitante,
                'resultado': resultado_mandante
            }
            partidas.append(info_mandante)

            # Adicionar as informações do visitante à lista de partidas
            info_visitante = {
                'rodada_id': rodada_id,
                'partida_id': partida_id,
                'time_id': id_time_visitante,
                'mandante': False,
                'gols_marcados': gols_visitante,
                'gols_sofridos': gols_mandante,
                'resultado': resultado_visitante
            }
            partidas.append(info_visitante)
    else:
        print('Erro ao obter os dados da API para a rodada {}: {}'.format(rodada_id, response.text))

# Criar o DataFrame com as informações das partidas
df_partidas = pd.DataFrame(partidas)

# Ler o arquivo Excel com as informações dos clubes
df_times = pd.read_excel('base/dados_times.xlsx')

# Mesclar os DataFrames para obter o nome do time
df_times_partidas = pd.merge(df_partidas, df_times[['time_id', 'time_nome']], on='time_id', how='left')

# Reordenar as colunas do DataFrame
df_times_partidas = df_times_partidas.reindex(columns=[
    'rodada_id',
    'partida_id',
    'time_id',
    'time_nome',
    'mandante',
    'gols_marcados',
    'gols_sofridos',
    'resultado'
])

# Renomear o DataFrame
df_times_partidas.rename(columns={'time_nome': 'nome_time'}, inplace=True)

# Gerar o nome do arquivo com o momento da criação
data_atual_str = data_atual.strftime("%Y%m%d%H%M%S")
nome_arquivo = f'dados_times_partidas_{data_atual_str}.xlsx'

# Salvar o DataFrame como um arquivo Excel
df_times_partidas.to_excel(nome_arquivo, index=False)
