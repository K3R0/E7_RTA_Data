import requests
import json
import os
from tqdm import tqdm
from multiprocessing import Pool


# API links
# https://static.smilegatemegaport.com/gameRecord/epic7/epic7_user_world_asia.json
# https://static.smilegatemegaport.com/gameRecord/epic7/epic7_user_world_global.json
# https://static.smilegatemegaport.com/gameRecord/epic7/epic7_user_world_eu.json
# https://static.smilegatemegaport.com/gameRecord/epic7/epic7_user_world_jpn.json
# https://static.smilegatemegaport.com/gameRecord/epic7/epic7_user_world_kor.json

# Update the local json files from the API
def update_json():
    asia = requests.get("https://static.smilegatemegaport.com/gameRecord/epic7/epic7_user_world_asia.json")
    global_ = requests.get("https://static.smilegatemegaport.com/gameRecord/epic7/epic7_user_world_global.json")
    eu = requests.get("https://static.smilegatemegaport.com/gameRecord/epic7/epic7_user_world_eu.json")
    jpn = requests.get("https://static.smilegatemegaport.com/gameRecord/epic7/epic7_user_world_jpn.json")
    kor = requests.get("https://static.smilegatemegaport.com/gameRecord/epic7/epic7_user_world_kor.json")
    # write the json files
    if not os.path.exists("data_collection/unprocessed"):
        os.makedirs("data_collection/unprocessed")
    with open("data_collection/unprocessed/asia.json", "wb") as f:
        f.write(asia.content)
    with open("data_collection/unprocessed/global.json", "wb") as f:
        f.write(global_.content)
    with open("data_collection/unprocessed/eu.json", "wb") as f:
        f.write(eu.content)
    with open("data_collection/unprocessed/jpn.json", "wb") as f:
        f.write(jpn.content)
    with open("data_collection/unprocessed/kor.json", "wb") as f:
        f.write(kor.content)


# Filter list of player to get only emperor or legend players
def load_players(cores=1):
    if not os.path.exists("data_collection/processed"):
        os.makedirs("data_collection/processed")
    for region in ["asia", "global", "eu", "jpn", "kor"]:
        with open(f"data_collection/unprocessed/{region}.json", "r", encoding='utf-8') as f:
            data = json.load(f)
        player_count = data['users'].__len__()
        # If the file already exists, resume from the last saved player
        if os.path.exists(f"data_collection/processed/{region}.json"):
            with open(f"data_collection/processed/{region}.json", "r", encoding='utf-8') as f:
                processed_data = [json.loads(line) for line in f]
            last_player = processed_data[-1]
            start = data['users'].index(last_player)
        else:
            start = -1
        item_number = player_count - (start + 1)
        items = zip(data['users'][start + 1:], [region] * item_number)
        with Pool(cores) as p:
            for _ in tqdm(p.istarmap(func, items), total=item_number, desc=f"Filtering {region} players"):
                pass
    print("Done!")


def func(player, region):
    player_no = player['nick_no']
    params = (
        ('nick_no', player_no),
        ('world_code', f'world_{region}'),
        ('lang', 'en'),
    )
    r = requests.post('https://epic7.gg.onstove.com/gameApi/getUserInfo', params=params)
    try:
        r.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise SystemExit(e)
    except requests.exceptions.HTTPError as e:
        raise SystemExit(e)

    content = json.loads(r.text)
    if content['return_code'] != 0:
        print(f"Player {player_no} Error: {content['return_code']}")
        with open("data_collection/processed/error.log", "a", encoding='utf-8') as f:
            f.write(json.dumps(player) + f"Region: {region} Error: {content['return_code']}\n")
        return
    tier = content['result_body']['grade_code'].lower()
    if tier == "emperor" or tier == "legend":
        with open(f"data_collection/processed/{region}.json", "a", encoding='utf-8') as f:
            f.write(json.dumps(player) + "\n")
