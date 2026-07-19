import os
import datetime
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks
import pytz

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Definir fuso horário BRASIL
fuso_br = pytz.timezone("America/Sao_Paulo")

intents = discord.Intents.all()
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

entrada = {}
tempo_total = {}

@bot.event
async def on_ready():
    print(f"✅ Bot conectado: {bot.user}")
    print(f"🕒 Horário configurado para: BRASIL")
    global canal_atividade, canal_logs
    canal_atividade = discord.utils.get(bot.guilds[0].channels, name="atividade")
    canal_logs = discord.utils.get(bot.guilds[0].channels, name="logs")
    atualizar_ranking.start()

@bot.event
async def on_voice_state_update(membro, antigo, novo):
    if membro.bot:
        return

    agora = datetime.datetime.now(tz=fuso_br)
    hora = agora.strftime("%H:%M")

    if antigo.channel is None and novo.channel is not None:
        entrada[membro.id] = agora
        if canal_atividade:
            await canal_atividade.send(f"🟢 **{membro.display_name}** | Entrou às {hora}")

    elif antigo.channel and novo.channel is None:
        if membro.id in entrada:
            ini = entrada.pop(membro.id)
            dur = agora - ini
            total_seg = dur.total_seconds()
            min = round(total_seg / 60)
            h = round(total_seg / 3600, 2)
            h_ini = ini.strftime("%H:%M")

            if membro.id not in tempo_total:
                tempo_total[membro.id] = {"nome": membro.display_name, "tempo": 0}
            tempo_total[membro.id]["tempo"] += total_seg

            if canal_atividade:
                await canal_atividade.send(
                    f"🔴 **{membro.display_name}** | Entrou às {h_ini} | Saiu às {hora} | ⏱️ {min} min ({h}h)"
                )

@tasks.loop(minutes=15)
async def atualizar_ranking():
    if not canal_logs or not tempo_total:
        return
    ordem = sorted(tempo_total.values(), key=lambda x: x["tempo"], reverse=True)
    agora = datetime.datetime.now(tz=fuso_br).strftime("%d/%m às %H:%M")
    texto = f"🏆 **RANKING DE TEMPO - TROPA DO ENGUÇA** 🏆\n🕒 Atualizado: {agora}\n\n"
    for pos, p in enumerate(ordem, 1):
        h = int(p["tempo"] // 3600)
        m = int((p["tempo"] % 3600) // 60)
        texto += f"{pos}º • {p['nome']} → {h}h {m}min\n"
    await canal_logs.send(texto)

if __name__ == "__main__":
    bot.run(TOKEN)
