import requests
import pandas as pd
import json
from datetime import datetime

base_url = 'https://api.cartolafc.globo.com'

# Função para obter dados da API
def obter_dados_api(endpoint):
    try:
        url = f'{base_url}/{endpoint}'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print('Erro ao obter os dados da API:', str(e))
        return None

# Função para obter a última rodada já realizada
def obter_rodada_atual(dados_rodadas):
    hoje = datetime.now().date()
    ultima_rodada = None

    for rodada in dados_rodadas:
        data_fim = datetime.strptime(rodada['fim'], '%Y-%m-%d %H:%M:%S').date()
        if data_fim < hoje:
            ultima_rodada = rodada['rodada_id']
        else:
            break

    return ultima_rodada if ultima_rodada is not None else 1

# Função para obter as pontuações dos jogadores até a última rodada realizada
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
                    'rodada_id': rodada,
                    'pontuacao': atleta.get('pontuacao', 0),
                    **atleta.get('scout', {})
                }
                pontuacoes_jogadores.append(jogador_info)

    return pontuacoes_jogadores

# Função para obter os dados de destaque dos jogadores
def obter_dados_destaque(dados_destaque, dados_times):
    dados_destaque_limpos = []

    for destaque in dados_destaque:
        atleta_info = destaque.get('Atleta', {})
        clube_id = destaque.get('clube_id', '')
        clube_info = dados_times.get('clubes', {}).get(str(clube_id), {})
        time_abr = clube_info.get('abreviacao', '')

        dados_destaque_limpos.append({
            'atleta_id': atleta_info.get('atleta_id', ''),
            'apelido': atleta_info.get('apelido', ''),
            'clube_id': clube_id,
            'time_abr': time_abr,
            'posicao_abreviacao': destaque.get('posicao_abreviacao', ''),
            'preco_editorial': atleta_info.get('preco_editorial', ''),
            'escalacoes': destaque.get('escalacoes', '')
        })

    return dados_destaque_limpos

# Função para obter os dados de status dos jogadores
def obter_dados_status(dados_times):
    dados_status = dados_times.get('status', {})
    status_info = []

    for status_id, status in dados_status.items():
        status_info.append({
            'id': status.get('id', ''),
            'nome': status.get('nome', '')
        })

    return status_info

# Função para obter os dados de posições dos jogadores
def obter_dados_posicoes(dados_times):
    dados_posicoes = dados_times.get('posicoes', {})
    posicoes_info = []

    for posicao_id, posicao in dados_posicoes.items():
        posicoes_info.append({
            'id': posicao.get('id', ''),
            'nome': posicao.get('nome', '')
        })

    return posicoes_info

# Função para salvar as tabelas em um arquivo Excel
def salvar_em_excel(tabelas, arquivo_excel):
    try:
        with pd.ExcelWriter(arquivo_excel) as writer:
            for nome_tabela, tabela in tabelas.items():
                tabela.to_excel(writer, sheet_name=nome_tabela, index=False)
        print('Dados salvos com sucesso no arquivo Excel:', arquivo_excel)
    except Exception as e:
        print('Erro ao salvar os dados no arquivo Excel:', str(e))

# Função para preencher campos vazios em todas as tabelas
def preencher_campos_vazios(tabelas):
    for nome_tabela, tabela in tabelas.items():
        tabela.fillna('', inplace=True)

# Passo 1: Obter informações sobre as rodadas
dados_rodadas = obter_dados_api('rodadas')
if dados_rodadas is None:
    exit(1)

rodada_atual = obter_rodada_atual(dados_rodadas) + 1

# Passo 2: Obter as pontuações dos jogadores até a última rodada realizada
rodadas_anteriores = range(1, rodada_atual)
pontuacoes_jogadores = obter_pontuacoes_jogadores(rodadas_anteriores)

# Passo 3: Obter informações das rodadas finalizadas e da rodada atual, como destaques, partidas, times, etc.
rodadas_finalizadas = [rodada['rodada_id'] for rodada in dados_rodadas if datetime.strptime(rodada['fim'], '%Y-%m-%d %H:%M:%S').date() < datetime.now().date()]
ultima_rodada_finalizada = rodadas_finalizadas[-1] if rodadas_finalizadas else None

dados_destaque = obter_dados_api('mercado/destaques')
dados_partidas_realizadas = []
dados_partidas_atual = []

for rodada in rodadas_finalizadas:
    endpoint = f'partidas/{rodada}'
    data_partidas = obter_dados_api(endpoint)
    if data_partidas is not None and 'partidas' in data_partidas:
        for partida in data_partidas['partidas']:
            partida['rodada_id'] = rodada
        dados_partidas_realizadas.extend(data_partidas['partidas'])

if rodada_atual is not None and rodada_atual not in rodadas_finalizadas:
    endpoint = f'partidas/{rodada_atual}'
    data_partidas = obter_dados_api(endpoint)
    if data_partidas is not None and 'partidas' in data_partidas:
        for partida in data_partidas['partidas']:
            partida['rodada_id'] = rodada_atual
        dados_partidas_atual = data_partidas['partidas']
else:
    dados_partidas_atual = []

# Filtrar somente as partidas da rodada atual na tabela "dados_partidas_atual"
dados_partidas_atual = [partida for partida in dados_partidas_atual if partida['rodada_id'] == rodada_atual]

if rodada_atual is not None and rodada_atual not in rodadas_finalizadas:
    endpoint = f'partidas/{rodada_atual}'
    data_partidas = obter_dados_api(endpoint)
    if data_partidas is not None and 'partidas' in data_partidas:
        for partida in data_partidas['partidas']:
            partida['rodada_id'] = rodada_atual
        dados_partidas_atual = data_partidas['partidas']
else:
    dados_partidas_atual = []

dados_times = obter_dados_api('atletas/mercado')

# Passo 4: Organizar os dados em tabelas
pontuacoes_jogadores_df = pd.DataFrame(pontuacoes_jogadores)[['atleta_id', 'apelido', 'posicao_id', 'clube_id', 'entrou_em_campo', 'rodada_id', 'CA', 'DS', 'FC', 'FF', 'FD', 'FS', 'I', 'SG', 'A', 'G', 'DE', 'GS', 'V', 'PS', 'FT', 'PP', 'DP', 'CV', 'PC', 'GC', 'pontuacao']]
dados_destaque_df = pd.DataFrame(obter_dados_destaque(dados_destaque, dados_times))[['atleta_id', 'apelido', 'clube_id', 'time_abr', 'posicao_abreviacao', 'preco_editorial', 'escalacoes']]
dados_partidas_realizadas_df = pd.DataFrame.from_records(dados_partidas_realizadas)
dados_partidas_atual_df = pd.DataFrame.from_records(dados_partidas_atual)

dados_times_clubes = []
clubes = dados_times.get('clubes', {})
for clube_id, clube_info in clubes.items():
    nome = clube_info.get('nome', '')
    abreviacao = clube_info.get('abreviacao', '')
    dados_times_clubes.append({
        'clube_id': clube_id,
        'clube_nome': nome,
        'abreviacao': abreviacao
    })
dados_times_df = pd.DataFrame(dados_times_clubes, columns=['clube_id', 'clube_nome', 'abreviacao'])

dados_status_info = obter_dados_status(dados_times)
dados_status_df = pd.DataFrame(dados_status_info, columns=['id', 'nome'])

dados_posicoes_info = obter_dados_posicoes(dados_times)
dados_posicoes_df = pd.DataFrame(dados_posicoes_info, columns=['id', 'nome'])

# Converter clube_casa_id e clube_visitante_id para o mesmo tipo de dados que clube_id
dados_partidas_realizadas_df['clube_casa_id'] = dados_partidas_realizadas_df['clube_casa_id'].astype(str)
dados_partidas_realizadas_df['clube_visitante_id'] = dados_partidas_realizadas_df['clube_visitante_id'].astype(str)

# Merge dos dados de clubes e partidas
dados_partidas_realizadas_df = dados_partidas_realizadas_df.merge(dados_times_df[['clube_id', 'clube_nome']], left_on='clube_casa_id', right_on='clube_id', how='left')
dados_partidas_realizadas_df = dados_partidas_realizadas_df.merge(dados_times_df[['clube_id', 'clube_nome']], left_on='clube_visitante_id', right_on='clube_id', how='left')
dados_partidas_realizadas_df = dados_partidas_realizadas_df.drop(['clube_id_x', 'clube_id_y'], axis=1)
dados_partidas_realizadas_df = dados_partidas_realizadas_df.rename(columns={'clube_nome_x': 'clube_casa_nome', 'clube_nome_y': 'clube_visitante_nome'})

# Reordenar campos na tabela "Dados Partidas Realizadas"
campos_ordenados_realizadas = [
    'rodada_id',
    'partida_id',
    'partida_data',
    'clube_casa_id',
    'clube_casa_nome',
    'clube_casa_posicao',
    'aproveitamento_mandante',
    'clube_visitante_id',
    'clube_visitante_nome',
    'clube_visitante_posicao',
    'aproveitamento_visitante',
    'placar_oficial_mandante',
    'placar_oficial_visitante',
    'valida'
]
dados_partidas_realizadas_df = dados_partidas_realizadas_df[campos_ordenados_realizadas]

# Reordenar campos na tabela "Dados Partidas Atual"
campos_ordenados_atual = [
    'rodada_id',
    'partida_id',
    'partida_data',
    'clube_casa_id',
    'clube_casa_posicao',
    'aproveitamento_mandante',
    'clube_visitante_id',
    'clube_visitante_posicao',
    'aproveitamento_visitante',
    'valida'
]
dados_partidas_atual_df = dados_partidas_atual_df[campos_ordenados_atual]

# Passo 5: Obter informações dos atletas no mercado
dados_atletas_mercado = []
atletas_mercado = dados_times.get('atletas', {})
for atleta in atletas_mercado:
    atleta_info = {
        'atleta_id': atleta.get('atleta_id', ''),
        'apelido': atleta.get('apelido', ''),
        'rodada_id': atleta.get('rodada_id', ''),
        'clube_id': atleta.get('clube_id', ''),
        'posicao_id': atleta.get('posicao_id', ''),
        'status_id': atleta.get('status_id', ''),
        'pontos_num': atleta.get('pontos_num', ''),
        'preco_num': atleta.get('preco_num', ''),
        'variacao_num': atleta.get('variacao_num', ''),
        'media_num': atleta.get('media_num', ''),
        'jogos_num': atleta.get('jogos_num', ''),
        'minimo_para_valorizar': atleta.get('minimo_para_valorizar', ''),
    }

    scout = atleta.get('scout', {})
    atleta_info.update(scout)

    gato_mestre = atleta.get('gato_mestre', {})
    media_pontos_mandante = gato_mestre.get('media_pontos_mandante', '')
    media_pontos_visitante = gato_mestre.get('media_pontos_visitante', '')
    media_minutos_jogados = gato_mestre.get('media_minutos_jogados', '')
    minutos_jogados = gato_mestre.get('minutos_jogados', '')

    atleta_info['gt_med_FS'] = atleta_info.pop('FS', 0)
    atleta_info['gt_med_G'] = atleta_info.pop('G', 0)
    atleta_info['gt_med_DS'] = atleta_info.pop('DS', 0)
    atleta_info['gt_med_FC'] = atleta_info.pop('FC', 0)
    atleta_info['gt_med_PP'] = atleta_info.pop('PP', 0)
    atleta_info['gt_med_FD'] = atleta_info.pop('FD', 0)

    atleta_info['gt_man_FS'] = atleta_info.pop('FS', 0)
    atleta_info['gt_man_G'] = atleta_info.pop('G', 0)
    atleta_info['gt_man_DS'] = atleta_info.pop('DS', 0)
    atleta_info['gt_man_FC'] = atleta_info.pop('FC', 0)
    atleta_info['gt_man_CA'] = atleta_info.pop('CA', 0)
    atleta_info['gt_man_FF'] = atleta_info.pop('FF', 0)
    atleta_info['gt_man_FD'] = atleta_info.pop('FD', 0)

    atleta_info['gt_vis_FS'] = atleta_info.pop('FS', 0)
    atleta_info['gt_vis_G'] = atleta_info.pop('G', 0)
    atleta_info['gt_vis_DS'] = atleta_info.pop('DS', 0)
    atleta_info['gt_vis_FC'] = atleta_info.pop('FC', 0)
    atleta_info['gt_vis_PP'] = atleta_info.pop('PP', 0)
    atleta_info['gt_vis_FD'] = atleta_info.pop('FD', 0)

    atleta_info['gt_med_media_pontos_mandante'] = media_pontos_mandante
    atleta_info['gt_med_media_pontos_visitante'] = media_pontos_visitante
    atleta_info['gt_med_media_minutos_jogados'] = media_minutos_jogados
    atleta_info['gt_med_minutos_jogados'] = minutos_jogados

    dados_atletas_mercado.append(atleta_info)

# Reorganizar campos na tabela "Atletas Mercado"
campos_ordenados_atletas_mercado = [
    'atleta_id',
    'apelido',
    'rodada_id',
    'clube_id',
    'posicao_id',
    'status_id',
    'pontos_num',
    'preco_num',
    'variacao_num',
    'media_num',
    'jogos_num',
    'minimo_para_valorizar',
    'FT',
    'SG',
    'A',
    'I',
    'DE',
    'GS',
    'PS',
    'CV',
    'PC',
    'DP',
    'GC',
    'V',
    'gt_med_media_pontos_mandante',
    'gt_med_media_pontos_visitante',
    'gt_med_media_minutos_jogados',
    'gt_med_minutos_jogados',
    'gt_med_FS',
    'gt_med_G',
    'gt_med_DS',
    'gt_med_FC',
    'gt_med_PP',
    'gt_med_FD',
    'gt_man_FS',
    'gt_man_G',
    'gt_man_DS',
    'gt_man_FC',
    'gt_man_CA',
    'gt_man_FF',
    'gt_man_FD',
    'gt_vis_FS',
    'gt_vis_G',
    'gt_vis_DS',
    'gt_vis_FC',
    'gt_vis_PP',
    'gt_vis_FD'
]

# Criar DataFrame da tabela "Atletas Mercado"
atletas_mercado_df = pd.DataFrame(dados_atletas_mercado)
# Reordenar as colunas
atletas_mercado_df = atletas_mercado_df.reindex(columns=campos_ordenados_atletas_mercado)

tabelas = {
    'pontuacoes_jogadores': pontuacoes_jogadores_df,
    'dados_destaque': dados_destaque_df,
    'dados_partidas_realizadas': dados_partidas_realizadas_df,
    'dados_partidas_atual': dados_partidas_atual_df,
    'dados_times': dados_times_df,
    'status': dados_status_df,
    'posicoes': dados_posicoes_df,
    'atletas_mercado': atletas_mercado_df
}

# Passo 6: Preencher campos vazios em todas as tabelas
preencher_campos_vazios(tabelas)

# Passo 7: Salvar as tabelas em um arquivo Excel
data_hora = datetime.now().strftime('%Y%m%d%H%M%S')
nome_arquivo_excel = f'dados_cartola_{data_hora}.xlsx'
salvar_em_excel(tabelas, nome_arquivo_excel)

# Salvar as tabelas em um arquivo CSV
for nome_tabela, tabela in tabelas.items():
    nome_arquivo_csv = f'{nome_tabela}_{data_hora}.csv'
    tabela.to_csv(nome_arquivo_csv, index=False)
    print(f'Dados salvos com sucesso no arquivo CSV: {nome_arquivo_csv}')
