import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from datetime import datetime

# Passo 1: Carregar os dados das planilhas
df_jogadores = pd.read_excel('base/jogadores_pontuacao.xlsx')
df_destaque = pd.read_excel('base/dados_destaque.xlsx')
df_times = pd.read_excel('base/dados_times.xlsx')
df_partidas = pd.read_excel('base/dados_partidas.xlsx')
df_rodadas = pd.read_excel('base/dados_rodadas.xlsx')

# Passo 2: Pré-processar os dados (realizar as transformações e tratamentos necessários)

# Passo 3: Dividir os dados em conjunto de treinamento e teste
X = df_jogadores[['pt_scout_ca', 'pt_scout_cv', 'pt_scout_dp', 'pt_scout_fc', 'pt_scout_ff', 'pt_scout_fs', 'pt_scout_ft',
                  'pt_scout_g', 'pt_scout_i', 'pt_scout_ds', 'pt_scout_sg', 'pt_scout_gc', 'pt_scout_gs', 'pt_scout_ps',
                  'pt_scout_pc', 'pt_scout_a', 'pt_scout_fd', 'pt_scout_pp']]
y = df_jogadores['pontuacao']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Passo 5: Escolher um algoritmo de aprendizado de máquina e treinar o modelo
model = LinearRegression()
model.fit(X_train, y_train)

# Passo 7: Avaliar o desempenho do modelo
score = model.score(X_test, y_test)
print('Acurácia do modelo:', score)

# Passo 8: Identificar a próxima rodada
data_atual = datetime.now().date()
df_rodadas['rodada_fim'] = pd.to_datetime(df_rodadas['rodada_fim'])
proxima_rodada = df_rodadas[df_rodadas['rodada_fim'].dt.date > data_atual]['rodada_id'].min()

# Passo 9: Fazer previsões para os melhores jogadores em cada posição
df_goleiros = df_jogadores[df_jogadores['posicao_id'] == 1].copy()
df_laterais = df_jogadores[df_jogadores['posicao_id'] == 2].copy()
df_zagueiros = df_jogadores[df_jogadores['posicao_id'] == 3].copy()
df_meias = df_jogadores[df_jogadores['posicao_id'] == 4].copy()
df_atacantes = df_jogadores[df_jogadores['posicao_id'] == 5].copy()
df_tecnicos = df_jogadores[df_jogadores['posicao_id'] == 6].copy()

dfs = [df_goleiros, df_laterais, df_zagueiros, df_meias, df_atacantes, df_tecnicos]
df_recomendacoes = pd.DataFrame()

for df_posicao in dfs:
    X_posicao = df_posicao[['pt_scout_ca', 'pt_scout_cv', 'pt_scout_dp', 'pt_scout_fc', 'pt_scout_ff', 'pt_scout_fs',
                            'pt_scout_ft', 'pt_scout_g', 'pt_scout_i', 'pt_scout_ds', 'pt_scout_sg', 'pt_scout_gc',
                            'pt_scout_gs', 'pt_scout_ps', 'pt_scout_pc', 'pt_scout_a', 'pt_scout_fd', 'pt_scout_pp']]
    predictions_posicao = model.predict(X_posicao)
    df_posicao['pontuacao_prevista'] = predictions_posicao
    df_posicao = df_posicao.nlargest(4, 'pontuacao_prevista')
    df_recomendacoes = pd.concat([df_recomendacoes, df_posicao])

# Salvar o DataFrame df_recomendacoes em um arquivo Excel com o nome contendo a rodada e o momento da gravação
momento_gravacao = datetime.now().strftime('%Y%m%d_%H%M%S')
nome_arquivo = f'recomendacao_rodada_{proxima_rodada}_{momento_gravacao}.xlsx'
df_recomendacoes.to_excel(nome_arquivo, index=False)

# Agora você tem o DataFrame df_recomendacoes com as recomendações dos melhores jogadores em cada posição para a próxima rodada,
# e o arquivo Excel 'recomendacao_rodada_{proxima_rodada}_{momento_gravacao}.xlsx' foi gerado com os resultados.
