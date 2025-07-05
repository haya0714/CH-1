import discord
import os
import asyncio
from dotenv import load_dotenv
from utils import get_ai_reply
from flask import Flask
from threading import Thread

# 啟動 .env 變數
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 建立 Discord client
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# ✅ Discord bot 啟動時印出訊息
@client.event
async def on_ready():
    print(f"🧠 登入為：{client.user}")

# ✅ 接收所有使用者訊息，自動回應
@client.event
async def on_message(message):
    if message.author.bot:
        return

    prompt = message.content.strip()
    loop = asyncio.get_event_loop()
    reply = await loop.run_in_executor(None, get_ai_reply, prompt)
    await message.reply(reply or "……")

# ✅ Flask 用來維持 Replit 活著
app = Flask(__name__)

@app.route("/")
def home():
    return "I'm alive.", 200

def run_web():
    app.run(host="0.0.0.0", port=8080)

# ✅ 啟動 Flask Web Server
Thread(target=run_web).start()

# ✅ 啟動 Discord Bot
client.run(TOKEN)
