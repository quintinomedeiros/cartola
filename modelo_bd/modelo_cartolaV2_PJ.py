import requests
import pandas as pd
from datetime import datetime

base_url = 'https://api.cartolafc.globo.com'

def obter_dados_api(endpoint):
    try:
        url = f'{base_url}/{endpoint}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return data
    except requests.exceptions.RequestException as e:
        print('Erro ao obter os dados da API:', str(e))
        return None

def obter_rodada_atual(dados_rodadas):
    hoje = datetime.now().date()
    ultima_rodada = None

    for rodada in dados_rodadas:
        data_fim = datetime.strptime(rodada['fim'], '%Y-%m-%d %H:%M:%S').date()
        if data_fim < hoje:
            ultima_rodada = rodada['rodada_id']
        else:
            break

    rodada_atual = ultima_rodada + 1 if ultima_rodada is not None else 1

    return rodada_atual

def obter_pontuacoes_jogadores(rodadas):
    pontuacoes_jogadores = []

    for rodada in rodadas:
        endpoint = f"atletas/pontuados/{rodada}"
        data_rodada = obter_dados_api(endpoint)

        if data_rodada is not None and 'atletas' in data_rodada:
            atletas = data_rodada['atletas']
            for atleta_id, atleta in atletas.items():
                jogador_info = {
                    'atleta_id': atleta_id,
                    'apelido': atleta.get('apelido', ''),
                    'posicao_id': atleta.get('posicao_id', 0),
                    'clube_id': atleta.get('clube_id', 0),
                    'entrou_em_campo': atleta.get('entrou_em_campo', False),
                    'pontuacao': atleta.get('pontuacao', 0),
                    'rodada_id': rodada
                }
                scout = atleta.get('scout', {})
                jogador_info.update(scout)
                pontuacoes_jogadores.append(jogador_info)

    return pontuacoes_jogadores

def salvar_em_excel(tabelas, arquivo_excel):
    try:
        with pd.ExcelWriter(arquivo_excel) as writer:
            for nome_tabela, tabela in tabelas.items():
                tabela.to_excel(writer, sheet_name=nome_tabela, index=False)
        print('Dados salvos com sucesso no arquivo Excel:', arquivo_excel)
    except Exception as e:
        print('Erro ao salvar os dados no arquivo Excel:', str(e))

# Passo 1: Obter informações sobre as rodadas
dados_rodadas = obter_dados_api('rodadas')
if dados_rodadas is None:
    exit(1)

rodada_atual = obter_rodada_atual(dados_rodadas)

# Passo 2: Obter as pontuações dos jogadores até a última rodada realizada
rodadas_anteriores = range(1, rodada_atual)
pontuacoes_jogadores = obter_pontuacoes_jogadores(rodadas_anteriores)

# Passo 3: Obter informações da próxima rodada, como destaques, partidas, times, etc.
dados_destaque = obter_dados_api('mercado/destaques')
dados_partidas = obter_dados_api(f'partidas/{rodada_atual}')
dados_times = obter_dados_api('clubes')

# Passo 4: Organizar os dados em tabelas
pontuacoes_jogadores_df = pd.DataFrame(pontuacoes_jogadores)
dados_times_dict = {}

for jogador in dados_times.values():
    if isinstance(jogador, dict) and 'id' in jogador and 'abreviacao' in jogador:
        dados_times_dict[jogador['id']] = jogador['abreviacao']

pontuacoes_jogadores_df['time_abr'] = pontuacoes_jogadores_df['clube_id'].map(dados_times_dict)
pontuacoes_jogadores_df = pontuacoes_jogadores_df[['atleta_id', 'apelido', 'posicao_id', 'clube_id', 'time_abr', 'entrou_em_campo', 'rodada_id', 'CA', 'DS', 'FC', 'FF', 'FD', 'FS', 'I', 'SG', 'A', 'G', 'DE', 'GS', 'V', 'PS', 'FT', 'PP', 'DP', 'CV', 'PC', 'GC', 'pontuacao']]

tabelas = {
    'Pontuações Jogadores': pontuacoes_jogadores_df,
    'Dados Destaque': pd.DataFrame.from_records(dados_destaque),
    'Dados Partidas': pd.DataFrame.from_records(dados_partidas['partidas']),
    'Dados Times': pd.DataFrame.from_records(dados_times)
}

# Passo 5: Salvar as tabelas em um arquivo Excel
data_hora = datetime.now().strftime('%Y%m%d%H%M%S')
nome_arquivo = f'dados_analise_{data_hora}.xlsx'
salvar_em_excel(tabelas, nome_arquivo)
