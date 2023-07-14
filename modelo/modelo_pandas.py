import pandas as pd

# Carregar os dados das planilhas
jogadores_pontuacao = pd.read_excel('base/jogadores_pontuacao.xlsx')
dados_destaque = pd.read_excel('base/dados_destaque.xlsx')
dados_clubes = pd.read_excel('base/dados_times.xlsx')
dados_partidas = pd.read_excel('base/dados_partidas.xlsx')
dados_rodadas = pd.read_excel('base/dados_rodadas.xlsx')

# Filtrar os dados dos jogadores por posição
goleiros = jogadores_pontuacao[jogadores_pontuacao['posicao_id'] == 1]
laterais = jogadores_pontuacao[jogadores_pontuacao['posicao_id'] == 2]
zagueiros = jogadores_pontuacao[jogadores_pontuacao['posicao_id'] == 3]
meias = jogadores_pontuacao[jogadores_pontuacao['posicao_id'] == 4]
atacantes = jogadores_pontuacao[jogadores_pontuacao['posicao_id'] == 5]
tecnicos = jogadores_pontuacao[jogadores_pontuacao['posicao_id'] == 6]

# Ordenar os jogadores por pontuação na rodada anterior
goleiros = goleiros.sort_values(by='pontuacao', ascending=False)[:2]
laterais = laterais.sort_values(by='pontuacao', ascending=False)[:4]
zagueiros = zagueiros.sort_values(by='pontuacao', ascending=False)[:4]
meias = meias.sort_values(by='pontuacao', ascending=False)[:4]
atacantes = atacantes.sort_values(by='pontuacao', ascending=False)[:4]
tecnicos = tecnicos.sort_values(by='pontuacao', ascending=False)[:2]

# Obter informações adicionais dos jogadores, como clube e apelido
goleiros = goleiros.merge(dados_clubes[['time_id', 'time_nome']], left_on='time_id', right_on='time_id')
laterais = laterais.merge(dados_clubes[['time_id', 'time_nome']], left_on='time_id', right_on='time_id')
zagueiros = zagueiros.merge(dados_clubes[['time_id', 'time_nome']], left_on='time_id', right_on='time_id')
meias = meias.merge(dados_clubes[['time_id', 'time_nome']], left_on='time_id', right_on='time_id')
atacantes = atacantes.merge(dados_clubes[['time_id', 'time_nome']], left_on='time_id', right_on='time_id')
tecnicos = tecnicos.merge(dados_clubes[['time_id', 'time_nome']], left_on='time_id', right_on='time_id')

# Exibir a lista de jogadores recomendados por posição
print('Goleiros:')
print(goleiros[['apelido', 'time_nome', 'pontuacao']])

print('\nLaterais:')
print(laterais[['apelido', 'time_nome', 'pontuacao']])

print('\nZagueiros:')
print(zagueiros[['apelido', 'time_nome', 'pontuacao']])

print('\nMeias:')
print(meias[['apelido', 'time_nome', 'pontuacao']])

print('\nAtacantes:')
print(atacantes[['apelido', 'time_nome', 'pontuacao']])

print('\nTécnicos:')
print(tecnicos[['apelido', 'time_nome', 'pontuacao']])
