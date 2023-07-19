import os
import pandas as pd

ARQUIVOS_CSV = {
    'Atletas mercado': 'atletas_mercado.csv',
    'Dados Destaque': 'dados_destaque.csv',
    'Dados Partidas Atual': 'dados_partidas_atual.csv',
    'Dados Partidas Realizadas': 'dados_partidas_realizadas.csv',
    'Dados Times': 'dados_times.csv',
    'Pontuacoes Jogadores': 'pontuacoes_jogadores.csv'
}

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
    # Selecionar apenas as tabelas relevantes para o modelo
    tabelas_selecionadas = ['Atletas mercado', 'Dados Destaque', 'Dados Partidas Atual', 'Dados Partidas Realizadas', 'Dados Times', 'Pontuacoes Jogadores']
    tabelas_filtradas = {nome_tabela: tabela for nome_tabela, tabela in tabelas.items() if nome_tabela in tabelas_selecionadas}

    # Mesclar as tabelas relevantes em um único DataFrame
    df = pd.concat(tabelas_filtradas.values(), keys=tabelas_filtradas.keys(), axis=1)

    # Preencher campos vazios com zero
    df.fillna(0, inplace=True)

    # Aplicar pesos aos scouts na tabela "Pontuacoes Jogadores"
    if 'Pontuacoes Jogadores' in tabelas_filtradas:
        tabela_pontuacoes = df['Pontuacoes Jogadores']
        for scout, peso in SCOUT_WEIGHTS.items():
            if scout in tabela_pontuacoes:
                tabela_pontuacoes[scout] = tabela_pontuacoes[scout] * peso

    return df


# Passo 1: Carregar os dados dos arquivos CSV
tabelas = carregar_dados()

# Passo 2: Preencher campos vazios com zero
preencher_campos_vazios(tabelas)

# Passo 3: Criar DataFrame único com as tabelas relevantes
df = criar_dataframe(tabelas)

# Verificar se todas as tabelas foram carregadas corretamente após o preenchimento
tabelas_completas = True
for nome_tabela, tabela in tabelas.items():
    if tabela.isna().any().any():
        print(f'Valores ausentes encontrados na tabela: {nome_tabela}')
        colunas_ausentes = tabela.columns[tabela.isna().any()].tolist()
        print(f'Colunas com valores ausentes: {colunas_ausentes}')
        tabelas_completas = False

if tabelas_completas:
    print('Limpeza dos dados concluída. Os arquivos CSV limpos foram salvos.')

    tabelas_incluidas = ['Atletas mercado', 'Dados Destaque', 'Dados Partidas Atual', 'Dados Partidas Realizadas', 'Dados Times', 'Pontuacoes Jogadores']
    campos_incluidos = {
        'Atletas mercado': ['atleta_id', 'rodada_id', 'status_id'],
        'Dados Destaque': ['atleta_id', 'preco_editorial', 'escalacoes'],
        'Dados Partidas Atual': ['rodada_id', 'partida_id', 'partida_data', 'clube_casa_id', 'clube_casa_posicao', 'aproveitamento_mandante', 'clube_visitante_id', 'clube_visitante_posicao', 'aproveitamento_visitante', 'valida'],
        'Dados Partidas Realizadas': ['rodada_id', 'partida_id', 'partida_data', 'clube_casa_id', 'clube_casa_posicao', 'aproveitamento_mandante', 'clube_visitante_id', 'clube_visitante_posicao', 'aproveitamento_visitante', 'placar_oficial_mandante', 'placar_oficial_visitante', 'valida'],
        'Dados Times': ['clube_id', 'clube_nome', 'abreviacao'],
        'Pontuacoes Jogadores': ['atleta_id', 'apelido', 'posicao_id', 'clube_id', 'entrou_em_campo', 'rodada_id', 'CA', 'DS', 'FC', 'FF', 'FD', 'FS', 'I', 'SG', 'A', 'G', 'DE', 'GS', 'V', 'PS', 'FT', 'PP', 'DP', 'CV', 'PC', 'GC', 'pontuacao']
    }

    campos_dataframe = []
    descricao_campos = []

    for nome_tabela in tabelas_incluidas:
        campos = campos_incluidos[nome_tabela]
        campos_dataframe.extend(campos)

        if nome_tabela == 'Atletas mercado':
            descricao_campos.extend([
                'identificador do atleta no CartolaFC',
                'identificador da rodada',
                'identificador do id do atleta na rodada atual'
            ])

        elif nome_tabela == 'Dados Destaque':
            descricao_campos.extend([
                'identificador do atleta no CartolaFC',
                'valor em cartoletas para escalação do atleta no CartolaFC',
                'total de escalações do atleta nos times participantes do CartolaFC'
            ])

        elif nome_tabela == 'Dados Partidas Atual':
            descricao_campos.extend([
                'identificador da rodada',
                'identificador da partida',
                'data de realização da partida',
                'identificado do clube mandante',
                'posição atual do clube mandante no campeonato brasileiro',
                'últimos cinco resultados do clube mandante, sendo "v" para vitória, "e" para empate e "d" para derrota',
                'identificado do clube visitante',
                'posição atual do clube visitante no campeonato brasileiro',
                'últimos cinco resultados do clube visitante, sendo "v" para vitória, "e" para empate e "d" para derrota',
                'informação se a partida será válida (VERDADEIRO) ou não (FALSO) para a pontuação na rodada. Se não for válida (FALSO), os atletas dos times não pontuarão na rodada'
            ])

        elif nome_tabela == 'Dados Partidas Realizadas':
            descricao_campos.extend([
                'identificador da rodada',
                'identificador da partida',
                'data de realização da partida',
                'identificado do clube mandante',
                'posição atual do clube mandante no campeonato brasileiro',
                'últimos cinco resultados do clube mandante, sendo "v" para vitória, "e" para empate e "d" para derrota',
                'identificado do clube visitante',
                'posição atual do clube visitante no campeonato brasileiro',
                'últimos cinco resultados do clube visitante, sendo "v" para vitória, "e" para empate e "d" para derrota',
                'total de gols marcados na partida pelo time mandante',
                'total de gols marcados na partida pelo time visitante',
                'informação se a partida será válida (VERDADEIRO) ou não (FALSO) para a pontuação na rodada. Se não for válida (FALSO), os atletas dos times não pontuarão na rodada'
            ])

        elif nome_tabela == 'Dados Times':
            descricao_campos.extend([
                'identificador do time no CartolaFC',
                'nome do clube',
                'abreviação do nome do clube'
            ])

        elif nome_tabela == 'Pontuacoes Jogadores':
            descricao_campos.extend([
                'identificador do atleta',
                'apelido do atleta',
                'identificador da posição do atleta',
                'identificador do time',
                'situação do jogador na rodada se entrou em campo (VERDADEIRO) ou não (FALSO)',
                'identificador da rodada',
                'cartão amarelo - tem peso -1.0',
                'desarme - tem peso +1.2',
                'falta cometida - tem peso -0.3',
                'finalização para fora - tem peso +0.8',
                'finalização defendida - tem peso +1.0',
                'falta sofrida - tem peso +0.5',
                'impedimento - tem peso -0.1',
                'sem gol - tem peso +5.0',
                'assistência - tem peso +5.0',
                'gol - tem peso +8.0',
                'defesa - tem peso 1.0',
                'gol sofrido - tem peso -1.0',
                'vitória - tem peso +1.0',
                'penalti sofrido - tem peso +1.0',
                'finalização na trave - tem peso +3.0',
                'penalti perdido - tem peso -4.0',
                'defesa de penalti - tem peso +7.0',
                'cartão vermelho - tem peso -3.0',
                'penalti cometido - tem peso -1.0',
                'gol contra - tem peso -3.0',
                'total de pontos obtidos na rodada obtido pelo somatório das frequências dos scouts pelo seu respectivo peso'
            ])

    print(f'O dataframe é formado pelos seguintes campos: {"; ".join(campos_dataframe)}\n')

    for campo, descricao in zip(campos_dataframe, descricao_campos):
        print(f'- {campo}: {descricao}')

else:
    print('Erro ao carregar tabelas. Verifique se todos os arquivos estão presentes ou se há valores ausentes nos dados.')
