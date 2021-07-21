import asyncio
import discord
import random
import shutil
import os
import pickle as pcl
import json
import threading
from discord.ext import tasks
import datetime
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

intents = discord.Intents.default()
intents.members = True
intents.typing = True
bot = discord.Client(intents=intents)
SERVERS = {}
OUT_MSG = []
interval = {}
wait_users = []
saving = {}
dm_now = None
maintenance = False
dm_messages = {}
out = False
today = datetime.datetime.today().day
prefix = "!lg."
TOKEN = "Nzg0NDA1MzIwMjY5MDM3NTc4.X8o0YQ.t1DMVf-BrA7Q9RaVcTv3SVeSgMI"
owner_id = 535429351743946764
ads_time = datetime.datetime.now() + datetime.timedelta(minutes=100)
AdsInterval = [100,1000]

@bot.event
async def on_ready():
    print("- LOGIN CREATED -")
    try:
        bot_status.start()
        DELETE_LIMIT.start()
        dm_timeout.start()
        observer_view_activity.start()
        report_limits.start()
        ViewAds.start()
        auto_leave.start()
    except RuntimeError:
        pass
    print("CLEAR")

@bot.event
async def on_message(message):
    global SERVERS,OUT_MSG,interval,out,owner_id,wait_users,dm_messages,saving,dm_now,maintenance,prefix
    prefix = "!lg."
    out = False
    #LAコマンド
    LA_HELP = {
        "!lg.admin.dm.set ":{
            "description":"dmをセットします"
        },
        "!lg.admin.dm.end":{
            "description":"個別dmを終了します"
        },
        "!lg.admin.report.limit.break":{
            "description":"レポートの制限をリセットします"
        },
        "!lg.admin.announce":{
            "description":"すべてのサーバーにアナウンスを流します"
        },
        "!lg.admin.maintenance:true":{
            "description":"メンテナンスモードを有効にします"
        },
        "!lg.admin.maintenance:false":{
            "description":"メンテナンスモードを無効にします"
        },
        "!lg.admin.leave":{
            "description":"指定のサーバーから退居します"
        },
        "!lg.admin.token.permission":{
            "description":"仮登録されたトークンを有効化します",
        },
        "!lg.admin.token.rejection":{
            "description":"仮登録されたトークンを無効化します"
        },
        "!lg.admin.block":{
            "description":"指定のユーザーをブロックします"
        },
        "!lg.admin.block.list":{
            "description":"ブロックされているユーザーのリストを表示します"
        }
    }
    #help構造
    help = {
        "!lg.build":{
            "description":"ログセットアップのビルドを行います"
        }
    }
    if not os.path.exists("server"):
        os.mkdir("server")
    if not os.path.exists("release_dm.pcl"):
        await DUMP_DATA("release_dm.pcl",None)
    if os.path.exists("out_message.json"):
        with open("out_message.json",encoding="UTF-8") as f:
            OUT_MSG = json.loads(f.read())
    if not os.path.exists("admins.json"):
        with open("admins.json",encoding="UTF-8",mode="w") as f:
            json.dump([],f)
    if not os.path.exists("prefixs"):
        await DUMP_DATA("prefixs",{})
    if not os.path.exists("saving.pcl"):
        await DUMP_DATA("saving.pcl",{})
    if not os.path.exists("reports"):
        await DUMP_DATA("reports",{})
    if not os.path.exists("request_tokens"):
        await DUMP_DATA("request_tokens",{})
    if not os.path.exists("ads"):
        os.makedirs("ads")
    if not os.path.exists("blocks"):
        with open("blocks","wb") as f:
            await DUMP_DATA("blocks",{})
    if not os.path.exists("leaving.json"):
        json.dump([],open("leaving.json","w"))
    saving = GET_DATA("saving.pcl")
    prefixs = GET_DATA("prefixs")
    if not "dm_messages" in saving:
        saving["dm_messages"] = {}
    await DUMP_DATA("saving.pcl",saving)
    dm_messages = saving["dm_messages"]
    RELDM = GET_DATA("release_dm.pcl")
    msg = message
    ch = message.channel
    author = message.author
    content = message.content
    guild = message.guild
    try:
        print(f"{message.author.name} / {message.author.id} - (Server:{guild.name} | {guild.id} / serverOwner:{guild.owner_id})")
    except Exception:
        pass
    with open("admins.json","r") as f:
        admins = json.loads(f.read())
    #受け取ったチャンネルがdmだった場合
    LA_CMD = list(LA_HELP.keys())
    if type(msg.channel) == discord.DMChannel:
        if author != bot.user:
            if author.id == owner_id:
                if content.startswith(LA_CMD[0]):
                    try:
                        id = int(content[len(LA_CMD[0]):])
                    except ValueError:
                        await ch.send("`request processing error | help> Arguments are limited to numbers`")
                        return
                    if id == RELDM:
                        await ch.send("既に接続されています")
                        return
                    #データのリセット
                    saving["dm_messages"] = {}
                    await DUMP_DATA("saving.pcl",saving)
                    RELDM = id
                    user = bot.get_user(id)
                    if user != None:
                        await DUMP_DATA("release_dm.pcl",RELDM)
                        await ch.send("セッティング完了しました、その他のDMメッセージの受付を停止します\n`-------- start talk -----------`")
                        await user.send("`----- start talk -----`")
                    else:
                        await ch.send("`⚠ユーザーが見つかりませんでした`")
                    return
                if content == LA_CMD[1]:
                    if RELDM != None:
                        user = bot.get_user(RELDM)
                        #会話終了の報告
                        if user != None:
                            msg = await user.send("`プロセスを終了しました\ndmの受付を再開します`")
                        #dmを送信できなかったユーザーに報告
                        for id in wait_users:
                            user = bot.get_user(id)
                            if user != None:
                                await user.send("`大変長らくお待たせいたしました`\n`dmの受付を再開いたします`")
                                try:
                                    await user.unblock()
                                except Exception:
                                    pass
                            wait_users = []
                        RELDM = None
                        await DUMP_DATA("release_dm.pcl",RELDM)
                        await ch.send("`プロセスを終了しました、DMの受付を再開します`")
                        #データのリセット
                        saving["dm_messages"] = {}
                        dm_now = None
                        await DUMP_DATA("saving.pcl",saving)
                    else:
                        await ch.send("`既に終了されています`")
                    return
            if RELDM != None:
                if author.id == owner_id:
                    user = bot.get_user(RELDM)
                    if user != None:
                        try:
                            n = ""
                            files = []
                            for attach in msg.attachments:
                                n += f"{attach.url}\n"
                                files.append(attach.url)
                            n += f"{content} - ({author.name})"
                            message = await user.send(n)
                            dm_messages.update(
                                {
                                    msg.id:{
                                        "id":message.id,
                                        "channel_id":message.channel.id,
                                        "files":files
                                    }
                                }
                            )
                            saving["dm_messages"] = dm_messages
                            await DUMP_DATA("saving.pcl",saving)
                            await msg.add_reaction('✅')
                            dm_now = datetime.datetime.now()
                        except Exception as error:
                            await ch.send(f"`{error}`")
                            await msg.add_reaction('✖')
                    return
                if author.id == RELDM:
                    blocks = GET_DATA("blocks")
                    if not author.id in blocks:
                        user = bot.get_user(owner_id)
                        if user != None:
                            try:
                                n = ""
                                files = []
                                for attach in msg.attachments:
                                    n += f"{attach.url}\n"
                                    files.append(attach.url)
                                n += f"{content} - ({author.name})"
                                message = await user.send(n)
                                dm_messages.update(
                                    {
                                        msg.id:{
                                            "id":message.id,
                                            "channel_id":message.channel.id,
                                            "files":files
                                        }
                                    }
                                )
                                saving["dm_messages"] = dm_messages
                                await DUMP_DATA("saving.pcl",saving)
                                await msg.add_reaction('✅')
                                dm_now = datetime.datetime.now()
                            except Exception as error:
                                await ch.send(f"`{error}`")
                                await msg.add_reaction('✖')
                        else:
                            if RELDM != None:
                                if not author.id in wait_users:
                                    await author.send("`⚠現在オーナーが別のユーザーと個別にdmをしているため、送信できません`\n`プロセスが終了するまでしばらくお待ちください...`")
                                    wait_users.append(author.id)
                                await msg.add_reaction('✖')
                    else:
                        await msg.add_reaction('✖')
                        await author.send("⚠`貴方はシステムからブロックを受けているためプロセスを通過できません`")
            else:
                if author.id != owner_id:
                    blocks = GET_DATA("blocks")
                    if not author.id in blocks:
                        user = bot.get_user(owner_id)
                        if user != None:
                            await user.send(f"{content} - ({author.name})")
                            await msg.add_reaction('✅')
                    else:
                        print(f"+ [UserMessageblock] + | {author}")
                        await msg.add_reaction('✖')
                        await author.send("⚠`貴方はシステムからブロックを受けているためプロセスを通過できません`")
        return
    #adminコマンド
    if author.id in admins:
        if content.startswith(LA_CMD[2] + " "):
            try:
                id = int(content[len(LA_CMD[2]) + 1:])
            except ValueError:
                await ch.send("`⚠数値以外は指定できません`")
                return
            DETAS = GET_DATA("reports")
            if id in DETAS:
                DETAS[id]["count"] = 0
            else:
                await ch.send("`⚠指定のidは見つかりませんでした`")
                return
            await DUMP_DATA("reports",DETAS)
            user = bot.get_user(id)
            if user != None:
                name = f"`{user.name}`"
            else:
                name = f"`ID:{id}(NoDiscovery)`"
            await ch.send(f"{name}さんのリミットを解除しました")
            return
        if content.startswith(LA_CMD[3] + " "):
            dscpt = content[len(LA_CMD[3]) + 1:]
            servers = os.listdir("server")
            for server in servers:
                try:
                    server = int(server)
                except Exception:
                    continue
                server = bot.get_guild(server)
                if server != None:
                    options = GET_DATA(f"server/{server.id}/option.pcl")
                    if "auc_channel" in options:
                        auc__channel = bot.get_channel(options["auc_channel"])
                        if auc__channel != None:
                            await auc__channel.send(dscpt)
                        else:
                            del options["auc_channel"]
                            await DUMP_DATA(f"server/{server.id}/option.pcl")
            return
        if content == LA_CMD[4]:
            if not maintenance:
                maintenance = True
                await ch.send("`メンテナンスモードをオンにしました`")
            else:
                await ch.send("既にメンテナンスモードはオンになっています")
            return
        if content == LA_CMD[5]:
            if maintenance:
                maintenance = False
                await ch.send("`メンテナンスモードをオフにしました`")
            else:
                await ch.send("既にメンテナンスモードはオフになっています")
            return
        if content.startswith(LA_CMD[6] + " "):
            detas = content[len(LA_CMD[6]) + 1:]
            print(detas)
            try:
                detas = json.loads(detas)
            except json.decoder.JSONDecodeError:
                await ch.send("`dict形式データの読み込みに失敗しました`")
                return
            if "id" in detas:
                if "reason" in detas:
                    reason = detas["reason"]
                    server_id = detas["id"]
                    SERVER = bot.get_guild(server_id)
                    if SERVER != None:
                        if reason == None:
                            await SERVER.leave()
                        all_server = []
                        #取得したファイル名をintに変換
                        for i in os.listdir("server"):
                            all_server.append(int(i))
                        embed = discord.Embed(title="< サーバー退居のお知らせ >",description="`loggingシステム管理者からサーバー退居コマンドが実行されました`",color=discord.Colour.red())
                        embed.add_field(name="理由と説明",value=f"*{reason}*")
                        if SERVER.id in all_server:
                            OPTIONS = GET_DATA(f"server/{SERVER.id}/option.pcl")
                            if "auc_channel" in OPTIONS:
                                AUC_CH = bot.get_channel(OPTIONS["auc_channel"])
                                if AUC_CH != None:
                                    await AUC_CH.send(embed=embed)
                                else:
                                    #アナウンスチャンネルが見つからなかった場合のデータ削除
                                    del OPTIONS["auc_channel"]
                                await DUMP_DATA(f"server/{SERVER.id}/option.pcl",OPTIONS)
                                await SERVER.leave()
                                JSDT = json.loads(open("leaving.json","r").read())
                                JSDT.append(SERVER.id)
                                json.dump(JSDT,open("leaving.json","w"),indent=4)
                                shutil.rmtree(f"server/{SERVER.id}/")
                            else:
                                owner = bot.get_user(SERVER.owner_id)
                                try:
                                    await owner.send(f"`※サーバー`{SERVER.name}`はアナウンスチャンネルが設定されていなかったため\n当サーバーオーナー様のdmにご報告いたします`")
                                    await owner.send(embed=embed)
                                except Exception:
                                    pass
                                await SERVER.leave()
                                shutil.rmtree(f"server/{SERVER.id}/")
                        else:
                            pass
                    else:
                        await ch.send("```指定のサーバーを検出できませんでした```")
                else:
                    await ch.send("KEY`reason`は必須です")
            else:
                await ch.send("KEY`id`は必須です")
            return
        if content.startswith(LA_CMD[7] + " "):
            token_value = content[len(LA_CMD[7] + " "):]
            TOKENS_DATA = GET_DATA("request_tokens")
            if token_value in TOKENS_DATA:
                token_cash_data = TOKENS_DATA[token_value]
                print("[INFO] - cmd: Token activate")
                for i in token_cash_data["functions"]:
                    await i["func"](*i["args"])
            else:
                await ch.send("指定のトークンは存在しません")
            return
        if content.startswith(LA_CMD[8] + " "):
            token_value = content[len(LA_CMD[8] + " "):]
            TOKENS_DATA = GET_DATA("request_tokens")
            if token_value in TOKENS_DATA:
                pass
            else:
                await ch.send("指定のトークンは存在しません")
        if content.startswith(LA_CMD[9] + " "):
            try:
                input_id = int(content[len(LA_CMD[9] + " "):])
            except ValueError:
                await ch.send("⚠idはすべて数字です")
                return
            user_ids = [i.id for i in bot.users]
            if input_id in user_ids:
                msg = await ch.send("コマンドを実行中...")
                BLOCK_DATAS = GET_DATA("blocks")
                if not input_id in BLOCK_DATAS:
                    activate_token = await make_token(100)
                    data_pkg = {
                        input_id:{
                            "ACTIVATE_TOKEN":activate_token,
                            "date":datetime.datetime.now()
                        }
                    }
                    BLOCK_DATAS.update(data_pkg)
                    await DUMP_DATA("blocks",BLOCK_DATAS)
                    await msg.edit(content=f"`正常に実行されました!`")
                else:
                    try:
                        await msg.edit(content="⚠このユーザーは既にブロックされています")
                    except Exception:
                        pass
            else:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                await ch.send("指定のユーザーidは検出できませんでした")
            return
        if content == LA_CMD[10]:
            n = ""
            page = 1
            BLOCKS_DATA = GET_DATA("blocks")
            embed = discord.Embed(title=f"🔓Blocking Users🔓 <PAGE / {page}>",color=discord.Colour.red())
            for id in BLOCKS_DATA:
                data = BLOCKS_DATA[id]
                user = bot.get_user(id)
                if user != None:
                    user_name = user.name
                else:
                    user_name = "`Not Found user`"
                token = data["ACTIVATE_TOKEN"]
                c = n + f"{user_name}`{token}`"
                n_size = len(c)
                if n_size > 900:
                    await ch.send(embed=embed)
                    page += 1
                    embed = discord.Embed(title=f"🔓Blocking Users🔓 <PAGE / {page}>",color=discord.Colour.red())
                    n = ""
                    continue
                embed.add_field(name=user_name,value=f"`{token}`",inline=False)
                n += c
            if n == "":
                embed = discord.Embed(title=f"🔓Blocking Users🔓 <PAGE / {page}>",description="`⚠現在ブロックされているユーザーはいません`",color=discord.Colour.red())
                await ch.send(embed=embed)
            else:
                await ch.send(embed=embed)
            return
    #サーバーかの判定
    if guild != None:
        #インターバルの設定
        if not guild.id in interval:
            interval.update({guild.id:datetime.datetime.now()})
        #カスタムプレフィックス
        if guild.id in prefixs:
            BP = prefix
            prefix = prefixs[guild.id]
            if BP != prefix:
                if content.startswith(BP):
                    await ch.send(f"※このサーバーでのプレフィックスは`{prefix}`です")
        #botか否かの判別
        if bot.user != author:
            server_path = f"server/{guild.id}"
            if not os.path.exists("logging_servers.pcl"):
                with open("logging_servers.pcl","wb") as f:
                    pcl.dump({},f)
            with open("logging_servers.pcl","rb") as f:
                SERVERS = pcl.load(f)
                await SERVERS_SAVE()
            for i in list(SERVERS):
                SF = []
                for n in os.listdir("server"):
                    SF.append(int(n))
                if not i in SF:
                    del SERVERS[i]
            await DUMP_DATA("logging_servers.pcl",SERVERS)
            LJDT = json.loads(open("leaving.json","r").read())
            if guild.id in LJDT:
                await ch.send(f"⚠プロセスを通過できません\n`現在このサーバーはシステムからブロックされているためコマンドを使用することができません`")
                return
            if guild.id in SERVERS:
                help = {
                    "log":True,
                    f"{prefix}set_view":{
                        "description":"ログを表示するチャンネルを変更します",
                        "using":f"{prefix}set_view"
                    },
                    f"{prefix}announce_channel":{
                        "description":"botからのアナウンスを表示します",
                        "using":f"{prefix}announce_channel"
                    },
                    f"{prefix}log.message.default.search":{
                        "description":"指定したユーザーidで保存されているメッセージ一覧を表示します",
                        "using":f"{prefix}log.message.default.search <ユーザーid>"
                    },
                    f"{prefix}log.message.out.search":{
                        "description":"指定したユーザーidで不適切な表現が含まれている可能性があるメッセージ一覧を表示します",
                        "using":f"{prefix}log.message.out.search <ユーザーid>"
                    },
                    f"{prefix}log.message.destroy.search":{
                        "description":"指定したユーザーidで保存されているメッセージの削除ログを表示します",
                        "using":f"{prefix}log.message.destroy.search <ユーザーid>"
                    },
                    f"{prefix}invite":{
                        "description":"招待リンクを発行します",
                        "using":f"{prefix}invite"
                    },
                    f"{prefix}log.message.search.id":{
                        "description":"指定のidのメッセージログを検索し表示します",
                        "using":f"{prefix}log.message.search.id <メッセージid>"
                    },
                    f"{prefix}build.observer":{
                        "description":"サーバー内メッセージの統計や、比較などの機能をビルドします",
                        "using":f"{prefix}build.observer"
                    },
                    f"{prefix}system.JoinServers":{
                        "description":"現在導入されているサーバー一覧を表示します",
                        "using":f"{prefix}system.JoinServers"
                    },
                    f"{prefix}genereat.token":{
                        "description":"logging内で使用されるタイプのトークン文字列を生成します\n(生成した文字列はtokenとして使うことはできません)",
                        "using":f"{prefix}genereat.token <長さ>"
                    },
                    f"{prefix}report":{
                        "description":"loggingサポートにレポートを送信します",
                        "using":f"{prefix}report <内容>"
                    },
                    f"{prefix}setting.custom.prefix":{
                        "description":"カスタムプレフィックスを設定します",
                        "using":f"{prefix}setting.custom.prefix <新しいプレフィックス名>"
                    },
                    f"{prefix}announce.ads:on":{
                        "description":"広告をオンにします",
                        "using":f"{prefix}announce.ads:on"
                    },
                    f"{prefix}announce.ads:off":{
                        "description":"広告をオフにします",
                        "using":f"{prefix}announce.ads:off"
                    },
                    f"{prefix}request.ads":{
                        "description":"広告を申請します",
                        "using":f"{prefix}request.ads"
                    },
                    f"{prefix}ads.setting":{
                        "description":"認証された広告の設定を行います",
                        "using":f"{prefix}ads.setting <token>"
                    },
                    f"{prefix}block.release":{
                        "description":"ユーザーのブロックを解除します",
                        "using":f"{prefix}block.release"
                    }
                }
                if maintenance:
                    if any(content.startswith(i) for i in help):
                        await ch.send("`メンテナンス中のためコマンドを実行できません`")
                    return
                #ユーザーのログ
                server_list = []
                users = await GET_FILE_NAMES(f"server/{guild.id}/user")
                l = []
                for i in users:
                    l.append(int(i))
                users = l
                if not message.author.id in users:
                    data = {
                        "name":author.name,
                        "discriminator":author.discriminator,
                        "avatar_url":author.avatar,
                        "bot":author.bot,
                        "friend":author.is_friend(),
                        "block":author.is_blocked(),
                    }
                    await DUMP_DATA(f"{server_path}/user/{author.id}.pcl",data)
                #豆知識
                if not author.bot:
                    if bot.user in message.mentions:
                        tips = [
                            "loggingオーナーとお話しするには",
                            "絶賛アイコン募集中",
                            "APEX豆知識 [オクタン編]"
                        ]
                #view_channelにログを出力
                if not author.bot:
                    option = GET_DATA(f"{server_path}/option.pcl")
                    channel = bot.get_channel(option["view_channel"])
                    if any(i in content.lower() for i in OUT_MSG):
                        out = True
                    #連続した文字の判定
                    bfc = ""
                    cc = 0
                    line = 0
                    e_line = 0
                    flag = []
                    n = content
                    for value,cnt in enumerate(n):
                        if 12 < cc:
                            out = True
                            if cnt != bfc:
                                flag.append((e_line + (2 * len(flag)),line + (2 * len(flag))))
                                e_line = line
                                cc = 0
                        if cnt == bfc:
                            cc += 1
                        else:
                            e_line = line
                            cc = 0
                        line += 1
                        bfc = cnt
                    if 12 <= cc:
                        flag.append((e_line + (2 * len(flag)),line + (2 * len(flag))))
                    if channel != None:
                        embed = discord.Embed(color=discord.Colour.blue())
                        embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShcwpkR8lyNemFTL103WXkqV_E3MuFDWn-EA&usqp=CAU")
                        if out:
                            embed = discord.Embed(color=discord.Colour.red())
                            embed.set_thumbnail(url="https://www.silhouette-illust.com/wp-content/uploads/2017/10/mark_kinshi_41200-300x300.jpg")
                        embed.set_author(name="< - log - >",icon_url=author.avatar_url)
                        embed.add_field(name="< USER >",value=f"```{author}```\nFriend: `{author.is_friend()}`\nBlocked: `{author.is_blocked()}`",inline=False)
                        embed.add_field(name="< Channel >",value=f"{ch.mention} `id:{ch.id}`",inline=False)
                        if len(message.embeds) != 0:
                            for em in message.embeds:
                                await channel.send(embed=em)
                        if content != "":
                            if len(content) >= 950:
                                final = "`/...`"
                                content = content[:950 - len(final)] + final
                            embed.add_field(name="< Content >",value=f"{content}",inline=False)
                        else:
                            if len(message.embeds) != 0:
                                embed.add_field(name="< NoContent >",value=f"(embeds shown above)",inline=False)
                        if out:
                            embed.set_author(name="< - log[Filter] - >",icon_url=author.avatar_url)
                            for flg in flag:
                                n = await STRING_INSERT(n,"`",flg[0])
                                n = await STRING_INSERT(n,"`",flg[1] + 1)
                            for i in OUT_MSG:
                                if i in n.lower():
                                    p1 = n.lower().find(i)
                                    p2 = p1 + len(i) + 1
                                    n = await STRING_INSERT(n,"`",p1)
                                    n = await STRING_INSERT(n,"`",p2)
                            n = n.replace("``","")
                            embed.add_field(name="< FilterCatch >",value=n,inline=False)
                        time = datetime.datetime.now() - interval[guild.id]
                        embed.add_field(name="< MessageDetails >",value=f"`MessageId`:**{message.id}**\n`MessageType`:**{message.type}**\n`Mentions`:**{message.mentions}**\n`ChannelMentions`:**{message.channel_mentions}**\n`RoleMentions`:**{message.role_mentions}**\n`Activity`:**{message.activity}**\n`Attachments`:**{message.attachments}**",inline=False)
                        embed.add_field(name="< RecvInterval >",value=f"second: `{time.seconds}s`\nmicrosecond: `{time.microseconds}µs`",inline=False)
                        await channel.send(embed=embed)
                        #ログ終了表示
                    data = {
                        "content":content,
                        "option":{
                            "author":message.author.id,
                            "channel":message.channel.id,
                            "mention_everyone":message.mention_everyone,
                            "channel_mentions":message.channel_mentions,
                            "role_mentions":message.role_mentions,
                            "activity":message.activity,
                        },
                        "time":datetime.datetime.now()
                    }
                    if out:
                        await DUMP_DATA(f"{server_path}/out-message/{message.id}.pcl",data)
                    else:
                        await DUMP_DATA(f"{server_path}/message/{message.id}.pcl",data)
            #observerがある場合の処理
            if os.path.exists(f"{server_path}/observer"):
                fold_path = f"{server_path}/observer"
                required_files = ["channel_record.pcl","setup.pcl","user_record.pcl","view.pcl"]
                if os.path.exists(f"{fold_path}/WARNING.log"):
                    print(f"breaking obs folder...>SRV-ID/{guild.id}")
                    return
                if not all(os.path.exists(f"{fold_path}/{i}") for i in required_files):
                    await ch.send("`WARNING!!\n・オブザーバー拡張パッケージファイルが破損している為、observerシステムを停止します・`\n```botオーナーに報告しました、復旧までしばらくお待ちください```")
                    await send_dm(owner_id,f"<@{owner_id}>```[報告] サーバー{guild.id}のobserverフォルダが破損しました、復旧するまで機能を停止しています```")
                    with open(f"{fold_path}/WARNING.log","w",encoding="UTF-8") as f:
                        f.write("--------------------SYSTEM ERROR--------------------\nこのフォルダは破損しています、そのためデータを正常に読み取ることができませんでした\n内部ファイルが修正されるまで、読み込みを停止します")
                    return
                if os.path.exists(f"{fold_path}/setup.pcl"):
                    setting = GET_DATA(f"{fold_path}/setup.pcl")
                    if setting["completion"]:
                        help.update(
                            {
                                f"{prefix}observer.field.deploy":{
                                    "description":"observer適当チャンネルを追加します"
                                },
                                f"{prefix}observer.field.close":{
                                    "description":"observerチャンネルから除外します"
                                },
                                f"{prefix}observer.set.view":{
                                    "description":"observerのログチャンネルを設定します"
                                },
                                f"{prefix}observer.build.global":{
                                    "description":"グローバルランキング機能をビルドします"
                                }
                            }
                        )
                        hl = list(help.keys())
                        help_nbm = len(help) - 1
                        #管理者だった場合の判定
                        try:
                            author.guild_permissions.administrator
                        except AttributeError:
                            return
                        if content == hl[17]:
                            blocks_data = GET_DATA("blocks")
                            if author.id in blocks_data:
                                DATAS = blocks_data[author.id]
                                date = DATAS["date"]
                                def wait(msg):
                                    return msg.author == author and msg.channel == ch
                                await ch.send(f"`ブロックされた時刻`:{date}")
                                token = DATAS["ACTIVATE_TOKEN"]
                                while True:
                                    await ch.send(f"`❘アクティベートトークンを入力してください❘`")
                                    rcmsg = await bot.wait_for("message",check=wait)
                                    if rcmsg.content == token:
                                        del blocks_data[author.id]
                                        msg = await ch.send("処理中...")
                                        await DUMP_DATA("blocks",blocks_data)
                                        await msg.edit(content=":white_check_mark:`ブロックが解除されました`:white_check_mark:\n貴方のブロックが解除されたため\nコマンドプロセスが通過できるようになりました")
                                        return
                                    else:
                                        await ch.send("再入力しますか？ [Y/N]")
                                        rcmsg = await bot.wait_for("message",check=wait)
                                        print(rcmsg)
                                        ctn = False
                                        if rcmsg.content.upper() == "Y":
                                            ctn = True
                                        if ctn == True:
                                            continue
                                        else:
                                            await ch.send("コマンドを終了しました")
                                            return
                            else:
                                await ch.send("✖`あなたはシステムからブロックされていません`")
                            return
                        if author.guild_permissions.administrator:
                            if content.startswith(prefix):
                                admins = json.loads(open("admins.json","r").read())
                                if not author.id in admins:
                                    BLOCKS_DATA = GET_DATA("blocks")
                                    print(BLOCKS_DATA)
                                    if author.id in BLOCKS_DATA:
                                        cmd = hl[17]
                                        await ch.send(f"⚠プロセスを通過できません\n`現在あなたはシステムからブロックを受けているため\nこれ以上先のプロセスは通過できません`\nブロックを解除するには`{cmd}`を使用する必要があります")
                                        return
                            #コマンドの判定
                            if content.startswith(hl[help_nbm - 3]):
                                msg = await ch.send("`セットアップ中...`")
                                data = {
                                    "MessageCount":0,
                                    "CREATE":datetime.datetime.now(),
                                    "Users":{},
                                    "SAVE":{},
                                    "TOKEN":await make_token(100)
                                }
                                token = data["TOKEN"]
                                await DUMP_DATA(f"{fold_path}/channels/{ch.id}",data)
                                await author.send(f"テキストチャンネル`{ch.name}`をobserver適用チャンネルに設定しました\nChannelToken:`{token}`")
                                await msg.delete()
                                return
                            if content.startswith(hl[help_nbm - 2]):
                                CHES = await GET_FILE_NAMES(f"{fold_path}/channels")
                                if str(ch.id) in CHES:
                                    try:
                                        msg = await ch.send("データ削除中...")
                                        os.remove(f"{fold_path}/channels/{ch.id}")
                                        await msg.delete()
                                        await author.send(f"テキストチャンネル`{ch.name}`をobserverから除外しました、")
                                    except Exception:
                                        await ch.send("```想定されていないエラーが発生しました、処理を続行できません```")
                                    return
                                else:
                                    await ch.send("未登録のチャンネルです")
                            if content == hl[help_nbm - 1]:
                                CHANNEL_ID = GET_DATA(f"{fold_path}/view.pcl")
                                CHANNEL = bot.get_channel(CHANNEL_ID)
                                if CHANNEL != ch:
                                    msg = await ch.send("`設定しています...`")
                                    await DUMP_DATA(f"{fold_path}/view.pcl",ch.id)
                                    setup = GET_DATA(f"{fold_path}/setup.pcl")
                                    setup["SAVE"]["ViewSetAuthorId"] = author.id
                                    await msg.delete()
                                else:
                                    await ch.send("✅既にこのチャンネルに設定されています")
                                return
                            if content == hl[help_nbm]:
                                if not os.path.exists(f"{fold_path}/global-ranking"):
                                    member_count = len([i for i in guild.members if not i.bot])
                                    if member_count > 15:
                                        msg = await ch.send("`building a profile...`")
                                        os.makedirs(f"server/{guild.id}/observer/global-ranking")
                                        await DUMP_DATA(f"server/{guild.id}/observer/global-ranking/RECORD",{})
                                        await DUMP_DATA(f"server/{guild.id}/observer/global-ranking/SAVE",{})
                                        await DUMP_DATA(f"server/{guild.id}/observer/global-ranking/option",{"active":True})
                                        await msg.edit(content="```ビルドに成功しました````help` > `!lg.helpでコマンドを確認してください`")
                                    else:
                                        await ch.send("```[ ビルド不可 ]```・拡張機能をビルドするためにはサーバー人数が15人以上である必要があります")
                                else:
                                    await ch.send("`ビルド済み`")
                                return
                        CHNS = await GET_FILE_NAMES(f"{fold_path}/channels")
                        if str(ch.id) in CHNS:
                            if not author.bot:
                                CHANNEL_DATA = GET_DATA(f"{fold_path}/channels/{ch.id}")
                                CHANNEL_DATA["MessageCount"] += 1
                                if not author.id in CHANNEL_DATA["Users"]:
                                    CHANNEL_DATA["Users"].update(
                                        {
                                            author.id:{
                                                "count":1
                                            }
                                        }
                                    )
                                else:
                                    CHANNEL_DATA["Users"][author.id]["count"] += 1
                                await DUMP_DATA(f"{fold_path}/channels/{ch.id}",CHANNEL_DATA)
                        #グローバルランキングが有効の場合
                        if os.path.exists(f"{fold_path}/global-ranking"):
                            help.update(
                                {
                                    f"{prefix}observer.global:true":{
                                        "description":"グローバルランキングを有効化します"
                                    },
                                    f"{prefix}observer.global:false":{
                                        "description":"グローバルランキングを無効化します"
                                    }
                                }
                            )
                            hl = list(help.keys())
                            help_nbm = len(help) - 1
                            if content == hl[help_nbm - 1]:
                                options = GET_DATA(f"{fold_path}/global-ranking/option")
                                active = options["active"]
                                if not active:
                                    options["active"] = True
                                    await ch.send(f"```グローバルランキングを有効化しました```無効化する場合は`{hl[help_nbm]}`を実行してください")
                                    await DUMP_DATA(f"{fold_path}/global-ranking/option",options)
                                else:
                                    await ch.send("既に有効化されています")
                                return
                            if content == hl[help_nbm]:
                                options = GET_DATA(f"{fold_path}/global-ranking/option")
                                active = options["active"]
                                if active:
                                    options["active"] = False
                                    await ch.send(f"```グローバルランキングを無効化しました```再度有効化する場合は`{hl[help_nbm - 1]}`を実行してください")
                                    await DUMP_DATA(f"{fold_path}/global-ranking/option",options)
                                else:
                                    await ch.send("既に無効化されています")
                                return
                            options = GET_DATA(f"{fold_path}/global-ranking/option")
                            if options["active"]:
                                if not author.bot:
                                    USERS_RECORD = GET_DATA(f"{fold_path}/global-ranking/RECORD")
                                    if not author.id in USERS_RECORD:
                                        USERS_RECORD.update(
                                            {
                                                author.id:{
                                                    "count":1
                                                }
                                            }
                                        )
                                    else:
                                        USERS_RECORD[author.id]["count"] += 1
                                    await DUMP_DATA(f"{fold_path}/global-ranking/RECORD",USERS_RECORD)
            if content == f"{prefix}help":
                await VIEW_HELP(ch,help,"green")
                return
            if content.startswith(f"{prefix}help "):
                cmd_name = content[len(f"{prefix}help "):]
                cmds = {}
                for cmd in hl:
                    cmds.update(
                        {
                            cmd[len(prefix):]:help[cmd]
                        }
                    )
                if cmd_name in cmds:
                    embed = discord.Embed(color=discord.Colour.blue())
                    embed.set_author(name="Command Help",icon_url="https://illust8.com/wp-content/uploads/2018/06/mark_information_illust_82.png")
                    description = "`None`"
                    using = "`None`"
                    if "description" in cmds[cmd_name]:
                        description = cmds[cmd_name]["description"]
                    if "using" in cmds[cmd_name]:
                        using = cmds[cmd_name]["using"]
                    embed.add_field(name=cmd_name,value=description,inline=False)
                    embed.add_field(name="- 使い方 -",value=f"`{using}`",inline=False)
                    await ch.send(embed=embed)
                else:
                    embed = discord.Embed(title="エラー",description="コマンドが見つかりませんでした")
                    await ch.send(embed=embed)
                return
            if content == f"{prefix}admin.help":
                await VIEW_HELP(ch,LA_HELP,"red")
            hl = list(help.keys())
            if any(content.startswith(i) for i in hl):
                if not author.guild_permissions.administrator:
                    await ch.send("`PermissionError | You don't appear to have administrative privileges.`")
            try:
                author.guild_permissions.administrator
            except AttributeError:
                return
            #管理者権限の判定
            if author.guild_permissions.administrator:
                if guild.id in SERVERS:
                    #set_viewコマンド
                    if content == f"{prefix}set_view":
                        option = GET_DATA(f"{server_path}/option.pcl")
                        option["view_channel"] = ch.id
                        await DUMP_DATA(f"{server_path}/option.pcl",option)
                        await ch.send("**このチャンネルをログチャンネルに変更しました**")
                        return
                    if content == f"{prefix}close_log":
                        option = GET_DATA(f"{server_path}/option.pcl")
                        option["view_channel"] = 0
                        await DUMP_DATA(f"{server_path}/option.pcl",option)
                        await ch.send("**ログチャンネルを停止しました**")
                        return
                    hl = list(help.keys())
                    #searchコマンド
                    await SEARCH_CMD(ch,server_path,content,hl[3],"message","< LOG/Message >")
                    await SEARCH_CMD(ch,server_path,content,hl[4],"out-message","< LOG/OutMessage >",embed_color=discord.Colour.red())
                    await SEARCH_CMD(ch,server_path,content,hl[5],"delete-message","< LOG/DelMessage >",embed_color=discord.Colour.default())
                    #アナウンスチャンネルコマンド
                    if content == hl[2]:
                        option = GET_DATA(f"{server_path}/option.pcl")
                        option["auc_channel"] = ch.id
                        await DUMP_DATA(f"{server_path}/option.pcl",option)
                        await ch.send("**このチャンネルをアナウンスチャンネルに設定しました**")
                        return
                    #inviteコマンド
                    if content == hl[6]:
                        await ch.send("`invite URL:` https://discord.com/api/oauth2/authorize?client_id=784405320269037578&permissions=2147483639&scope=bot")
                        return
                    if content.startswith(hl[7]):
                        #例外処理
                        try:
                            id = int(content[len(hl[7]) + 1:])
                        except ValueError:
                            await ch.send("`request processing error | help> Arguments are limited to numbers`")
                        else:
                            #ファイルの取得
                            files = await GET_LIST_FILES(server_path,["message","out-message"])
                            send_log = False
                            for file in files:
                                EOF = False
                                with open(file,"rb") as f:
                                    try:
                                        data = pcl.load(f)
                                    except Exception:
                                        EOF = True
                                        continue
                                if EOF:
                                    os.remove(file)
                                p1 = file.rfind("/") + 1
                                p2 = file[p1:].find(".") + p1
                                data_id = int(file[p1:p2])
                                #idの識別
                                if id == data_id:
                                    TIME = data["time"]
                                    UI = data["option"]["author"]
                                    USER = bot.get_user(UI)
                                    embed = discord.Embed(color=discord.Colour.green())
                                    #ユーザーの識別
                                    if USER != None:
                                        embed.set_author(name=f"{USER.name}/{UI} - {data_id}",icon_url=USER.avatar_url)
                                    else:
                                        embed.set_author(name=f"NoFoundUser - {data_id}",icon_url="https://www.shoshinsha-design.com/wp-content/uploads/2018/07/0731-%E3%83%A6%E3%83%BC%E3%82%B5%E3%82%99%E3%83%BC%E4%B8%B8.png")
                                    n = data["content"]
                                    try:
                                        if len(n) >= 950:
                                            fake = "`/...`"
                                            n = n[:len(fake)] + fake
                                        embed.add_field(name="< LOG >",value=n)
                                        await ch.send(embed=embed)
                                    except Exception:
                                        await ch.send("`⚠システムエラーにより詳細データを送信できませんでした\nシステムを続行します:white_check_mark:`")
                                    send_log = True
                            if send_log == False:
                                await ch.send("`⚠保存データは見つかりませんでした`")
                        return
                    
                    #オブザーバービルド
                    if content == hl[8]:
                        print("-----STARTING BUILD OBS-----")
                        folder_path = f"{server_path}/observer"
                        CT = False
                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)
                            print("[CFM] -> NoFolder. フェーズ続行...")
                        else:
                            data = GET_DATA(f"{folder_path}/setup.pcl")
                            if data["completion"]:
                                CT = True
                        if not CT:
                            print("MAKING FILES...")
                            with open(f"{folder_path}/setup.pcl","wb") as f:
                                data = {
                                    "folder_path":folder_path,
                                    "completion":False,
                                    "SAVE":{}
                                }
                                pcl.dump(data,f)
                            await DUMP_DATA(f"{folder_path}/channel_record.pcl",{})
                            os.makedirs(f"{folder_path}/channels")
                            with open(f"{folder_path}/user_record.pcl","wb") as f:
                                pcl.dump({},f)
                            await DUMP_DATA(f"{folder_path}/view.pcl",None)
                            #セットアップ完了ライン
                            setting = GET_DATA(f"{folder_path}/setup.pcl")
                            setting["completion"] = True
                            await DUMP_DATA(f"{folder_path}/setup.pcl",setting)
                            await ch.send(f"ビルドセットアップが完了しました\n`-----start process-----`\n詳細 > OBS拡張機能の詳細は`{prefix}help`で確認できます")
                        else:
                            await ch.send("`⚠observer拡張機能は既にビルドされています`")
                        return
                    #joinServerコマンド
                    if content == hl[9]:
                        n = ""
                        for i in bot.guilds:
                            n += f"`{i.name} | {i.id} ({len(i.members)})`\n"
                        embed = discord.Embed(title="< Join - Servers >",description=n,color=discord.Colour.green())
                        await ch.send(embed=embed)
                        return
                    #トークン生成コマンド
                    if content.startswith(hl[10] + " "):
                        try:
                            count = int(content[len(hl[10])+1:])
                        except ValueError:
                            await ch.send("⚠数値のみ指定できます")
                            return
                        value = await make_token(count)
                        try:
                            await ch.send(f"`{value}`")
                        except Exception:
                            await ch.send("データを送信できません\n```文字数が多すぎるかもしくは別のエラーです```")
                        return
                    #レポートコマンド
                    if content.startswith(hl[11] + " "):
                        report = content[len(hl[11]) + 1:]
                        rt = datetime.datetime.now()
                        DETAS = GET_DATA("reports")
                        if not author.id in DETAS:
                            DETAS.update(
                                {
                                    author.id:{
                                        "count":1,
                                        "reports":[report],
                                        "last_time":rt
                                    }
                                }
                            )
                        else:
                            count = DETAS[author.id]["count"]
                            if count >= 5:
                                await ch.send("`Restriction Error | 制限回数を越えているためレポートを送信できませんでした`")
                                return
                            count += 1
                            DETAS[author.id]["count"] = count
                            reports = DETAS[author.id]["reports"]
                            reports.append(report)
                            DETAS[author.id]["reports"] = reports
                        await DUMP_DATA("reports",DETAS)
                        count = DETAS[author.id]["count"]
                        print(count)
                        msg = await ch.send("レポートを送信中...")
                        try:
                            embed = discord.Embed(title="< レポート >",color=discord.Colour.red(),description=report)
                            embed.add_field(name="+ 詳細 +",value=f"**送信されたサーバー**:`{guild.name} ({guild.id})`\n**送信したユーザー**:`{author.name} ({author.id})`\n**送信された時刻**:`{rt}`")
                            admins = json.loads(open("admins.json","r").read())
                            actv_admins = []
                            for admin in admins:
                                user = bot.get_user(admin)
                                if user != None:
                                    actv_admins.append(user)
                            await asyncio.gather(*[admin.send(embed=embed) for admin in actv_admins])
                        except Exception:
                            await ch.send("`⚠予期せぬエラーが発生したためレポートを送信できませんでした\n処理を続行します`")
                            return
                        await msg.edit(content="`レポート送信完了しました`")
                        await message.add_reaction('✅')
                    #カスタムプレフィックスコマンド
                    if content.startswith(hl[12] + " "):
                        new_prifix = content[len(hl[12]) + 1:]
                        prefixs[guild.id] = new_prifix
                        await DUMP_DATA("prefixs",prefixs)
                        await ch.send(f"プレフィックスを`{new_prifix}`に変更しました")
                        return
                    #広告オンコマンド
                    if content == hl[13]:
                        folder_path = f"{server_path}"
                        options = GET_DATA(f"{folder_path}/option.pcl")
                        if "ads" in options:
                            if options["ads"] == False:
                                options["ads"] = True
                                await ch.send("広告を`オン`に変更しました")
                            else:
                                await ch.send("既に`オン`になっています")
                        else:
                            options["ads"] = True
                            await ch.send("広告を`オン`に変更しました")
                        await DUMP_DATA(f"{folder_path}/option.pcl",options)
                        return
                    #広告オフコマンド
                    if content == hl[14]:
                        folder_path = f"{server_path}"
                        options = GET_DATA(f"{folder_path}/option.pcl")
                        if "ads" in options:
                            if options["ads"] == True:
                                options["ads"] = False
                                await ch.send("広告を`オフ`に変更しました")
                            else:
                                await ch.send("既に`オフ`になっています")
                        else:
                            options["ads"] = False
                            await ch.send("広告を`オフ`に変更しました")
                        await DUMP_DATA(f"{folder_path}/option.pcl",options)
                        return
                    #広告申請コマンド
                    if content == hl[15]:
                        if not os.path.exists(f"ads/{guild.id}"):
                            rt = datetime.datetime.now()
                            guild_members = [i for i in guild.members if not i.bot]
                            if 10 <= len(guild_members):
                                msg = await ch.send("準備中...")
                                if not os.path.exists("ads"):
                                    os.mkdir("ads")
                                await msg.delete()
                                def check(msg):
                                    return msg.author == author and msg.channel == ch
                                def Y_N_check(msg):
                                    if any(msg.content.upper() == i for i in ["Y","N"]):
                                        return msg
                                def Y_N(content):
                                    if content == "Y":
                                        return True
                                    else:
                                        return False
                                while True:
                                    await ch.send("`| 広告文を入力してください |`")
                                    msg = await bot.wait_for("message",check=check)
                                    ads_value = msg.content
                                    if len(ads_value) > 900:
                                        await ch.send("⚠広告文が長すぎます (900文字以内)")
                                        continue
                                    embed = discord.Embed(description=msg.content,title="Advertising")
                                    await ch.send(embed=embed)
                                    await ch.send("こちらでよろしいですか？ `Y/N`")
                                    CHECK = await bot.wait_for("message",check=Y_N_check)
                                    CHECK = Y_N(CHECK.content)
                                    if CHECK == True:
                                        break
                                    else:
                                        continue
                                msg = await ch.send("広告を申請しています...")
                                token = await make_token(10)
                                package_deta = {
                                    token:{
                                        "content":ads_value,
                                        "status":False
                                    }
                                }
                                await DUMP_DATA(f"ads/{guild.id}",package_deta)
                                embed = discord.Embed(title="< 広告の申請 >",color=discord.Colour.blue())
                                embed.add_field(name="- 広告内容 -",value=ads_value,inline=False)
                                embed.add_field(name="- 詳細 -",value=f"**申請したユーザー**:`{author.name} | {author.id}`\n**申請したサーバー**:`{guild.name} | {guild.id}`\n**申請した時刻**:`{rt}`",inline=False)
                                embed.add_field(name="トークン",value=f"`{token}`")
                                admins = json.loads(open("admins.json").read())
                                conf_msgs = []
                                #全てのアドミンに申請を報告 & 判定がだされたときにembedを更新する用のidの保存
                                for id in admins:
                                    user = bot.get_user(id)
                                    if user != None:
                                        e_msg = await user.send(embed=embed)
                                        conf_msgs.append(
                                            {
                                                "author":user.id,
                                                "msg_id":e_msg.id
                                            }
                                        )
                                #トークンを一時的に保存
                                await token_request(
                                    token,
                                    [
                                        {
                                            "func":ads_finalize,
                                            "args":[
                                                f"ads/{guild.id}",
                                                token,
                                                author.id,
                                            ]
                                        },
                                        {
                                            "func":MDFA,
                                            "args":[
                                                conf_msgs
                                            ]
                                        }
                                    ],
                                    {"author":author.id}
                                )
                                await msg.edit(content="★申請が完了しました\n`結果がでるまでに時間がかかる場合がありますが、ご理解ください`")
                            else:
                                await ch.send("`[ このコマンドを実行するには以下の条件を満たしている必要があります ]`\n・サーバー人数が10人以上であること")
                        else:
                            await ch.send("⚠すでにこのサーバーは広告を申請しています\n`申請してから了承または却下の判定が出されるまで\n少し時間がかかる場合がございます、ご理解ください`")
                        return
                    if content.startswith(hl[16] + " "):
                        input_token = content[len(hl[16] + " "):]
                        msg = await ch.send("準備中...")
                        ALL_DATA = GET_ADS_DATAS()
                        if input_token in ALL_DATA:
                            #オブジェクト定義
                            def wait(msg):
                                return msg.channel == ch and msg.author == author
                            DATAS = ALL_DATA[input_token]
                            if not "setting" in DATAS:
                                DATAS["setting"] = None
                            await msg.delete()
                            msg = await ch.send("```advertisementセッティングへようこそ```")
                            opereat = ADS_setting(bot,ch,author.id,input_token,guild)
                            op = await opereat.main_setting()
                            if type(op) == ERROR:
                                if op.tag == "P-O":
                                    await msg.edit(content="⚠`オペレーティングは進行中です`")
                                if op.tag == "T-V":
                                    await msg.edit(content="⚠`トークンが無効な物です`")
                                return
                        else:
                            await msg.edit(content="⚠指定したトークンは無効のようです...")
                        return
                #ビルドコマンド
                if content == f"{prefix}build":
                    if not guild.id in SERVERS:
                        embed = discord.Embed(title="< 規約 >",description="以下の規約に同意する場合は`Y`やめておく場合は`N`を送信してください。 `Y/N`",color=discord.Colour.red())
                        embed.add_field(name="- 1 -",value="```このbotでのトラブルなどの責任等を一切負いません。```",inline=False)
                        embed.add_field(name="- 2 -",value="```金銭関係に関わる場合このbotの使用を禁止します。```",inline=False)
                        embed.add_field(name="- 3 -",value="```荒らし対策などにこのbotを使用してください、悪用は厳禁です。```",inline=False)
                        embed.add_field(name="- 4 -",value="```致命的なエラーが発生した場合は必ず運営に報告すること。```",inline=False)
                        await ch.send(embed=embed)
                        def Y_N_CHECK(m):
                            if m.channel == ch:
                                if m.author == author:
                                    if m.content in ["Y","N"]:
                                        return m
                        msg = await bot.wait_for("message",check=Y_N_CHECK)
                        if msg.content == "Y":
                            await ch.send("承認しました \nビルドセットアップを実行しています...")
                            if not os.path.exists(server_path):
                                os.makedirs(f"{server_path}/message")
                                os.makedirs(f"{server_path}/user")
                                os.makedirs(f"{server_path}/out-message")
                                os.makedirs(f"{server_path}/delete-message")
                                with open(f"{server_path}/option.pcl","wb") as f:
                                    data = {
                                        "view_channel":0,
                                        "ads":True
                                    }
                                    pcl.dump(data,f)
                                await ch.send("セットアップが完了しました\nロギングを開始します\n`----- start process -----`")
                            else:
                                os.remove(f"server/{guild.id}")
                                os.makedirs(f"server/{guild.id}/message")
                                os.makedirs(f"server/{guild.id}/user")
                                os.makedirs(f"{server_path}/delete-message")
                                await ch.send("登録データとプロファイルデータが異なったため、リセット処理を行います\nリセット終了後は再度ビルドを行いますので、ご安心ください")
                            SERVERS.update({guild.id:{}})
                            await SERVERS_SAVE()
                            return
                        else:
                            await ch.send("ビルドを終了します")
                            return
                    else:
                        await ch.send("ビルド済みのようです")
                    return
        interval[guild.id] = datetime.datetime.now()

@bot.event
async def on_typing(channel,user,when):
    global wait_users,owner_id
    print(f"now typing...\n{user.name}")
    RELDM = GET_DATA("release_dm.pcl")
    if type(channel) == discord.DMChannel:
        if RELDM != None:
            if user.id != owner_id:
                if user.id != RELDM:
                    if not user.id in wait_users:
                        await user.send("`⚠現在オーナーが別のユーザーと個別にdmをしているため、送信できません`\n`プロセスが終了するまでしばらくお待ちください...`")
                        try:
                            await user.block()
                        except Exception as error:
                            print(error)
                        wait_users.append(user.id)

@tasks.loop(seconds=10)
async def auto_leave():
    if not os.path.exists("leaving.json"):
        json.dump([],open("leaving.json","w"))
    try:
        DATAS = json.loads(open("leaving.json","r").read())
        for id in DATAS:
            SERVER = bot.get_guild(id)
            if SERVER:
                await SERVER.leave()
    except Exception:
        pass

@tasks.loop(seconds=1)
async def observer_view_activity():
    global today
    if today != datetime.datetime.today().day:
        folders = os.listdir("server")
        GLOBAL_USERS = {}
        G_CHANNELS = []
        for fold in folders:
            folders = os.listdir(f"server/{fold}")
            if "observer" in folders:
                #observerフォルダまでのパス
                fold_path = f"server/{fold}/observer"
                dictr = os.listdir(fold_path)
                #停止しているフォルダかどうかの判定
                if not "WARNING.log" in dictr:
                    CHID = GET_DATA(f"{fold_path}/view.pcl")
                    CH = bot.get_channel(CHID)
                    #チャンネルが存在するかどうかの判定
                    if CH != None:
                        await CH.send("`----------昨日のチャンネルアクティビティ----------`")
                        files = os.listdir(f"{fold_path}/channels")
                        for file in files:
                            id = int(file.replace(".pcl",""))
                            CHANNEL = bot.get_channel(id)
                            CHANNEL_DATA = GET_DATA(f"{fold_path}/channels/{file}")
                            if CHANNEL != None:
                                ch_name = CHANNEL.name
                                embed = discord.Embed(title=f"< {ch_name} >",color=discord.Colour.gold())
                                value = "\n"
                                #build時刻
                                builded_time = CHANNEL_DATA["CREATE"]
                                #発言回数
                                msg_count = CHANNEL_DATA["MessageCount"]
                                #ユーザーの取得
                                users = CHANNEL_DATA["Users"]
                                users_count = len(users)
                                #回数順になおす
                                counts = {}
                                for user in users:
                                    number = users[user]["count"]
                                    if not number in counts:
                                        counts.update(
                                            {
                                                number:[user]
                                            }
                                        )
                                    else:
                                        counts[number].append(user)
                                print(counts)
                                #ランキング追加
                                count = 0
                                if counts == {}:
                                    value += "`<ランキングなし>`"
                                for number in range(len(counts)):
                                    v = max(counts)
                                    if 5 <= count:
                                        break
                                    cc = 0
                                    for id in counts[v]:
                                        user = bot.get_user(id)
                                        name = ""
                                        if user != None:
                                            name = user.name
                                        else:
                                            name = f"ID:{id}(NoDiscovery)"
                                        if cc < 1:
                                            value += "**"
                                            if count + 1 == 1:
                                                value += "👑 "
                                            if count + 1 == 2:
                                                value += "🥈 "
                                            if count + 1 == 3:
                                                value += "🥉 "
                                            value += f"{count + 1}位** `{name}`   発言回数:`{v}`回\n\n"
                                        else:
                                            value += f"**同率{count + 1}位** `{name}`   発言回数:`{v}`回\n\n"
                                        cc += 1
                                    count += 1
                                    del counts[v]
                                embed.add_field(name="- ユーザーランキング -",value=value,inline=False)
                                value = f"\n**このチャンネルで発言したユーザー数**:`{users_count}`人\n**このチャンネルで発言された回数**:`{msg_count}`回\n**チャンネルがセットアップされた時刻**:`{builded_time}`"
                                embed.add_field(name="- チャンネル詳細 -",value=value,inline=False)
                                await CH.send(embed=embed)
                                CHANNEL_DATA["MessageCount"] = 0
                                CHANNEL_DATA["Users"] = {}
                                await DUMP_DATA(f"{fold_path}/channels/{file}",CHANNEL_DATA)
                            else:
                                await CH.send(f"```[テキストチャンネル]ID:{id} は検出できませんでした```")
                    else:
                        setup = GET_DATA(f"{fold_path}/setup.pcl")
                        if "ViewSetAuthorId" in setup["SAVE"]:
                            user = bot.get_channel(setup["SAVE"]["ViewSetAuthorId"])
                            if user != None:
                                await user.send("`< オブザーバーシステムのVIEWチャンネルを検出できませんでした >`\n```自動的にviewチャンネルをリセットします```")
                            del setup["SAVE"]["ViewSetAuthorId"]
                            await DUMP_DATA(f"{fold_path}/setup.pcl",setup)
                    if CH != None:
                        if os.path.exists(f"{fold_path}/global-ranking"):
                            options = GET_DATA(f"{fold_path}/global-ranking/option")
                            if options["active"]:
                                DETAS = GET_DATA(f"{fold_path}/global-ranking/RECORD")
                                for id in DETAS:
                                    if not id in GLOBAL_USERS:
                                        GLOBAL_USERS.update(
                                            {
                                                id:{
                                                    "count":DETAS[id]["count"]
                                                }
                                            }
                                        )
                                    else:
                                        GLOBAL_USERS[id]["count"] += DETAS[id]["count"]
                                await CH.send("登録された全てのユーザーデータを集計中...")
                                G_CHANNELS.append(CH.id)
                                await DUMP_DATA(f"{fold_path}/global-ranking/RECORD",{})
        #グローバルランキング
        #データ集計
        numbers = {}
        for USER in GLOBAL_USERS:
            count = GLOBAL_USERS[USER]["count"]
            if not count in numbers:
                numbers.update(
                    {
                        count:{
                            "users":[USER]
                        }
                    }
                )
            else:
                numbers[count]["users"].append(USER)
        if numbers == {}:
            embed = discord.Embed(title="-|-  グローバルランキング  -|-",description="`< 残念ながら誰一人として発言していないようです... >`",color=discord.Colour.red())
            for channel_id in G_CHANNELS:
                channel = bot.get_channel(channel_id)
                if channel != None:
                    await channel.send(embed=embed)
            today = datetime.datetime.today().day
            return
        embed = discord.Embed(title="-<  G  >-  グローバルランキング  -<  R  >-",color=discord.Colour.blue())
        embed.set_thumbnail(url="https://t3.ftcdn.net/jpg/03/87/76/56/360_F_387765634_oHdsMQyW2xQakiLS96KsVeO0FeRVonPT.jpg")
        LENGE = 5
        for i in range(1,len(numbers)):
            if i > 5:
                break
            number = max(numbers)
            title = "-  "
            words = [
                "真の",
                "栄光ある",
                "",
                "全loggingサーバー",
                "最強の"
            ]
            if i == 1:
                title += f"👑 {random.choice(words)}"
            if i == 2:
                title += "🥈 トップ"
            if i == 3:
                title += "🥉 トップ"
            user = bot.get_user(numbers[number]["users"][0])
            user_id = numbers[number]["users"][0]
            if user == None:
                name = f"ID:{user_id}"
            else:
                name = user.name
            title += f"{i}位    {name}    -"
            descrpt = f"**発言した回数** : `{number}`回"
            embed.add_field(name=title,value=descrpt,inline=False)
            del numbers[number]
        for channel_id in G_CHANNELS:
            channel = bot.get_channel(channel_id)
            if channel != None:
                await channel.send(embed=embed)
    today = datetime.datetime.today().day

@tasks.loop(seconds=1)
async def dm_timeout():
    global dm_now,wait_users,owner_id
    if dm_now != None:
        ITV = datetime.datetime.now() - dm_now
        if 1800 <= ITV.seconds:
            RELDM = GET_DATA("release_dm.pcl")
            user = bot.get_user(RELDM)
            if user != None:
                await user.send("⚠[TimeOut] dmが30分以上行われなかったため自動的にプロセスを停止しました")
            #dmを送信できなかったユーザーに報告
            for id in wait_users:
                user = bot.get_user(id)
                if user != None:
                    await user.send("`大変長らくお待たせいたしました`\n`dmの受付を再開いたします`")
                    try:
                        await user.unblock()
                    except Exception:
                        pass
                wait_users = []
            RELDM = None
            await DUMP_DATA("release_dm.pcl",RELDM)
            owner = bot.get_user(owner_id)
            if owner != None:
                await owner.send("`プロセスが自動終了しました、DMの受付を再開します`")
            #データのリセット
            saving["dm_messages"] = {}
            await DUMP_DATA("saving.pcl",saving)
            dm_now = None

@bot.event
async def on_message_edit(before,after):
    global dm_messages,owner_id
    saving = GET_DATA("saving.pcl")
    dm_messages = saving["dm_messages"]
    BC = before.content
    AC = after.content
    user_id = after.author.id
    user_name = after.author.name
    if user_id == owner_id:
        user_name = "`owner`"
    if BC != AC:
        if after.id in dm_messages:
            if after.author != bot.user:
                channel = bot.get_channel(dm_messages[after.id]["channel_id"])
                if channel != None:
                    msg = await channel.fetch_message(dm_messages[after.id]["id"])
                    n = ""
                    for url in dm_messages[after.id]["files"]:
                        n += f"{url}\n"
                    n += AC
                    if not AC.endswith(f" - ({user_name})"):
                        n += f" - ({user_name})"
                    await msg.edit(content=n)

@bot.event
async def on_message_delete(message):
    global SERVERS,dm_messages
    ch = message.channel
    author = message.author
    if type(ch) == discord.DMChannel:
        if author != bot.user:
            if message.id in dm_messages:
                channel_id = dm_messages[message.id]["channel_id"]
                channel = bot.get_channel(channel_id)
                msg_id = dm_messages[message.id]["id"]
                msg = await channel.fetch_message(msg_id)
                if msg != None:
                    await msg.edit(content="(削除済み)")
                del dm_messages[message.id]
        return
    content = message.content
    guild = message.guild
    server_path = f"server/{guild.id}"
    if guild.id in SERVERS:
        option = GET_DATA(f"{server_path}/option.pcl")
        channel = bot.get_channel(option["view_channel"])
        if channel != None:
            try:
                embed = discord.Embed(color=discord.Colour.red())
                embed.set_author(name="< MessageDestroy >",icon_url=message.author.avatar_url)
                embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTp8q6c2DMnazxg5-LR6LQ5ajCOJLeB8150YQ&usqp=CAU")
                embed.add_field(name="< USER >",value=f"```{message.author}```",inline=False)
                embed.add_field(name="< Channel >",value=f"{message.channel.mention} `id:{message.channel.id}`",inline=False)
                if len(message.embeds) != 0:
                    for em in message.embeds:
                        await channel.send(embed=em)
                else:
                    if len(content) >= 950:
                        final = "`/...`"
                        content = content[:950 - len(final)] + final
                    embed.add_field(name="< Content >",value=f"{content}",inline=False)
                await channel.send(embed=embed)
            except Exception:
                await channel.send("`⚠システムエラーにより詳細データを送信できませんでした\nシステムを続行します:white_check_mark:`")
        if not author.bot:
            data = {
                "content":content,
                "option":{
                    "author":message.author.id,
                    "channel":message.channel.id,
                    "mention_everyone":message.mention_everyone,
                    "channel_mentions":message.channel_mentions,
                    "role_mentions":message.role_mentions,
                    "webhook_id":message.webhook_id,
                    "activity":message.activity,
                },
                "time":datetime.datetime.now()
            }
            await DUMP_DATA(f"{server_path}/delete-message/{message.id}.pcl",data)

@tasks.loop(seconds=1)
async def report_limits():
    if not os.path.exists("reports"):
        await DUMP_DATA("reports",{})
    DETAS = GET_DATA("reports")
    #ファイルから取得したデータのidでループ
    for id in DETAS:
        last_time = DETAS[id]["last_time"]
        #時間の差を求める
        TV = datetime.datetime.now() - last_time
        if TV.seconds > 60 * 15:
            if DETAS[id]["count"] > 0:
                DETAS[id]["count"] -= 1
                DETAS[id]["last_time"] = datetime.datetime.now()
    await DUMP_DATA("reports",DETAS)

@tasks.loop(seconds=3)
async def bot_status():
    global SERVERS,maintenance
    if maintenance:
        actv = discord.Game(name="< ＭＡＩＮＴＥＮＡＮＣＥ >")
        await bot.change_presence(activity=actv,status=discord.Status.do_not_disturb)
        return
    with open("logging_servers.pcl","rb") as f:
        SERVERS = pcl.load(f)
    users = len(bot.users)
    actv = discord.Game(name=f"in-server : {len(bot.guilds)} | logging-server : {len(SERVERS)} / users : {users}")
    await bot.change_presence(activity=actv,status=discord.Status.do_not_disturb)

@tasks.loop(seconds=5)
async def DELETE_LIMIT():
    folders = os.listdir("server")
    for fold in folders:
        server_path = f"server/{fold}"
        option = GET_DATA(f"{server_path}/option.pcl")
        channel = bot.get_channel(option["view_channel"])
        #メッセージデータの更新
        files = os.listdir(f"{server_path}/message")
        for file in files:
            EOF = False
            with open(f"{server_path}/message/{file}","rb") as f:
                try:
                    data = pcl.load(f)
                except Exception:
                    EOF = True
            if EOF:
                print(f"EOF : {server_path}/message/{file} / Removed")
                os.remove(f"{server_path}/message/{file}")
                continue
            time = data["time"]
            dif = datetime.datetime.now() - time
            dif = dif.days
            if dif >= 3:
                os.remove(f"{server_path}/message/{file}")
        #削除済みメッセージデータの更新
        files = os.listdir(f"{server_path}/delete-message")
        for file in files:
            EOF = False
            with open(f"{server_path}/delete-message/{file}","rb") as f:
                try:
                    data = pcl.load(f)
                except Exception:
                    EOF = True
            if EOF:
                print(f"EOF : {server_path}/delete-message/{file} / Removed")
                os.remove(f"{server_path}/delete-message/{file}")
                continue
            time = data["time"]
            dif = datetime.datetime.now() - time
            dif = dif.days
            if dif > 3:
                os.remove(f"{server_path}/delete-message/{file}")
        #アウトメッセージデータの更新
        files = os.listdir(f"{server_path}/out-message")
        for file in files:
            EOF = False
            with open(f"{server_path}/out-message/{file}","rb") as f:
                try:
                    data = pcl.load(f)
                except Exception:
                    EOF = True
            if EOF:
                print(f"EOF : {server_path}/out-message/{file} / Removed")
                os.remove(f"{server_path}/out-message/{file}")
                continue
            time = data["time"]
            dif = datetime.datetime.now() - time
            dif = dif.days
            if dif > 15:
                os.remove(f"{server_path}/out-message/{file}")
        #ユーザーデータの更新
        files = os.listdir(f"{server_path}/user")
        for file in files:
            with open(f"{server_path}/user/{file}","rb") as f:
                EOF = False
                try:
                    data = pcl.load(f)
                except Exception:
                    EOF = True
            if EOF:
                print(f"EOF : {server_path}/user/{file} / Removed")
                os.remove(f"{server_path}/user/{file}")
                continue
            user_id = int(file[:file.find(".")])
            user = bot.get_user(user_id)
            if user != None:
                data = {
                    "name":user.name,
                    "discriminator":user.discriminator,
                    "avatar_url":user.avatar,
                    "bot":user.bot,
                    "friend":user.is_friend(),
                    "block":user.is_blocked(),
                }
                with open(f"{server_path}/user/{file}","wb") as f:
                    pcl.dump(data,f)

@tasks.loop(seconds=1)
async def ViewAds():
    global ads_time
    if ads_time < datetime.datetime.now():
        AdsDatas = []
        for FileName in os.listdir("ads"):
            data = GET_DATA(f"ads/{FileName}")
            for token in data:
                if data[token]["status"] == True:
                    AdsDatas.append(data[token])
        AdsData = random.choice(AdsDatas)
        print(AdsData)
        AdsContent = AdsData["content"]
        title = "広告"
        if "setting" in AdsData:
            if AdsData["setting"] != None:
                if AdsData["setting"]["contents"] != None:
                    AdsContent = AdsData["setting"]["contents"]
                if AdsData["setting"]["title"] != None:
                    title = AdsData["setting"]["title"]
        embed = discord.Embed(title=title,color=discord.Colour.green(),description=AdsContent)
        if "setting" in AdsData:
            if AdsData["setting"] != None:
                if AdsData["setting"]["thumbnail"] != None:
                    embed.set_thumbnail(url=AdsData["setting"]["thumbnail"])
        user = bot.get_user(AdsData["author"])
        UserName = "< No search user >"
        UserIconURL = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.shoshinsha-design.com%2F2016%2F10%2F%25E3%2583%25A6%25E3%2583%25BC%25E3%2582%25B6%25E3%2583%25BC%25E3%2582%25A2%25E3%2582%25A4%25E3%2582%25B3%25E3%2583%25B3%25E7%25B4%25A0%25E6%259D%2590%2F.html&psig=AOvVaw1k3foaV7sXqX5SMy2_yuEx&ust=1620147696013000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCLDw49H-rfACFQAAAAAdAAAAABAJ"
        if user != None:
            UserName = user.name
            UserIconURL = user.avatar_url
        embed.set_footer(icon_url=UserIconURL,text=f"{UserName} - Advertisement")
        async def send(channel_id,embed):
            try:
                channel = bot.get_channel(channel_id)
                if channel != None:
                    await channel.send(embed=embed)
            except Exception:
                pass
        channel_ids = GET_ALL_AUC()
        #await asyncio.gather(*[send(i,embed) for i in channel_ids])
        ads_time = datetime.datetime.now() + datetime.timedelta(minutes=random.randint(*AdsInterval))

async def REPORT_ERROR(title,content,guild:discord.Guild,ch:discord.channel):
    admins = json.loads(open("admins.json","r").read())
    embed = discord.Embed(title=title,description=content)
    embed.add_field(name="< ERROR Details >",value=f"発生したサーバー:`{guild.name}`\n発生したチャンネル:`{ch.name}`\n発生した時刻:`{datetime.datetime.now()}`\n\n`※このembedは任意で送信されたものではなく自動的に送信されたものです`",inline=False)
    for admin_id in admins:
        admin = bot.get_user(admin_id)
        if admin:
            await admin.send(embed=embed)

class ERROR:
    def __init__(self,content,tag) -> None:
        self.content = content
        print(self.content)
        self.tag = tag


class ADS_setting:
    accessing_users = []
    def __init__(self,bot:discord.Client,ch:discord.channel,author_id,token,guild:discord.Guild) -> None:
        self.author = author_id
        self.using_token = token
        self.client = bot
        self.ch = ch
        self.guild = guild
        self.bot = bot
        self.SETTING_LIST = {
            "Title":{
                "description":"広告のタイトルを変更します",
                "type":1,
                "tag":"タイトル",
                "state":"title"
            },
            "Contents":{
                "description":"広告の内容を変更します",
                "type":2,
                "tag":"広告文",
                "state":"contents"
            },
            "Thumbnail":{
                "description":"(embedの)サムネイルを設定します",
                "type":3,
                "tag":"サムネイルのURL",
                "state":"thumbnail"
            }
        }
        self.ALL_ADS_DATAS = GET_ADS_DATAS()
        self.save_state = {
            "title":None,
            "contents":None,
            "thumbnail":None
        }
        files = GET_FILES_ADS()
        file_path = files[self.using_token]
        DATA = GET_DATA(file_path)
        if "setting" in DATA[self.using_token]:
            if DATA[self.using_token]["setting"] != None:
                self.save_state = DATA[self.using_token]["setting"]
    def author_certification(self) -> bool:
        author = self.bot.get_user(self.author)
        if author:
            return True
        else:
            return False
    def token_certification(self) -> bool:
        ALL_ADS_DATA = GET_ADS_DATAS()
        if self.using_token in ALL_ADS_DATA:
            return True
        else:
            return False
    def leave(self):
        ADS_setting.accessing_users.remove(self.author)
    def create_embed(self):
        embed = discord.Embed(title="< Advertisement operating >",color=discord.Colour.blue())
        for option in self.SETTING_LIST:
            description = self.SETTING_LIST[option]["description"]
            number = self.SETTING_LIST[option]["type"]
            embed.add_field(name=option,value=f"{description}\n**コマンド番号**:`{number}`",inline=False)
        return embed
    def cast_setting_list(self):
        numbers = {}
        for item in self.SETTING_LIST:
            numbers.update(
                {
                    self.SETTING_LIST[item]["type"]:self.SETTING_LIST[item]
                }
            )
        return numbers
    async def setting_state(self,number):
        if self.author_certification():
            author = self.bot.get_user(self.author)
            if any(number == self.SETTING_LIST[i]["type"] for i in self.SETTING_LIST):
                items = self.cast_setting_list()
                def check(msg):
                    return msg.channel == self.ch and msg.author == author
                while True:
                    tag = items[number]["tag"]
                    state = items[number]["state"]
                    print(items)
                    await self.ch.send(f"`| {tag}を入力してください |`")
                    value = None
                    try:
                        msg = await self.bot.wait_for("message",check=check,timeout=100)
                        await self.ch.send("これでよろしいですか？ [Y/N]")
                        Y_N_C = await self.bot.wait_for("message",check=check,timeout=100)
                        if Y_N_C.content.upper() == "Y":
                            value = msg.content
                        else:
                            continue
                    except asyncio.TimeoutError:
                        return ERROR("[TimeOut] - Timeout message request","T-O")
                    if state in self.save_state:
                        self.save_state[state] = value
                        await self.ch.send("`<設定を変更しました>`")
                        return
                    else:
                        return ERROR("[ERROR] - this state is not active","S-S-ACT")
            else:
                return ERROR("[ERROR] - This number is not active","S-ACT")
        else:
            return
    async def SAVE_SETTING(self):
        try:
            token_files_path = GET_FILES_ADS()
            file_path = token_files_path[self.using_token]
            DATA = GET_DATA(file_path)
            DATA[self.using_token]["setting"] = self.save_state
            print(self.save_state)
            await DUMP_DATA(file_path,DATA)
        except Exception as error:
            print(f"[{error.__class__.__name__}] {error}")
            return ERROR("[SystemError] - system Error","S-E")
    async def main_setting(self):
        embed = self.create_embed()
        embed.add_field(name="終了するには",value="番号`0`を送信するとオペレーティングを終了することができます",inline=False)
        last_number = len(self.SETTING_LIST) + 1
        embed.add_field(name="設定を保存するには",value=f"番号`{last_number}`を送信すると設定を保存できます",inline=False)
        if self.author in ADS_setting.accessing_users:
            return ERROR("[In progress] - The user who executed the command is in the process of operating","P-O")
        else:
            ADS_setting.accessing_users.append(self.author)
        if not self.token_certification():
            return ERROR("[AdsSetting_CLASS_ERROR] - This token is not a valid one","T-V")
        await self.ch.send(embed=embed)
        author = self.bot.get_user(self.author)
        def check(msg):
            return author == msg.author and self.ch == msg.channel
        while True:
            if self.author_certification():
                if not self.token_certification():
                    return ERROR("[AdsSetting_CLASS_ERROR] - This token is not a valid one","T-V")
                await self.ch.send("`| 上のコマンドのリストから実行したいコマンド番号を送信してください |`")
                try:
                    msg = await self.bot.wait_for("message",check=check,timeout=100)
                except asyncio.TimeoutError:
                    await self.ch.send("[**TimeOut**] 操作を終了します")
                    self.leave()
                    return
                try:
                    input_value = int(msg.content)
                except ValueError:
                    await self.ch.send("**数字を入力してください**")
                    continue
                if input_value == 0:
                    await self.ch.send("`<オぺレーティングを終了しました>`")
                    self.leave()
                    return
                if input_value == last_number:
                    msg = await self.ch.send("保存中...")
                    RR = await self.SAVE_SETTING()
                    if type(RR) == ERROR:
                        await self.ch.send("[**SystemError**] システムエラーが発生したため、データを保存できませんでした\n`オペレーティングを終了します ※エラーはオーナーに自動的に通知されます`")
                        await REPORT_ERROR("[SystemError]",f"{self.__class__.__name__}クラスでシステムエラーが発生しました",self.guild,self.ch)
                        self.leave()
                        return
                    await self.ch.send("<保存完了>")
                    continue
                RR = await self.setting_state(input_value)
                if type(RR) == ERROR:
                    if RR.tag == "T-O":
                        await self.ch.send("[**TimeOut**] タイムアウトしました、処理を終了します")
                        self.leave()
                        return
                    else:
                        await self.ch.send("**< システムエラーが発生しました >**\n処理を続行できないため終了します")
                        self.leave()
                        return
            else:
                await self.ch.send("`CommandStageError | コマンドを実行したユーザーが検出されなくなったため、ステージを通過できません`")
                self.leave()
                return

def GET_FILES_ADS():
    tokens = {}
    folders = os.listdir("ads")
    for file in folders:
        DATA = GET_DATA(f"ads/{file}")
        for token in DATA:
            tokens.update(
                {
                    token:f"ads/{file}"
                }
            )
    return tokens

def GET_ALL_AUC():
    folders = os.listdir(f"server")
    ids = []
    for folder in folders:
        data = GET_DATA(f"server/{folder}/option.pcl")
        if "auc_channel" in data:
            ids.append(
                data["auc_channel"]
            )
    return ids

def GET_ADS_DATAS():
    files = os.listdir("ads")
    datas = {}
    for file_path in files:
        DATAS = GET_DATA(f"ads/{file_path}")
        if DATAS != None:
            datas.update(DATAS)
    return datas

async def token_request(token,functions,*arg):
    TOKENS = GET_DATA("request_tokens")
    TOKENS.update(
        {
            token:{
                "functions":functions
            }
        }
    )
    for i in arg:
        TOKENS[token].update(i)
    await DUMP_DATA("request_tokens",TOKENS)

async def MDFA(ids):
    embed = discord.Embed(title="処理済み")
    async def edit(i):
        try:
            user = bot.get_user(i["author"])
            if user != None:
                channel = await user.create_dm()
                if channel != None:
                    msg = await channel.fetch_message(i["msg_id"])
                    if msg != None:
                        await msg.edit(embed=embed)
        except Exception:
            pass
    await asyncio.gather(*[edit(i) for i in ids])

async def ads_finalize(DETA_PATH,token,author):
    if os.path.exists(DETA_PATH):
        DATAS = GET_DATA(DETA_PATH)
        if token in DATAS:
            DATAS[token]["setting"] = None
            DATAS[token]["status"] = True
            DATAS[token]["author"] = author
            await DUMP_DATA(DETA_PATH,DATAS)
            #保存されたトークンデータを削除
            TOKEN_DATA = GET_DATA("request_tokens")
            if token in TOKEN_DATA:
                del TOKEN_DATA[token]
            await DUMP_DATA("request_tokens",TOKEN_DATA)
            user = bot.get_user(author)
            if user != None:
                await user.send(f":tada:おめでとうございます！！:tada:\nあなたが申請した広告が了承されました!\n広告はランダムでランダムな時間に表示されます、もしかしたら次はあなたの広告かも?\n__AccessToken__:`{token}`\n※このトークンを使用することで誰でもこの広告の設定が行えます、取り扱いには十分ご注意ください\n```すべての判定は公平に行われています```:white_check_mark:`decision by all LoggingAdministrator`")
    else:
        print("[ERROR] - No find DATA FILE")
        print("[TriggerAction] - Delete Token data")
        TOKENS_DATA = GET_DATA("request_tokens")
        if token in TOKENS_DATA:
            del TOKENS_DATA[token]
        await DUMP_DATA("request_tokens",TOKENS_DATA)
        print("[ChangeFIle] - request_tokens:data")

async def GET_LIST_FILES(server_path,folders):
    files = []
    for folder in folders:
        for path in os.listdir(f"{server_path}/{folder}"):
            files.append(f"{server_path}/{folder}/{path}")
    return files

async def MDL(msg,second):
    time.sleep(second)
    await msg.delete()

async def make_token(rang):
    words = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "0",
        "X",
        "x",
        "O",
        "p",
        "-",
        "/",
        "*",
        "s",
        "Y",
        "T",
        "U",
        "r",
        "e",
        "R",
        "E",
        "F",
        "f",
        "+",
        ".",
        "!"
    ]
    token = ""
    for i in range(rang):
        token += random.choice(words)
    return token

async def SEARCH_CMD(ch,server_path,content,EVNT,folder,title,embed_color=discord.Colour.blue()):
    if content.startswith(EVNT):
        if content[:content.find(" ")] == EVNT:
            try:
                id = int(content[len(EVNT):])
            except ValueError:
                await ch.send("`request processing error | help> Arguments are limited to numbers`")
                return
            await view_log(ch,id,server_path,folder,title,color=embed_color)

async def view_log(ch,U,server_path,folder,title,color=discord.Colour.blue()):
    GU = bot.get_user(U)
    count = 0
    line = 0
    cnt = ""
    files = os.listdir(f"{server_path}/{folder}")
    for file in files:
        data = GET_DATA(f"{server_path}/{folder}/{file}",mode="delete")
        if data == None:
            continue
        UI = data["option"]["author"]
        c = data["content"]
        c = c.replace("\n","\n`|` ")
        time = data["time"]
        CT = f"`-` {c}   `({time})`\n"
        if U == UI:
            count += len(CT)
            if count > 980:
                count = 0
                line += 1
                embed = discord.Embed(color=color)
                if GU:
                    embed.set_author(name=f"| -- {GU} -- |",icon_url=GU.avatar_url)
                else:
                    embed.set_author(name=f"| NoFoundUser |",icon_url="https://www.shoshinsha-design.com/wp-content/uploads/2018/07/0731-%E3%83%A6%E3%83%BC%E3%82%B5%E3%82%99%E3%83%BC%E4%B8%B8.png")
                embed.add_field(name=f"{title} (page/{line})",value=cnt,inline=False)
                await ch.send(embed=embed)
                cnt = ""
                continue
            cnt += CT
    if cnt == "":
        cnt += "```⚠現在記録データなし```"
    embed = discord.Embed(color=color)
    if GU:
        embed.set_author(name=f"| -- {GU} -- |",icon_url=GU.avatar_url)
    else:
        embed.set_author(name=f"| NoFoundUser |",icon_url="https://www.shoshinsha-design.com/wp-content/uploads/2018/07/0731-%E3%83%A6%E3%83%BC%E3%82%B5%E3%82%99%E3%83%BC%E4%B8%B8.png")
    line += 1
    embed.add_field(name=f"{title} (page/{line})",value=cnt,inline=False)
    await ch.send(embed=embed)

async def send_dm(id,content):
    user = bot.get_user(id)
    if user != None:
        await user.send(content)

async def GET_FILE_NAMES(path,cut=[".pcl"]):
    list = os.listdir(path)
    rl = []
    for l in list:
        for c in cut:
            l = l.replace(c,"")
        rl.append(l)
    return rl

async def SERVERS_SAVE():
    with open("logging_servers.pcl","wb") as f:
        pcl.dump(SERVERS,f)

def GET_DATA(path,mode="DEFAULT"):
    modes = [
        "DEFAULT",
        "DELETE"
    ]
    mode = mode.upper()
    if not mode in modes:
        return print("Unknow mode(error)")
    try:
        EOF = False
        with open(f"{path}","rb") as f:
            try:
                data = pcl.load(f)
            except Exception:
                EOF = True
                return None
        if mode == modes[1]:
            if EOF:
                os.remove(path)
    except FileNotFoundError:
        return print("FILE NOT FOUND")
    return data

async def STRING_INSERT(basic_text,content,place):
    return basic_text[:place] + content + basic_text[place:]

async def DUMP_DATA(path,data):
    with open(f"{path}","wb") as f:
        pcl.dump(data,f)

async def DUMP_JSON(path,data):
    with open(path,"w") as f:
        json.dump(data,f,indent=4)

async def VIEW_HELP(channel,help_data,color):
    try:
        embed = discord.Embed(title="< HELP >",color=eval(f"discord.Colour.{color}()"))
    except AttributeError:
        embed = discord.Embed(title="< HELP >")
    n = ""
    for data in help_data:
        if data == "log":
            if help_data[data]:
                embed.add_field(name="< データ保存について >",value="```保存されたデータログはパフォーマンス維持の為\n三日後に消去されます、その三日以内であれば保存されているので\nご自由にご使用ください```",inline=False)
                continue
        n += f"・`{data}`\n"
    n += "```コマンドの詳細を表示する場合は\n!lg.help (コマンド名)で詳細を表示できます```"
    embed.add_field(name="Commands",value=n,inline=False)
    await channel.send(embed=embed)

bot.run(TOKEN)