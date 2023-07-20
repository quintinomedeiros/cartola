import pandas as pd
import requests
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")  # Ignore warning messages

# Function to calculate the score of scouts by multiplying them by their respective weight
def calculate_scout_score(scouts, scouts_weights):
    if scouts is None:
        return 0

    scouts = {scout: scouts.get(scout, 0) for scout in scouts_weights.keys()}
    score = sum(value * scouts_weights[scout] for scout, value in scouts.items())
    return score

# Dictionary with the weights of scouts
scouts_weights = {
    'ds': 1.2, 'fc': -0.3, 'gc': -3.0, 'ca': -1.0, 'cv': -3.0, 'sg': 5.0, 'dp': 7.0, 'gs': -1.0,
    'pc': -1.0, 'fs': 0.5, 'a': 5.0, 'ft': 3.0, 'fd': 1.2, 'ff': 0.8, 'g': 8.0, 'i': -0.1,
    'pp': -4.0, 'ps': 1.0
}

# Obtain the total number of rounds
url_rounds = 'https://api.cartolafc.globo.com/rodadas'
response_rounds = requests.get(url_rounds)
rounds_data = response_rounds.json()

# Extract round_ids from the list of rounds
round_ids = [round_info['rodada_id'] for round_info in rounds_data]

# Create empty lists to store player attributes
players_data = []

# Iterate over the rounds and retrieve player scores
for round_id in round_ids:
    url_scores = f'https://api.cartolafc.globo.com/atletas/pontuados/{round_id}'
    response_scores = requests.get(url_scores)
    scores_data = response_scores.json()
    if 'atletas' in scores_data:
        players = scores_data['atletas']
        for player_id, player in players.items():
            # Collect player attributes
            scouts = player.get('scout')
            score = calculate_scout_score(scouts, scouts_weights)
            players_data.append({
                'player_id': player_id,
                'player_nickname': player['apelido'],
                'position_id': player['posicao_id'],
                'team_id': player['clube_id'],
                'score': score,
                'entered_field': player['entrou_em_campo'],
                'round_id': round_id
            })

# Create DataFrame with player attributes
df_combined = pd.DataFrame(players_data)

# Get match information
matches_data = []

# Iterate over the rounds
for round_id in round_ids:
    url_matches = f'https://api.cartolafc.globo.com/partidas/{round_id}'
    response_matches = requests.get(url_matches)
    if response_matches.status_code == 200:
        matches_info = response_matches.json()
        if 'partidas' in matches_info:
            for match in matches_info['partidas']:
                home_team_id = match['clube_casa_id']
                away_team_id = match['clube_visitante_id']
                for index, row in df_combined.iterrows():
                    if row['team_id'] == home_team_id and row['round_id'] == round_id:
                        match_date = match['partida_data']
                        home_team_performance = ', '.join(match['aproveitamento_mandante'])
                        home_team_position = match['clube_casa_posicao']
                        away_team_score = match['placar_oficial_visitante']
                        home_team_score = match['placar_oficial_mandante']
                        valid_match = match['valida']
                        home_team_match = True
                        matches_data.append([row['player_id'], row['player_nickname'], row['position_id'],
                                             row['team_id'], row['score'], row['entered_field'],
                                             row['round_id'], home_team_match, match['partida_id'], match_date,
                                             home_team_performance, home_team_position, away_team_score,
                                             home_team_score, valid_match])
                    elif row['team_id'] == away_team_id and row['round_id'] == round_id:
                        match_date = match['partida_data']
                        away_team_performance = ', '.join(match['aproveitamento_visitante'])
                        away_team_position = match['clube_visitante_posicao']
                        away_team_score = match['placar_oficial_visitante']
                        home_team_score = match['placar_oficial_mandante']
                        valid_match = match['valida']
                        home_team_match = False
                        matches_data.append([row['player_id'], row['player_nickname'], row['position_id'],
                                             row['team_id'], row['score'], row['entered_field'],
                                             row['round_id'], home_team_match, match['partida_id'], match_date,
                                             away_team_performance, away_team_position, away_team_score,
                                             home_team_score, valid_match])

# Create DataFrame with player attributes and match information
df_combined = pd.DataFrame(matches_data, columns=[
    'player_id', 'player_nickname', 'position_id', 'team_id', 'score', 'entered_field', 'round_id',
    'home_team_match', 'match_id', 'match_date', 'home_team_performance', 'home_team_position',
    'away_team_score', 'home_team_score', 'valid_match'
])

# Calculate team score in each round
df_combined['team_score'] = df_combined.groupby(['round_id', 'team_id'])['score'].transform('sum')

# Calculate the average score of players in each round
df_combined['avg_team_score'] = df_combined.groupby(['round_id', 'team_id'])['score'].transform('mean')

# Generate the name of the file with the current timestamp
current_time_str = datetime.now().strftime("%Y%m%d%H%M%S")
file_name = f'players_and_matches_{current_time_str}.xlsx'

# Save the DataFrame to an Excel file
df_combined.to_excel(file_name, index=False)
