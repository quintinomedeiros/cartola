import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# Dicionário que mapeia os nomes das tabelas aos seus respectivos arquivos CSV
ARQUIVOS_CSV = {
    'Atletas mercado': 'atletas_mercado.csv',
    'Dados Destaque': 'dados_destaque.csv',
    'Dados Partidas': 'dados_partidas.csv',
    'Dados Times': 'dados_times.csv',
    'Pontuacoes Jogadores': 'pontuacoes_jogadores.csv'
}

# Dicionário que mapeia os pesos dos scouts
SCOUT_WEIGHTS = {
    'DS': 1.2,
    'FC': -0.3,
    'GC': -3.0,
    'CA': -1.0,
    'CV': -3.0,
    'SG': 5.0,
    'DE': 1.0,
    'DP': 7.0,
    'GS': -1.0,
    'PC': -1.0,
    'FS': 0.5,
    'I': -0.1,
    'A': 5.0,
    'FT': 3.0,
    'FD': 1.2,
    'FF': 0.8,
    'G': 8.0,
    'PP': -4.0,
    'PS': 1.0,
    'V': 1.0
}

def carregar_dados():
    """
    Carrega os dados dos arquivos CSV para um dicionário de DataFrames.
    """
    diretorio = 'bd_cartola_modelo'
    tabelas = {}

    for nome_tabela, nome_arquivo in ARQUIVOS_CSV.items():
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)
        if os.path.exists(caminho_arquivo):
            tabela = pd.read_csv(caminho_arquivo)
            tabelas[nome_tabela] = tabela
        else:
            print(f'Arquivo não encontrado: {caminho_arquivo}')

    if len(tabelas) != len(ARQUIVOS_CSV):
        # Verificar quais arquivos estão faltando
        arquivos_faltantes = set(ARQUIVOS_CSV.values()) - set(tabelas.keys())
        for arquivo in arquivos_faltantes:
            print(f'Arquivo faltando: {arquivo}')

    return tabelas


def preencher_campos_vazios(tabelas):
    """
    Preenche campos vazios nas tabelas com zero e aplica pesos aos scouts.
    """
    for nome_tabela, tabela in tabelas.items():
        tabela.fillna(0, inplace=True)

    # Tratamento específico para a tabela "Atletas mercado"
    if 'Atletas mercado' in tabelas:
        tabela_atletas = tabelas['Atletas mercado']
        tabela_atletas.fillna(0, inplace=True)
        tabela_atletas[['minimo_para_valorizar']] = tabela_atletas[['minimo_para_valorizar']].astype(int)
        for scout in SCOUT_WEIGHTS.keys():
            if scout in tabela_atletas:
                tabela_atletas[scout] = tabela_atletas[scout] * SCOUT_WEIGHTS[scout]

    # Tratamento específico para a tabela "Pontuacoes Jogadores"
    if 'Pontuacoes Jogadores' in tabelas:
        tabela_pontuacoes = tabelas['Pontuacoes Jogadores']
        tabela_pontuacoes.fillna(0, inplace=True)
        for scout in SCOUT_WEIGHTS.keys():
            if scout in tabela_pontuacoes:
                tabela_pontuacoes[scout] = tabela_pontuacoes[scout] * SCOUT_WEIGHTS[scout]


def criar_dataframe(tabelas):
    """
    Cria um DataFrame único mesclando as tabelas relevantes e realiza transformações nos dados.
    """
    # Selecionar apenas as tabelas relevantes para o modelo
    tabelas_selecionadas = ['Pontuacoes Jogadores', 'Dados Partidas']
    tabelas_filtradas = {nome_tabela: tabela for nome_tabela, tabela in tabelas.items() if nome_tabela in tabelas_selecionadas}

    # Criar DataFrame com campos da tabela "Pontuacoes Jogadores"
    df = tabelas_filtradas['Pontuacoes Jogadores'].copy()

    # Adicionar campos da tabela "Dados Partidas" ao DataFrame
    df = pd.concat([df, tabelas_filtradas['Dados Partidas']], axis=1)

    # Preencher campos vazios com zero
    df.fillna(0, inplace=True)

    # Renomear campos da tabela "Dados Partidas"
    df.rename(columns={'clube_casa_nome': 'clube_nome', 'clube_visitante_nome': 'clube_nome', 'clube_casa_posicao': 'clube_posicao', 'clube_visitante_posicao': 'clube_posicao', 'aproveitamento_mandante': 'clube_aproveitamento', 'aproveitamento_visitante': 'clube_aproveitamento'}, inplace=True)

    return df


def criar_tabela_dados_rodada_atual(tabelas):
    """
    Cria a tabela "Dados Rodada Atual" com base nas tabelas "Atletas mercado" e "Dados Destaque".
    """
    if 'Atletas mercado' in tabelas and 'Dados Destaque' in tabelas:
        tabela_atletas = tabelas['Atletas mercado']
        tabela_destaque = tabelas['Dados Destaque']

        tabela_rodada_atual = tabela_atletas.copy()

        # Preencher campos da tabela "Dados Rodada Atual" com base na tabela "Dados Destaque"
        tabela_rodada_atual['rodada_dest'] = tabela_rodada_atual['atleta_id'].isin(tabela_destaque['atleta_id'])
        tabela_rodada_atual.loc[tabela_rodada_atual['rodada_dest'], 'total_escal'] = tabela_destaque.loc[tabela_destaque['atleta_id'].isin(tabela_rodada_atual['atleta_id']), 'escalacoes']
        tabela_rodada_atual['rodada_dest'] = tabela_rodada_atual['rodada_dest'].map({True: 'VERDADEIRO', False: 'FALSO'})

        return tabela_rodada_atual

    return None


# Passo 1: Carregar os dados dos arquivos CSV
tabelas = carregar_dados()

# Passo 2: Preencher campos vazios com zero e aplicar pesos aos scouts
preencher_campos_vazios(tabelas)

# Passo 3: Criar DataFrame único com as tabelas relevantes
df = criar_dataframe(tabelas)

# Passo 4: Criar tabela "Dados Rodada Atual"
tabela_rodada_atual = criar_tabela_dados_rodada_atual(tabelas)

if tabela_rodada_atual is not None:
    print('Limpeza dos dados concluída. Os arquivos CSV limpos foram salvos.')
    print('DataFrame consolidado:')
    print(df.head())
    print('Tabela "Dados Rodada Atual":')
    print(tabela_rodada_atual.head())

    # Criar arquivo do Excel com o DataFrame consolidado e a tabela de origem
    nome_arquivo_excel = f'dados_consolidados_{pd.Timestamp.now().strftime("%Y%m%d%H%M%S")}.xlsx'
    writer = pd.ExcelWriter(nome_arquivo_excel, engine='openpyxl')

    # Exportar DataFrame consolidado
    df.to_excel(writer, sheet_name='Dados Consolidados', index=False)

    # Exportar tabela "Dados Rodada Atual"
    tabela_rodada_atual.to_excel(writer, sheet_name='Dados Rodada Atual', index=False)

    # Exportar tabela com campos/tabelas de origem
    tabela_origem = pd.DataFrame({'Campo': df.columns, 'Tabela': df.columns})
    tabela_origem.to_excel(writer, sheet_name='Origem dos Dados', index=False)

    writer._save()

    print(f'Dados exportados para o arquivo: {nome_arquivo_excel}')
else:
    print('Erro ao carregar tabelas. Verifique se todos os arquivos estão presentes ou se há valores ausentes nos dados.')
