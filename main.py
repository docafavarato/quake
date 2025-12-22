import json
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from collections import Counter

# cria o objeto do jogador apenas com o ID
def create_player(id):
    return {
        "id": int(id),
        "current_name": "",
        "old_names": [],
        "kills": 0,
        "deaths": 0,
        "suicides": 0,
        "used_weapons": [],
        "collected_items": []
    }

# cria o objeto do jogo
def create_game(index, map, total_kills, players):
    return {
        "game": index,
        "map": map,
        "total_kills": total_kills,
        "players": players
    }

# verifica, com base no ID, se um jogador já existe na lista de jogadores
def player_exists(id, players):
    for player in players:
        if id == player["id"]:
            return True
    return False

# faz o parse do arquivo
def parse_log(filename):
    with open(filename, "r") as f:
        data = f.read()

    # separa os jogos com base no texto de finalização
    games = data.split("ShutdownGame:")

    result = [] 

    index = 1
    for game in games:
        players = []

        # separa o jogo em linhas
        lines = game.split("\n")
        for line in lines:

            # pega o nome do mapa
            if "InitGame: " in line:
                game_map = line.split("mapname\\")[1].split("\\")[0]

            # cria o objeto de cada jogador e adiciona à lista de jogadores
            if "ClientConnect: " in line:
                id = int(line.split("ClientConnect: ")[1])
                if not player_exists(id, players):
                    players.append(create_player(id))

            # mapeia mudanças de nome
            if "ClientUserinfoChanged: " in line:
                id = int(line.split("ClientUserinfoChanged: ")[1].split(" n\\")[0])
                name = line.split("n\\")[1].split("\\")[0]

                for player in players:
                    if player["id"] == id:
                        if player["current_name"] == "":
                            player["current_name"] = name
                        elif player["current_name"] != name:
                            if player["current_name"] not in player["old_names"]:
                                player["old_names"].append(player["current_name"])
                            
                            player["current_name"] = name

                            if name in player["old_names"]:
                                player["old_names"].remove(name)

            # mapeia as kills, mortes, suícidios e armas utilizadas
            if "Kill: " in line:
                if "<world>" in line:
                    for player in players:
                        if player["current_name"] == line.split("killed ")[1].split(" by")[0]:
                            player["deaths"] += 1
                
                else:
                    id_killer =  int(line.split("Kill: ")[1].split()[0])
                    id_killed = int(line.split("Kill: ")[1].split()[1].split()[0])
                    weapon = line.split("by ")[1]
                    
                    if id_killer != id_killed:
                        for player in players:
                            if player["id"] == id_killer:
                                player["kills"] += 1
                                player["used_weapons"].append(weapon)
                            elif player["id"] == id_killed:
                                player["deaths"] += 1
                    
                    else:
                        for player in players:
                            if player["id"] == id_killer:
                                player["deaths"] += 1
                                player["suicides"] += 1
                                player["used_weapons"].append(weapon)
            
            # mapeia os itens coletados. Optei por não deixar a lista com itens repetidos
            if "Item: " in line:
                id = int(line.split("Item: ")[1].split()[0])
                item = line.split("Item: ")[1].split()[1]

                for player in players:
                    if player["id"] == id:
                        if item not in player["collected_items"]:
                            player["collected_items"].append(item)


        # mapeia o total de kills da partida e a arma favorita de cada jogador.
        total_kills = 0
        for player in players:
            if player["used_weapons"]:
                player["favorite_weapon"] = Counter(player["used_weapons"]).most_common(1)[0][0]
            else:
                player["favorite_weapon"] = "none"
            del player["used_weapons"]

            total_kills += player["kills"]


        # adiciona o objeto do jogo à lista
        result.append(create_game(index, game_map, total_kills, players))

        index += 1

    # salva o resultado em um arquivo json
    with open("resultado.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    create_parquet(result)

# cria o arquivo parquet com base nos resultados do parser
def create_parquet(obj):
    df = pd.DataFrame(obj)
    schema = pa.schema([
        ('game', pa.int32()),
        ('map', pa.string()),
        ('total_kills', pa.int32()),
        ('players', pa.list_(pa.struct([
            ('id', pa.int32()),
            ('current_name', pa.string()),
            ('old_names', pa.list_(pa.string())),
            ('kills', pa.int32()),
            ('deaths', pa.int32()),
            ('suicides', pa.int32()),
            ('favorite_weapon', pa.string()),
            ('collected_items', pa.list_(pa.string()))
        ])))
    ])

    try:
        table = pa.Table.from_pandas(df, schema=schema)
        
        pq.write_table(table, 'resultado.parquet')
        
    except Exception as e:
        print(f"Erro ao gerar Parquet: {e}")

if __name__ == "__main__":
    parse_log("Quake 1.log")