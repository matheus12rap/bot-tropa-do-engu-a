import discord
from discord.ext import commands, tasks

from config import TOKEN, CANAL_ATIVIDADE, CANAL_LOGS
from atividade import usuario_entrou, usuario_saiu
from ranking import atualizar_ranking

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

canal_atividade = None
canal_logs = None


@bot.event
async def on_ready():
    global canal_atividade, canal_logs

    print(f"✅ Bot conectado como {bot.user}")

    guild = bot.guilds[0]

    canal_atividade = discord.utils.get(
        guild.text_channels,
        name=CANAL_ATIVIDADE
    )

    canal_logs = discord.utils.get(
        guild.text_channels,
        name=CANAL_LOGS
    )

    if not atualizar_ranking_loop.is_running():
        atualizar_ranking_loop.start()


@bot.event
async def on_voice_state_update(member, before, after):

    if member.bot:
        return

    # Ignora eventos que não mudaram de canal
    if before.channel == after.channel:
        return

    # Entrou em um canal de voz
    if before.channel is None and after.channel is not None:

        await usuario_entrou(member)

        if canal_atividade:
            await canal_atividade.send(
                f"🟢 **{member.display_name}** entrou em **{after.channel.name}**"
            )

    # Saiu completamente do canal de voz
    elif before.channel is not None and after.channel is None:

        dados = await usuario_saiu(member)

        if dados and canal_atividade:
            await canal_atividade.send(
                f"🔴 **{member.display_name}** saiu.\n"
                f"⏱️ Tempo: **{dados['texto']}**"
            )

    # Trocou de canal de voz
    elif before.channel != after.channel:

        await usuario_saiu(member)
        await usuario_entrou(member)


@tasks.loop(minutes=5)
async def atualizar_ranking_loop():

    if canal_logs:
        await atualizar_ranking(canal_logs)


bot.run(TOKEN)
