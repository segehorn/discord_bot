# -*- coding: utf-8 -*-
"""
ポケモンのデータを取得するモジュール
"""

from bs4 import BeautifulSoup
import requests
import csv

# region Description
POKEMON_DATA_URL = 'http://blog.game-de.com/pokedata/pokemon-data/'
CSV_TITLE = ['No.', '名前', '英語名', 'HP', '攻撃', '防御', '特攻', '特防', '素早さ', '合計',
             'タイプ1', 'タイプ2', '特性(隠し特性)', '高さ(m)', '重さ(kg)']
POKEMON_DATA_CSV = 'poke_data.csv'

# endregion


def get_poke_data(title):
    """
    定数のURLからポケモンのデータを取得してcsvに書き込む
    :param title: csvファイル名
    :return:
    """
    # url取得
    r = requests.get(POKEMON_DATA_URL)
    # パース用オブジェクト作成(lxmlがダメならhtml5libにする)
    soup = BeautifulSoup(r.text, 'lxml')
    # 改行タグを除去
    for br in soup.find_all('br'):
        br.extract()

    # 必要な情報を抜き出しポケモン毎にリスト化
    poke_list = [list(tr.find_all('td')[:len(CSV_TITLE)]) for tr in soup.find_all('tr')]

    # ポケモン毎のデータでディクショナリを作る
    # poke_dict_list = []
    # for a_poke_data in poke_list:
    #     data = {k: v.get_text() for k, v in zip(CSV_TITLE, a_poke_data)}
    #     poke_dict_list.append(data)

    result_poke_list = []
    for a_poke_data in poke_list:
        data = [data.get_text() for data in a_poke_data]
        result_poke_list.append(data)

    # csvファイルを作成して書き込む
    with open(title, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # ヘッダーを書き込む
        # writer.writerow(CSV_TITLE)
        # ポケモンの情報を書き込む
        writer.writerows(result_poke_list)


def read_pokemon_csv(title):
    """
    ポケモンの情報をcsvファイルから読み込む
    :param title: csvファイル名
    :return: 辞書のリスト, タプルのリスト
    """
    # ファイル読み込み
    with open(title, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, fieldnames=CSV_TITLE)
        result_list = [row for row in reader]

    number_name_list = [(result['No.'], result['名前']) for result in result_list]

    return result_list, number_name_list


if __name__ == '__main__':
    # get_poke_data(POKEMON_DATA_CSV)
    a_list, name_list = read_pokemon_csv(POKEMON_DATA_CSV)
    for data in name_list:
        print(data)