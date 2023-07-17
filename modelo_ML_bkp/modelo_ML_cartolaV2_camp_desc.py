import os
import pandas as pd

ARQUIVOS_CSV = {
    'Atletas mercado': 'atletas_mercado.csv',
    'Dados Destaque': 'dados_destaque.csv',
    'Dados Partidas Atual': 'dados_partidas_atual.csv',
    'Dados Partidas Realizadas': 'dados_partidas_realizadas.csv',
    'Dados Times': 'dados_times.csv',
    'Pontuacoes Jogadores': 'pontuacoes_jogadores.csv',
    'Posicoes': 'posicoes.csv',
    'Status': 'status.csv'
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
    'PI': -0.1,
    'A': 5.0,
    'FT': 3.0,
    'FD': 1.2,
    'FF': 0.8,
    'G': 8.0,
    'I': -0.1,
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


# Passo 1: Carregar os dados dos arquivos CSV
tabelas = carregar_dados()

# Passo 2: Preencher campos vazios com zero
preencher_campos_vazios(tabelas)

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

    for nome_tabela, tabela in tabelas.items():
        print(f'{nome_tabela}:')
        print(tabela.head())
        
        # Descrições das tabelas
        if nome_tabela == 'Atletas mercado':
            print('Esta tabela contém informações sobre a situação dos atletas na rodada atual.')
            print('Campos disponíveis: atleta_id; rodada_id; status_id; variacao_num; minimo_para_valorizar;')
            '''
            Descrição dos campos da tabela "Atletas mercado":
            atleta_id: identificador do atleta no CartolaFC
            rodada_id: identificador da rodada
            status_id: identificador do id do atleta na rodada atual
            variacao_num: ganho ou perda de pontos considerando as duas últimas rodadas do atleta
            minimo_para_valorizar: pontuação mínima para que o atleta tenha seu preço valorizado
            '''    
        
        if nome_tabela == 'Dados Destaque':
            print('Esta tabela contém informações sobre os jogadores mais escalados na rodada atual.')
            print('Campos disponíveis: atleta_id, apelido, clube_id, time_abr, posicao_abreviacao, preco_editorial, escalacoes')
            '''
            Descrição dos campos da tabela "Dados Destaque":
            atleta_id: identificador do atleta no CartolaFC
            clube_id: identificador do clube do atleta
            time_abr: abreviação do nome do clube do atleta
            preco_editorial: valor em cartoletas para escalação do atleta no CartolaFC
            escalacoes: total de escalações do atleta nos times participantes do CartolaFC
            '''    
        
        if nome_tabela == 'Dados Partidas Atual':
            print('Esta tabela contém informações sobre a as partidas que serão realizadas na rodada atual.')
            print('Campos disponíveis: rodada_id, partida_id, partida_data, clube_casa_id, clube_casa_posicao, aproveitamento_mandante,clube_visitante_id, clube_visitante_posicao, aproveitamento_visitante e valida')
            '''
            Descrição dos campos da tabela "Dados Partidas Atual":
            rodada_id: identificador da rodada
            partida_id: identificador da partida
            partida_data: data de realização da partida
            clube_casa_id: identificado do clube mandante
            clube_casa_posicao: posição atual do clube mandante no campeonato brasileiro
            aproveitamento_mandante: últimos cinco resultados do clube mandante, sendo 'v' para vitória, 'e' para empate e 'd' para derrota
            clube_visitante_id: identificado do clube visitante
            clube_visitante_posicao: posição atual do clube visitante no campeonato brasileiro
            aproveitamento_visitante: últimos cinco resultados do clube visitante, sendo 'v' para vitória, 'e' para empate e 'd' para derrota
            valida: informação se a partida será válida (VERDADEIRO) ou não (FALSO) para a pontuação na rodada. Se não for válida (FALSO), os atletas dos times não pontuarão na rodada
            '''    

        if nome_tabela == 'Dados Partidas Realizadas':
            print('Esta tabela contém informações sobre a as partidas que realizadas até a última rodada finalizada.')
            print('Campos disponíveis: rodada_id, partida_id, partida_data, clube_casa_id, clube_casa_posicao, aproveitamento_mandante,clube_visitante_id, clube_visitante_posicao,aproveitamento_visitante, placar_oficial_mandante, placar_oficial_visitante e valida')
            '''
            Descrição dos campos da tabela "Dados Partidas Realizadas":
            rodada_id: identificador da rodada
            partida_id: identificador da partida
            partida_data: data de realização da partida
            clube_casa_id: identificado do clube mandante
            clube_casa_posicao: posição atual do clube mandante no campeonato brasileiro
            aproveitamento_mandante: últimos cinco resultados do clube mandante, sendo 'v' para vitória, 'e' para empate e 'd' para derrota
            clube_visitante_id: identificado do clube visitante
            clube_visitante_posicao: posição atual do clube visitante no campeonato brasileiro
            aproveitamento_visitante: últimos cinco resultados do clube visitante, sendo 'v' para vitória, 'e' para empate e 'd' para derrota
            placar_oficial_mandante: total de gols marcados na partida pelo time mandante
            placar_oficial_visitante: total de gols marcados na partida pelo time visitante 
            valida: informação se a partida será válida (VERDADEIRO) ou não (FALSO) para a pontuação na rodada. Se não for válida (FALSO), os atletas dos times não pontuarão na rodada            
            '''    

        if nome_tabela == 'Dados Times':
            print('Esta tabela contém informações sobre os times participantes do CartolaFC 2023.')
            print('clube_id; clube_nome; abreviacao')
            '''
            Descrição dos campos da tabela "Atletas mercado":
            clube_id: identificador do time no CartolaFC
            clube_nome: nome do clube
            abreviacao: abreviação do nome do clube  
            '''    

        if nome_tabela == 'Pontuacoes Jogadores':
            print('Esta tabela contém informações sobre os jogadores e suas pontuações detalhadas nas rodadas já finalizadas.')
            print('Campos disponíveis: atleta_id, apelido, posicao_id, clube_id, entrou_em_campo, rodada_id, CA, DS, FC, FF, FD, FS, I, SG, A, G, DE,GS, V, PS, FT, PP, DP, CV, PC, GC, pontuacao')
            '''
            Descrição dos campos da tabela "Pontuacoes Jogadores":
            atleta_id: indentificador do atleta
            apelido: apelido do atleta
            posicao_id: identificador da posição do atleta
            clube_id: identificador do time
            entrou_em_campo: situação do jogador na rodada se entrou em campo (VERDADEIRO) ou não (FALSO)
            rodada_id: identificador da rodada
            CA: cartão amarelo - tem peso -1.0
            DS: desarme - tem peso + 1.2
            FC: falta cometida - tem peso -0.3
            FF: finalização para fora - tem peso +0.8
            FD: finalização defendida - tem peso +1.0
            FS: falta sofrida - tem peso +0.5
            I: impedimento - tem peso -0.1
            SG: sem gol - tem peso +5.0
            A: assistência - tem peso +5.0
            G: gol - tem peso +8.0
            DE: defesa - tem peso 1.0
            GS: gol sofrido - tem peso -1.0
            V: vitória - tem peso +1.0
            PS: penalti sofrido - tem peso +1.0
            FT: finalização na trave - tem peso +3.0
            PP: penalti perdido - tem peso -4.0
            DP: defesa de penalti - tem peso +7.0
            CV: cartão vermelho - tem peso -3.0
            PC: penalti cometido - tem peso -1.0
            GC: gol contra - tem peso -3.0
            pontuacao: total de pontos obtidos na rodada obtido pelo somatório das frequências dos scouts pelo seu respectivo peso
            '''    

else:
    print('Erro ao carregar tabelas. Verifique se todos os arquivos estão presentes ou se há valores ausentes nos dados.')
