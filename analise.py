import pandas as pd

df = pd.read_parquet("resultado.parquet")

# cria uma linha para cada jogador encontrado em cada partida
df_players_exploded = df.explode('players').reset_index(drop=True)

# transforma o dicionário da coluna players em colunas reais
df_details = pd.json_normalize(df_players_exploded['players'])

df_full = df_players_exploded[['game', 'map']].join(df_details)

# ANÁLISE 1: Ranking Geral de Kills 
def rank_kills():
    ranking_kills = df_full.groupby('current_name')['kills'].sum().sort_values(ascending=False).head(5)
    
    return ranking_kills

# ANÁLISE 2: Mapas com mais kills
def map_kills():
    map_stats = df.groupby('map')['total_kills'].sum().sort_values(ascending=False)

    return map_stats

# ANÁLISE 3: Armas mais utilizadas nos servidores
def favorite_weapons():
    weapons = df_full[df_full['favorite_weapon'] != "none"]
    weapon_stats = weapons['favorite_weapon'].value_counts().head(3)

    return weapon_stats

if __name__ == "__main__":
    print("=== ANÁLISE 1: TOP 5 KILLERS ===")
    print(rank_kills())

    print("=== ANÁLISE 2: MAPAS COM MAIS MORTES ===")
    print(map_kills())

    print("=== ANÁLISE 3: ARMAS PREFERIDAS ===")
    print(favorite_weapons())