import json
import pandas as pd
import itertools
import os
from sklearn.preprocessing import LabelEncoder
import numpy as np
from tqdm import tqdm


def data_preprocessing():
    l = []
    # Load original data
    with open("data_collection/matches/asia.json", "r", encoding='utf-8') as f:
        asia = [json.loads(line) for line in f]
    with open("data_collection/matches/global.json", "r", encoding='utf-8') as f:
        global_ = [json.loads(line) for line in f]
    with open("data_collection/matches/eu.json", "r", encoding='utf-8') as f:
        eu = [json.loads(line) for line in f]
    with open("data_collection/matches/jpn.json", "r", encoding='utf-8') as f:
        jpn = [json.loads(line) for line in f]
    with open("data_collection/matches/kor.json", "r", encoding='utf-8') as f:
        kor = [json.loads(line) for line in f]
    for item in itertools.chain(asia, global_, eu, jpn, kor):
        if len(item['player_team']['my_team']) == 0:
            continue
        player_non_banned = []
        enemy_non_banned = []
        for i in range(5):
            if item['player_team']['my_team'][i]['position'] != 0:
                player_non_banned.append(i)
            if item['enemy_team']['my_team'][i]['position'] != 0:
                enemy_non_banned.append(i)
        data = {}
        for i in range(len(player_non_banned)):
            while len(item['player_team']['my_team'][player_non_banned[i]]['equip']) < 3:
                item['player_team']['my_team'][player_non_banned[i]]['equip'].append('null')
            data.update({
                'is_win': item['iswin'],
                f'ally_hero_{i}': item['player_team']['my_team'][player_non_banned[i]]['hero_code'],
                f'ally_hero_{i}_art': item['player_team']['my_team'][player_non_banned[i]]['artifact'],
                f'ally_hero_{i}_set1': item['player_team']['my_team'][player_non_banned[i]]['equip'][0],
                f'ally_hero_{i}_set2': item['player_team']['my_team'][player_non_banned[i]]['equip'][1],
                f'ally_hero_{i}_set3': item['player_team']['my_team'][player_non_banned[i]]['equip'][2]
            })
        for i in range(len(enemy_non_banned)):
            while len(item['enemy_team']['my_team'][enemy_non_banned[i]]['equip']) < 3:
                item['enemy_team']['my_team'][enemy_non_banned[i]]['equip'].append('null')
            data.update({
                f'enemy_hero_{i}': item['enemy_team']['my_team'][enemy_non_banned[i]]['hero_code'],
                f'enemy_hero_{i}_art': item['enemy_team']['my_team'][enemy_non_banned[i]]['artifact'],
                f'enemy_hero_{i}_set1': item['enemy_team']['my_team'][enemy_non_banned[i]]['equip'][0],
                f'enemy_hero_{i}_set2': item['enemy_team']['my_team'][enemy_non_banned[i]]['equip'][1],
                f'enemy_hero_{i}_set3': item['enemy_team']['my_team'][enemy_non_banned[i]]['equip'][2]
            })
        l.append(data)
    df = pd.DataFrame(l)
    if not os.path.exists("data_analysis/data_preprocessing"):
        os.makedirs("data_analysis/data_preprocessing")
    df.to_pickle("data_analysis/data_preprocessing/non_augmented_data.pkl")
    print(df['is_win'].value_counts(normalize=True))

def label_encoding():
    df = pd.read_pickle("data_analysis/data_preprocessing/non_augmented_data.pkl")
    heroes_label = LabelEncoder()
    artifacts_label = LabelEncoder()
    sets_label = LabelEncoder()
    win_label = LabelEncoder()
    heroes_label.fit(pd.concat([df['ally_hero_0'], df['ally_hero_1'], df['ally_hero_2'], df['ally_hero_3'], df['enemy_hero_0'], df['enemy_hero_1'], df['enemy_hero_2'], df['enemy_hero_3']]))
    artifacts_label.fit(pd.concat([df['ally_hero_0_art'], df['ally_hero_1_art'], df['ally_hero_2_art'], df['ally_hero_3_art'], df['enemy_hero_0_art'], df['enemy_hero_1_art'], df['enemy_hero_2_art'], df['enemy_hero_3_art']]))
    sets_label.fit(pd.concat([df['ally_hero_0_set1'], df['ally_hero_0_set2'], df['ally_hero_0_set3'], df['ally_hero_1_set1'], df['ally_hero_1_set2'], df['ally_hero_1_set3'], df['ally_hero_2_set1'], df['ally_hero_2_set2'], df['ally_hero_2_set3'], df['ally_hero_3_set1'], df['ally_hero_3_set2'], df['ally_hero_3_set3'], df['enemy_hero_0_set1'], df['enemy_hero_0_set2'], df['enemy_hero_0_set3'], df['enemy_hero_1_set1'], df['enemy_hero_1_set2'], df['enemy_hero_1_set3'], df['enemy_hero_2_set1'], df['enemy_hero_2_set2'], df['enemy_hero_2_set3'], df['enemy_hero_3_set1'], df['enemy_hero_3_set2'], df['enemy_hero_3_set3']]))
    win_label.fit(df['is_win'])
    if not os.path.exists("data_analysis/data_preprocessing/label_encoding"):
        os.makedirs("data_analysis/data_preprocessing/label_encoding")
    np.save("data_analysis/data_preprocessing/label_encoding/heroes_label.npy", heroes_label.classes_)
    np.save("data_analysis/data_preprocessing/label_encoding/artifacts_label.npy", artifacts_label.classes_)
    np.save("data_analysis/data_preprocessing/label_encoding/sets_label.npy", sets_label.classes_)
    np.save("data_analysis/data_preprocessing/label_encoding/win_label.npy", win_label.classes_)
    for i in range(4):
        df[f'ally_hero_{i}'] = heroes_label.transform(df[f'ally_hero_{i}'])
        df[f'ally_hero_{i}_art'] = artifacts_label.transform(df[f'ally_hero_{i}_art'])
        df[f'ally_hero_{i}_set1'] = sets_label.transform(df[f'ally_hero_{i}_set1'])
        df[f'ally_hero_{i}_set2'] = sets_label.transform(df[f'ally_hero_{i}_set2'])
        df[f'ally_hero_{i}_set3'] = sets_label.transform(df[f'ally_hero_{i}_set3'])
        df[f'enemy_hero_{i}'] = heroes_label.transform(df[f'enemy_hero_{i}'])
        df[f'enemy_hero_{i}_art'] = artifacts_label.transform(df[f'enemy_hero_{i}_art'])
        df[f'enemy_hero_{i}_set1'] = sets_label.transform(df[f'enemy_hero_{i}_set1'])
        df[f'enemy_hero_{i}_set2'] = sets_label.transform(df[f'enemy_hero_{i}_set2'])
        df[f'enemy_hero_{i}_set3'] = sets_label.transform(df[f'enemy_hero_{i}_set3'])
    df['is_win'] = win_label.transform(df['is_win'])
    df.to_pickle("data_analysis/data_preprocessing/label_encoding/label_encoded_data.pkl")
    print('Label encoding done')

def shuffle():
    df = pd.read_pickle("data_analysis/data_preprocessing/label_encoding/label_encoded_data.pkl")
    l = []
    for i in tqdm(range(df.shape[0]), desc='Shuffling'):
        data = df.iloc[i]
        ally_permute = list(itertools.permutations([data[1:6], data[6:11], data[11:16], data[16:21]]))
        for j in range(len(ally_permute)):
            dict_data = {}
            dict_data.update({'is_win': data[0].item()})
            for k in range(4):
                dict_data.update({
                    f'ally_hero_{k}': ally_permute[j][k][0],
                    f'ally_hero_{k}_art': ally_permute[j][k][1],
                    f'ally_hero_{k}_set1': ally_permute[j][k][2],
                    f'ally_hero_{k}_set2': ally_permute[j][k][3],
                    f'ally_hero_{k}_set3': ally_permute[j][k][4]
                })
            for k in range(4):
                dict_data.update({
                    f'enemy_hero_{k}': data[21+k*5],
                    f'enemy_hero_{k}_art': data[22+k*5],
                    f'enemy_hero_{k}_set1': data[23+k*5],
                    f'enemy_hero_{k}_set2': data[24+k*5],
                    f'enemy_hero_{k}_set3': data[25+k*5]
                })
            l.append(dict_data)
    augmented_df = pd.DataFrame(l)
    augmented_df.sample(frac=1).reset_index(drop=True)
    augmented_df.to_pickle("data_analysis/data_preprocessing/shuffled_data.pkl")
    print('Shuffling done')