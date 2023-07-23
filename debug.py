import requests

def calcular_pontuacao_scout(scouts):
    pontuacao_ponderada = 0.0
    peso_scouts = {
        'DS': 1.5,
        'FC': -0.5,
        'GC': -6.0,
        'CA': -2.0,
        'CV': -5.0,
        'SG': 5.0,
        'DP': 7.0,
        'GS': -3.0,
        'PC': 5.0,
        'FS': 0.5,
        'A': 5.0,
        'FT': 3.5,
        'FD': 1.0,
        'FF': 0.7,
        'G': 8.0,
        'I': -0.5,
        'PP': -0.8,
        'PS': 0.5,
    }
    
    for scout, valor in scouts.items():
        peso = peso_scouts.get(scout, 0.0)
        pontuacao_ponderada += valor * peso

    return pontuacao_ponderada

def calcular_pontuacao_atleta(atleta_id):
    url_atleta = f'https://api.cartolafc.globo.com/atletas/{atleta_id}/pontuacao'
    resposta_atleta = requests.get(url_atleta)
    scouts_atleta = resposta_atleta.json()

    if not scouts_atleta or 'scouts' not in scouts_atleta:
        return None

    scouts = scouts_atleta['scouts']
    print(f"Atleta ID: {atleta_id}, Scouts da API: {scouts}")

    pontuacao_total = sum(scouts.values())
    pontuacao_ponderada = calcular_pontuacao_scout(scouts)

    return pontuacao_total, pontuacao_ponderada

# Testar com alguns atletas específicos
atletas_ids = [104502, 104580, 104640]

for atleta_id in atletas_ids:
    resultado = calcular_pontuacao_atleta(atleta_id)
    if resultado:
        pontuacao_total, pontuacao_ponderada = resultado
        print(f"Atleta ID: {atleta_id}, Pontuação Total: {pontuacao_total}, Pontuação Ponderada: {pontuacao_ponderada}")
    else:
        print(f"Atleta ID: {atleta_id}, Não foi possível calcular a pontuação.")

