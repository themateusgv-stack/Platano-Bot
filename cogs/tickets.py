import discord
from discord.ext import commands
from discord.ui import View, Button
import json

FILE = "torneos.json"
LOG_CHANNEL = "📜-logs"
STAFF_ROLE = "STAFF"
MAX_JUGADORES = 10

def cargar():
    with open(FILE, "r") as f:
        return json.load(f)

def guardar(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

# =====================
# 🎮 BOTÓN INSCRIPCIÓN
# =====================
class InscripcionView(View):
    def __init__(self, torneo):
        super().__init__(timeout=None)
        self.torneo = torneo

    @discord.ui.button(label="✅ Inscribirse", style=discord.ButtonStyle.green)
    async def inscribir(self, interaction, button):

        data = cargar()

        for tipo in data:
            if self.torneo in data[tipo]:

                jugadores = data[tipo].setdefault(self.torneo + "_players", [])

                if interaction.user.name in jugadores:
                    return await interaction.response.send_message(
                        "❌ Ya estás inscrito", ephemeral=True
                    )

                if len(jugadores) >= MAX_JUGADORES:
                    return await interaction.response.send_message(
                        "❌ Torneo lleno", ephemeral=True
                    )

                jugadores.append(interaction.user.name)
                guardar(data)

                return await interaction.response.send_message(
                    "✅ Te uniste al torneo", ephemeral=True
                )

# =====================
# 🎫 BOTONES PRINCIPALES
# =====================
class TicketButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🏆 Java", style=discord.ButtonStyle.green)
    async def java(self, interaction, button):
        await mostrar_torneos(interaction, "java")

    @discord.ui.button(label="🌍 Bedrock", style=discord.ButtonStyle.blurple)
    async def bedrock(self, interaction, button):
        await mostrar_torneos(interaction, "bedrock")

# =====================
# 📋 MOSTRAR TORNEOS
# =====================
async def mostrar_torneos(interaction, tipo):

    data = cargar()
    activos = [t for t, a in data[tipo].items() if a]

    if not activos:
        return await interaction.response.send_message(
            "❌ No hay torneos activos",
            ephemeral=True
        )

    view = View()

    for torneo in activos:
        view.add_item(Button(
            label=torneo,
            style=discord.ButtonStyle.gray,
            custom_id=torneo
        ))

    async def callback(inter):
        torneo = inter.data["custom_id"]
        await crear_ticket(inter, torneo)

        canal = inter.channel
        await canal.send(
            f"🎮 Inscripción para **{torneo}**",
            view=InscripcionView(torneo)
        )

    for item in view.children:
        item.callback = callback

    await interaction.response.send_message("🎮 Elige torneo:", view=view, ephemeral=True)

# =====================
# 🎫 CREAR TICKET
# =====================
async def crear_ticket(interaction, nombre):

    guild = interaction.guild
    user = interaction.user

    staff = discord.utils.get(guild.roles, name=STAFF_ROLE)
    if not staff:
        staff = await guild.create_role(name=STAFF_ROLE)

    categoria = discord.utils.get(guild.categories, name="🎫 TICKETS")
    if not categoria:
        categoria = await guild.create_category("🎫 TICKETS")

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        staff: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True)
    }

    canal = await guild.create_text_channel(
        name=f"ticket-{nombre}-{user.name}".lower(),
        category=categoria,
        overwrites=overwrites
    )

    await canal.send(
        f"🎫 {user.mention} Ticket creado\nTorneo: **{nombre}**",
        view=CloseTicket()
    )

    logs = discord.utils.get(guild.text_channels, name=LOG_CHANNEL)
    if not logs:
        logs = await guild.create_text_channel(LOG_CHANNEL)

    await logs.send(f"📥 Ticket creado: {canal.name} | {user}")

    await interaction.response.send_message(
        f"✅ Ticket creado: {canal.mention}",
        ephemeral=True
    )

# =====================
# 🔒 CERRAR SOLO STAFF
# =====================
class CloseTicket(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Cerrar", style=discord.ButtonStyle.red)
    async def cerrar(self, interaction, button):

        staff = discord.utils.get(interaction.guild.roles, name=STAFF_ROLE)

        if staff not in interaction.user.roles:
            return await interaction.response.send_message(
                "❌ Solo STAFF puede cerrar",
                ephemeral=True
            )

        logs = discord.utils.get(interaction.guild.text_channels, name=LOG_CHANNEL)

        if logs:
            await logs.send(f"📤 Ticket cerrado: {interaction.channel.name}")

        await interaction.response.send_message("Cerrando...", ephemeral=True)
        await interaction.channel.delete()

# =====================
# ➕ ADD / REMOVE
# =====================
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def panel(self, ctx):
        embed = discord.Embed(
            title="🎮 SISTEMA PRO",
            description="Selecciona 👇",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=TicketButtons())

    @commands.command()
    async def add(self, ctx, miembro: discord.Member):
        await ctx.channel.set_permissions(miembro, view_channel=True, send_messages=True)
        await ctx.send(f"✅ {miembro.mention} añadido al ticket")

    @commands.command()
    async def remove(self, ctx, miembro: discord.Member):
        await ctx.channel.set_permissions(miembro, overwrite=None)
        await ctx.send(f"❌ {miembro.mention} removido del ticket")

async def setup(bot):
    await bot.add_cog(Tickets(bot))