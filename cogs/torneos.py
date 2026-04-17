import discord
from discord.ext import commands
import json, os

FILE = "torneos.json"

def cargar():
    if not os.path.exists(FILE):
        data = {
            "java": {"UHC PRO": True},
            "bedrock": {"Survival PRO": True}
        }
        with open(FILE, "w") as f:
            json.dump(data, f, indent=4)
        return data

    with open(FILE, "r") as f:
        return json.load(f)

def guardar(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

class Torneos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def crear_torneo(self, ctx, tipo, *, nombre):
        data = cargar()
        tipo = tipo.lower()

        if tipo not in data:
            return await ctx.send("❌ Usa: java o bedrock")

        data[tipo][nombre] = True
        guardar(data)

        await ctx.send(f"✅ Torneo creado: {nombre}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def borrar_torneo(self, ctx, tipo, *, nombre):
        data = cargar()
        tipo = tipo.lower()

        if tipo not in data:
            return await ctx.send("❌ Usa: java o bedrock")

        if nombre not in data[tipo]:
            return await ctx.send("❌ Ese torneo no existe")

        del data[tipo][nombre]
        guardar(data)

        await ctx.send(f"🗑️ Torneo eliminado: {nombre}")

async def setup(bot):
    await bot.add_cog(Torneos(bot))