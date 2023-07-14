import requests
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

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
                    'rodada_id': rodada,
                    'pontuacao': atleta.get('pontuacao', 0),
                }
                scout = atleta.get('scout', {})
                jogador_info.update(scout)
                pontuacoes_jogadores.append(jogador_info)

    return pontuacoes_jogadores

def obter_dados_destaque(dados_destaque, dados_clubes):
    dados_destaque_limpos = []

    for destaque in dados_destaque:
        atleta_info = destaque.get('Atleta', {})
        clube_id = destaque.get('clube_id', '')
        clube_info = dados_clubes.get(str(clube_id), {})
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

def preparar_dados(pontuacoes_jogadores_df, dados_partidas_df):
    # Preencher campos vazios com zeros
    pontuacoes_jogadores_df.fillna(0, inplace=True)

    # Converter dados categóricos em variáveis numéricas
    pontuacoes_jogadores_df['entrou_em_campo'] = pontuacoes_jogadores_df['entrou_em_campo'].map({'VERDADEIRO': 1, 'FALSO': 0})

    # Normalizar os valores numéricos usando Min-Max Scaler
    scaler = MinMaxScaler()
    pontuacoes_jogadores_df[['pontuacao']] = scaler.fit_transform(pontuacoes_jogadores_df[['pontuacao']])

    # Desmembrar colunas 'aproveitamento_visitante' e 'aproveitamento_mandante'
    dados_partidas_df[['ultimos_resultados_visitante1', 'ultimos_resultados_visitante2', 'ultimos_resultados_visitante3', 'ultimos_resultados_visitante4', 'ultimos_resultados_visitante5']] = dados_partidas_df['aproveitamento_visitante'].str.extract('([ved]{1}){0,1}([ed]{1}){0,1}([ved]{1}){0,1}([ed]{1}){0,1}([ved]{1}){0,1}')
    dados_partidas_df[['ultimos_resultados_mandante1', 'ultimos_resultados_mandante2', 'ultimos_resultados_mandante3', 'ultimos_resultados_mandante4', 'ultimos_resultados_mandante5']] = dados_partidas_df['aproveitamento_mandante'].str.extract('([ved]{1}){0,1}([ed]{1}){0,1}([ved]{1}){0,1}([ed]{1}){0,1}([ved]{1}){0,1}')

    # Remover colunas não utilizadas
    colunas_removidas = ['transmissao', 'local', 'status_transmissao_tr', 'status_cronometro_tr', 'periodo_tr', 'inicio_cronometro_tr', 'timestamp', 'campeonato_id']
    dados_partidas_df.drop(columns=colunas_removidas, inplace=True)

    return pontuacoes_jogadores_df, dados_partidas_df

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
rodadas_anteriores = range(1, rodada_atual + 1)

# Passo 2: Obter as pontuações dos jogadores até a última rodada realizada
pontuacoes_jogadores = obter_pontuacoes_jogadores(rodadas_anteriores)

# Passo 3: Obter os dados dos destaques
dados_destaque = obter_dados_api('mercado/destaques')
dados_clubes = obter_dados_api('clubes')

if dados_destaque is None or dados_clubes is None:
    exit(1)

# Passo 4: Organizar os dados em tabelas
pontuacoes_jogadores_df = pd.DataFrame(pontuacoes_jogadores)
dados_destaque_df = pd.DataFrame(obter_dados_destaque(dados_destaque, dados_clubes))
dados_partidas_df = pd.DataFrame(obter_dados_api('partidas'))

# Passo 5: Preparar os dados
pontuacoes_jogadores_df, dados_partidas_df = preparar_dados(pontuacoes_jogadores_df, dados_partidas_df)

tabelas = {
    'Pontuações Jogadores': pontuacoes_jogadores_df[['atleta_id', 'apelido', 'posicao_id', 'clube_id', 'entrou_em_campo', 'rodada_id', 'CA', 'DS', 'FC', 'FF', 'FD', 'FS', 'I', 'SG', 'A', 'G', 'DE', 'GS', 'V', 'PS', 'FT', 'PP', 'DP', 'CV', 'PC', 'GC', 'pontuacao']],
    'Dados Destaque': dados_destaque_df[['atleta_id', 'apelido', 'clube_id', 'time_abr', 'posicao_abreviacao', 'preco_editorial', 'escalacoes']],
    'Dados Partidas': dados_partidas_df[['data_realizacao', 'hora_realizacao', 'clube_casa_id', 'clube_visitante_id', 'ultimos_resultados_mandante1', 'ultimos_resultados_mandante2', 'ultimos_resultados_mandante3', 'ultimos_resultados_mandante4', 'ultimos_resultados_mandante5', 'ultimos_resultados_visitante1', 'ultimos_resultados_visitante2', 'ultimos_resultados_visitante3', 'ultimos_resultados_visitante4', 'ultimos_resultados_visitante5']],
    'Dados Times': pd.DataFrame.from_records(dados_clubes)
}

# Passo 6: Salvar as tabelas em um arquivo Excel
data_hora = datetime.now().strftime('%Y%m%d%H%M%S')
nome_arquivo = f'dados_analise_{data_hora}.xlsx'
salvar_em_excel(tabelas, nome_arquivo)