import requests
import json
import os
from tqdm import tqdm
import itertools
from multiprocessing import Pool


# Link for list of heroes and artifacts
# https://static.smilegatemegaport.com/gameRecord/epic7/epic7_hero.json
# https://static.smilegatemegaport.com/gameRecord/epic7/epic7_artifact.json

def update_json():
    hero = requests.get("https://static.smilegatemegaport.com/gameRecord/epic7/epic7_hero.json")
    artifact = requests.get("https://static.smilegatemegaport.com/gameRecord/epic7/epic7_artifact.json")
    # write the json files
    if not os.path.exists("data_collection/hero_artifact"):
        os.makedirs("data_collection/hero_artifact")
    with open("data_collection/hero_artifact/hero.json", "wb") as f:
        f.write(hero.content)
    with open("data_collection/hero_artifact/artifact.json", "wb") as f:
        f.write(artifact.content)


def load_matches(regions: list):
    cores = 1  # Core should be 1 to not mess up when writing to the file
    if not os.path.exists("data_collection/matches"):
        os.makedirs("data_collection/matches")
    for region in regions:
        with open(f"data_collection/processed/{region}.json", "r", encoding='utf-8') as f:
            player_data = [json.loads(line) for line in f]
        for player in tqdm(player_data, desc=f"Loading {region} matches"):
            player_id = player['nick_no']
            params = (
                ('nick_no', player_id),
                ('world_code', f'world_{region}'),
                ('lang', 'en'),
                ('season_code', ''),
            )
            r = requests.post('https://epic7.gg.onstove.com/gameApi/getBattleList', params=params)
            try:
                r.raise_for_status()
            except requests.exceptions.ConnectionError as e:
                raise SystemExit(e)
            except requests.exceptions.HTTPError as e:
                raise SystemExit(e)
            match_data = json.loads(r.text)
            if match_data['return_code'] != 0 or match_data['result_body']['return_code'] != 0:
                with open(f"data_collection/matches/error.log", "a", encoding='utf-8') as f:
                    f.write(json.dumps(
                        player) + f"Region: {region} Error: {match_data['return_code']} and {match_data['result_body']['return_code']}\n")
                continue
            matches_list = match_data['result_body']['battle_list']
            if matches_list is None:
                with open(f"data_collection/matches/error.log", "a", encoding='utf-8') as f:
                    f.write(json.dumps(player) + f"Region: {region} Error: No matches found\n")
                continue
            items = zip(matches_list, [region] * matches_list.__len__())
            with Pool(cores) as p:
                p.starmap(match_func, items)
    print("Done!")


def match_func(match, region):
    enemy_team = json.loads('{' + match['teamBettleInfoenemy'] + '}')
    player_team = json.loads('{' + match['teamBettleInfo'] + '}')
    iswin = match['iswin']
    for hero in itertools.chain(enemy_team['my_team'], player_team['my_team']):
        hero.pop('attack_damage')
        hero.pop('receive_damage')
        hero.pop('recovery')
        hero.pop('mvp_point')
        hero.pop('respawn')
        hero.pop('mvp')
        hero.pop('kill_count')
        hero.pop('grade')
        hero.pop('awaken_grade')
        hero.pop('attribute_cd')
        hero.pop('level')
        hero.pop('job_cd')
    match_dict = {'player_team': player_team, 'enemy_team': enemy_team, 'iswin': iswin}
    with open(f"data_collection/matches/{region}.json", "a", encoding='utf-8') as f:
        f.write(json.dumps(match_dict) + "\n")
