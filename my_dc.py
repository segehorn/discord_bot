# -*- coding: utf-8 -*-
"""
かうんとえー用DiscordBot
機能は随時追加予定
"""
import discord
import re
import pokemon

# region CONST
# トークンID
TOKEN = 'NTExMTY2Nzc4NzgxNDY2NjI0.Dsr79Q.s4AQXyQrxDSnSiecrH_78dNuAJk'
# テキストチャンネルID (vc入室履歴)
NOTICE_CH_ID = 511538305251278871
# NOTICE_CH_ID = 571954766830370846 # テストサーバー
# ポケモンcsv
POKEMON_DATA_CSV = 'poke_data.csv'
# ポケモン育成論参考サイト
POKEMON_THEORY_URL = 'https://yakkun.com/sm/theory/'
# endregion

# region グローバルスコープ変数
name_list = []
poke_list = []
client = discord.Client()
# endregion


# ログイン時
@client.event
async def on_ready():
    print(f'{client.user}がログインしました')


# 誰かが発言時
@client.event
async def on_message(message):

    # Botの発言は無視
    if message.author.bot:
        return

    # 発言者名を取得して反応する
    if message.content.startswith('こんにちは'):
        if message.author != client.user:
            reply = f'こんにちは、{message.author.name}さん'
            await message.channel.send(reply)

    # アマゾンの汚いURLが貼られたら修正する
    if message.content.startswith('https://www.amazon.co.jp/'):
        valid_url = re.compile('^https://www.amazon.co.jp/dp/[\w]{10}/$')
        if not re.match(valid_url, message.content):
            # 修正したURLを発言
            try:
                marchant_code = re.findall('dp/[\w]{10}', message.content)
                reply = f'{message.author.name}: https://www.amazon.co.jp/{marchant_code[0]}/'
                # 修正して書き直す
                await rewrite_message(message, reply)
            except:
                print('非対応のamazonのURLを検出')

    # 育成論を呼び出す
    if message.content.startswith('育成論'):
        # ポケモンの特定
        pokedex_no, poke_name = await identify_pokemon(message)

        # 送信
        msg = f'{POKEMON_THEORY_URL}p{pokedex_no}'
        await message.channel.send(msg)

    # 種族値を呼び出す
    if message.content.startswith('種族値'):
        # ポケモンの特定
        pokedex_no, poke_name = await identify_pokemon(message)

        # 種族値等のデータを呼び出す
        for pokemon in poke_list:
            # ポケモンの名前で検索
            if pokemon['名前'] == poke_name:
                pk = pokemon

        msg = '{0} {1}-{2}-{3}-{4}-{5}-{6}({7})\n{8} {9}タイプ / {10}'.format(pk['名前'], pk['HP'], pk['攻撃'],
                                                                              pk['防御'], pk['特攻'], pk['特防'],
                                                                              pk['素早さ'], pk['合計'], pk['タイプ1'],
                                                                              pk['タイプ2'], pk['特性(隠し特性)']
                                                                                )

        # 送信
        await message.channel.send(msg)

# VCの状態更新時
@client.event
async def on_voice_state_update(member, before, after):
    """
    ボイスチャンネルに入退室したメンバーを書き込む
    """

    if ((before.self_mute is not after.self_mute)
            or (before.self_deaf is not after.self_deaf)):
        # ミュート設定が切り替わっただけなので無視
        return

    if before.channel is None:
        # 入室時に入室者名を通知する
        reply = f'{member.name} 参戦！！'
        # 通知用チャンネルのID取得
        reply_channel = client.get_channel(NOTICE_CH_ID)
        # メッセージ送信
        await reply_channel.send(reply)

    if after.channel is None:
        # 退室時に退室者名を通知する
        reply = f'{member.name}さんがバーストしました'
        # 通知用チャンネルのID取得
        reply_channel = client.get_channel(NOTICE_CH_ID)
        # メッセージ送信
        await reply_channel.send(reply)


# region 共通関数
async def rewrite_message(message, reply):
    """
    直前のメッセージを消して書き直す
    :param message: チャンネル情報が含まれたmessageオブジェクト
    :param reply: 書き直す内容
    :return: なし
    """
    # 直前のメッセージを消す
    await message.delete()
    # 書き直す
    await message.channel.send(reply)


async def identify_pokemon(message):
    """
    書き込まれたポケモンを特定する
    :param message:
    :return: 図鑑番号, ポケモンの名前
    """
    # ポケモンの名前が無かったら無視
    try:
        indicated_pokemon = message.content.split()[1]
    except:
        print('不正な入力')
        return

    for name in name_list:
        if indicated_pokemon == name[1]:
            # 名前があれば図鑑番号を確保
            pokedex_no = name[0]
            break
    else:
        print('存在しないポケモン')
        return

    if '-' in pokedex_no:
        pokedex_no = pokedex_no[:-2]

    return pokedex_no, indicated_pokemon

# endregion

if __name__ == '__main__':
    # ポケモンのデータ読み込み(詳細情報のある辞書リスト, 図鑑番号と名前のタプルリスト)
    poke_list, name_list = pokemon.read_pokemon_csv(POKEMON_DATA_CSV)
    # クライアント実行
    client.run(TOKEN)
