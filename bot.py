import discord
from discord.ext import commands
import os

# KEEP ALIVE
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot activo 24/7"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# CONFIG
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 


bot = commands.Bot(command_prefix="!", intents=intents)

# READY
@bot.event
async def on_ready():
    print(f"🔥 Bot listo como {bot.user}")

    for archivo in os.listdir("./cogs"):
        if archivo.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{archivo[:-3]}")
                print(f"✅ Cargado: {archivo}")
            except Exception as e:
                print(f"❌ Error en {archivo}: {e}")

# START
import os
bot.run(os.getenv("TOKEN"))



