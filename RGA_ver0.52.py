import discord
from discord import app_commands 
from discord.ext import commands
import requests
import json
import pandas as pd

# Riot Developer PortalにログインしてAPIkeyを生成してコピーしてください
# Riot Developer Portal_URL(https://developer.riotgames.com/)
APIkey = ""
#discord developer portalにログインしてアプリケーションを作成してTOKENをコピーしてください
#discord developer portal_URL(https://discord.com/developers/applications)
TOKEN = ""

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents) 
tree = app_commands.CommandTree(client)

SN = []
SUMLEV = []
WIN = []
CHAMPN = []
KDA = []
LANE = []

@client.event
async def on_ready():
    print('ログインしました') 
    # アクティビティを設定 
    new_activity = f"League of Legends" 
    await client.change_presence(activity=discord.Game(new_activity)) 
    await tree.sync()
  
# スラッシュコマンドの実装
@tree.command(name='hello', description='Display profile based on gameName and tagLine') 
async def test(interaction: discord.Interaction, gn:str, tl:int):
    # gnにはgameNameをtlにはtagLineを引数として受け取る
    url = f'https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gn}/{tl}?api_key={APIkey}'
    encryptedPUUID = requests.get(url).json()


    #マッチID取得リクエスト, count=nの数字が取得マッチID数
    url = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{encryptedPUUID["puuid"]}/ids?start=0&count=1&api_key={APIkey}'
    matchIndex = requests.get(url).json()
    matchID = matchIndex[0]

    url = f'https://asia.api.riotgames.com/lol/match/v5/matches/{matchID}?api_key={APIkey}'
    matchInfo = requests.get(url).json()


    gameDuration = matchInfo["info"]["gameDuration"]
    gameVersion = matchInfo["info"]["gameVersion"]


    for participants in range(10):
        SN.append(f'{matchInfo["info"]["participants"][participants]["riotIdGameName"]}{matchInfo["info"]["participants"][participants]["riotIdTagline"]}')
        SUMLEV.append(matchInfo["info"]["participants"][participants]["summonerLevel"])
        WIN.append(matchInfo["info"]["participants"][participants]["win"])
        CHAMPN.append(matchInfo["info"]["participants"][participants]["championName"])
        KDA.append(f'{matchInfo["info"]["participants"][participants]["kills"]}/{matchInfo["info"]["participants"][participants]["deaths"]}/{matchInfo["info"]["participants"][participants]["assists"]}')
        LANE.append(matchInfo["info"]["participants"][participants]["teamPosition"])   
    matchResult = {
        'SN': SN,
        'サモレベ': SUMLEV,
        'win': WIN,
        '使用チャンピオン': CHAMPN,
        'k/d/a': KDA,
        'lane': LANE,
    }

    df = pd.DataFrame(matchResult)
    embed = discord.Embed(
                        title=f"{gn}の最新の対戦履歴",
                        color=0x00ff00,
                        description="説明が表示される欄",
                        url=f"https://www.op.gg/summoners/jp/{gn}-{tl}" # ついでにOPGGのリンクを生成
                        )
    # 他人から見えるBotの情報
    embed.set_author(name=client.user, # Bot運営者の名前
                    url="https://github.com/G-goma393", # nameへのマスクリンク、SNSのリンクでもどうぞ
                    icon_url="https://brand.riotgames.com/static/a91000434ed683358004b85c95d43ce0/8a20a/lol-logo.png"# アイコンのサンプルとしてLoLのロゴ
                    )

    embed.add_field(name = "試合時間(s)", value = gameDuration, inline=False)
    embed.add_field(name = "パッチ", value = gameVersion, inline=False)
    embed.add_field(name = "リザルト", value = df, inline=False)

    # フッターに載せる情報、だれが運営しているのか分かると良い
    embed.set_footer(text="made by youName",
                    icon_url="")

    await interaction.response.send_message(embed=embed)

client.run(TOKEN)
