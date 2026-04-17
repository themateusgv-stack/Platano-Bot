import discord
from discord.ext import commands
import re
import time

# =====================
# CONFIG
# =====================
link_regex = r"(https?://\S+|discord.gg/\S+)"
usuarios = {}
joins = []
anti_raid_activo = True

ROL_AUTO = "🍌 -ᴘʟᴀᴛᴀɴɪᴛᴏꜱ -🍌"
CANAL_BIENVENIDA = "👋-bienvenida"
CANAL_LOGS = "📜-logs"

# =====================
# COG
# =====================
class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================
    # 🚫 LINKS + SPAM
    # =====================
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # 🚫 BORRAR LINKS
        if re.search(link_regex, message.content.lower()):
            await message.delete()
            await message.channel.send(
                f"{message.author.mention} 🚫 No puedes enviar links",
                delete_after=3
            )

        # ⚠️ SPAM (SOLO AVISO)
        ahora = time.time()
        user = message.author.id

        if user not in usuarios:
            usuarios[user] = []

        usuarios[user].append(ahora)
        usuarios[user] = [t for t in usuarios[user] if ahora - t < 5]

        if len(usuarios[user]) > 6:
            await message.channel.send(
                f"{message.author.mention} ⚠️ No hagas spam",
                delete_after=3
            )

        await self.bot.process_commands(message)

    # =====================
    # 🟡 AUTO ROL + RAID
    # =====================
    @commands.Cog.listener()
    async def on_member_join(self, member):
        global anti_raid_activo

        guild = member.guild

        # 🟡 AUTO ROL
        rol = discord.utils.get(guild.roles, name=ROL_AUTO)
        if rol:
            await member.add_roles(rol)

        # =====================
        # 🚨 ANTI RAID (SOLO AVISA)
        # =====================
        ahora = time.time()
        joins.append(ahora)

        recientes = [t for t in joins if ahora - t < 10]

        if anti_raid_activo and len(recientes) >= 5:
            canal_logs = discord.utils.get(guild.text_channels, name=CANAL_LOGS)

            if canal_logs:
                await canal_logs.send("🚨 POSIBLE RAID DETECTADO")

        # =====================
        # 🎉 BIENVENIDA
        # =====================
        canal = discord.utils.get(guild.text_channels, name=CANAL_BIENVENIDA)

        if canal:
            embed = discord.Embed(
                title="🎉 Nuevo miembro",
                description=f"Bienvenido {member.mention} 🍌",
                color=discord.Color.yellow()
            )
            await canal.send(embed=embed)

    # =====================
    # 🔐 COMANDOS
    # =====================

    # 🟢 ACTIVAR RAID
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def raid_on(self, ctx):
        global anti_raid_activo
        anti_raid_activo = True
        await ctx.send("🟢 Anti-raid ACTIVADO")

    # 🔴 DESACTIVAR RAID
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def raid_off(self, ctx):
        global anti_raid_activo
        anti_raid_activo = False
        await ctx.send("🔴 Anti-raid DESACTIVADO")

    # 🧹 LIMPIAR CHAT
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, cantidad: int):
        await ctx.channel.purge(limit=cantidad)
        await ctx.send(f"🧹 Se borraron {cantidad} mensajes", delete_after=3)

    # ⚠️ WARN
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, miembro: discord.Member):
        await ctx.send(f"⚠️ {miembro.mention} advertido")

    # 🔒 LOCK CANAL
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Canal bloqueado")

    # 🔓 UNLOCK CANAL
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock_channel(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 Canal desbloqueado")

# =====================
# SETUP
# =====================
async def setup(bot):
    await bot.add_cog(Moderacion(bot))