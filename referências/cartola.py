import requests

# Lista de endpoints a serem consultados
endpoints = [
    'https://api.cartola.globo.com/mercado/status',
    'https://api.cartola.globo.com/atletas/mercado',
    'https://api.cartola.globo.com/atletas/pontuados',
    'https://api.cartolafc.globo.com/ligas?q="mirandada e amigos reunidos"'
    # Adicione os demais endpoints desejados...
]

# Dicionário para armazenar os dados coletados
dados = {}

# Fazer solicitações para cada endpoint e armazenar os dados
for endpoint in endpoints:
    response = requests.get(endpoint)
    if response.status_code == 200:
        endpoint_data = response.json()
        dados[endpoint] = endpoint_data
        print("Dados coletados com sucesso:", endpoint)
    else:
        print("Erro ao coletar dados. Código de status:", response.status_code)

# Exemplo de uso dos dados coletados
# Acessar os dados do endpoint '/atletas/mercado'
atletas_mercado = dados['https://api.cartola.globo.com/atletas/mercado']
# Fazer o processamento dos dados conforme necessário

# Acessar os dados do endpoint '/atletas/pontuados'
atletas_pontuados = dados['https://api.cartola.globo.com/atletas/pontuados']
# Fazer o processamento dos dados conforme necessário

# Acessar os dados do endpoint '/atletas/pontuados'
mercado_status = dados['https://api.cartola.globo.com/mercado/status']

# Acessar os dados do endpoint '/atletas/pontuados'
mirandanda = dados['https://api.cartolafc.globo.com/ligas?q="Mirandada e Amigos Reunidos - 2023"']

# Repita o processo para os demais endpoints

# Agora você possui os dados coletados de todos os endpoints disponíveis

