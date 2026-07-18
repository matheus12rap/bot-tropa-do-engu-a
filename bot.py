import os
import datetime
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks
import config

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN") or config.TOKEN

# Permissões completas
intents = discord.Intents.all()
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

entrada = {}
tempo_total = {}

@bot.event
async def on_ready():
    print("="*40)
    print(f"✅ Bot conectado: {bot.user}")

    # Busca os canais e avisa se encontrou
    global canal_atividade, canal_logs
    canal_atividade = discord.utils.get(bot.get_all_channels(), name="atividade")
    canal_logs = discord.utils.get(bot.get_all_channels(), name="logs")

    if canal_atividade:
        print(f"📝 Canal #atividade encontrado!")
    else:
        print("❌ ERRO: Canal #atividade NÃO ENCONTRADO — verifique o nome!")

    if canal_logs:
        print(f"📊 Canal #logs encontrado!")
    else:
        print("❌ ERRO: Canal #logs NÃO ENCONTRADO — verifique o nome!")

    print("="*40)
    atualizar_ranking.start()


@bot.event
async def on_voice_state_update(membro, antigo, novo):
    if membro.bot:
        return

    agora = datetime.datetime.now()
    hora = agora.strftime("%H:%M")

    # Entrou em alguma sala
    if antigo.channel is None and novo.channel is not None:
        entrada[membro.id] = agora
        print(f"📥 {membro.display_name} entrou às {hora}") # aparece no terminal também
        if canal_atividade:
            await canal_atividade.send(f"🟢 **{membro.display_name}** | Entrou às {hora}")

    # Saiu da sala
    elif antigo.channel is not None and novo.channel is None:
        if membro.id in entrada:
            hora_ini = entrada.pop(membro.id)
            dur = agora - hora_ini
            min = round(dur.total_seconds() / 60)
            h = round(dur.total_seconds() / 3600, 2)
            hora_entrada = hora_ini.strftime("%H:%M")

            # Soma tempo
            if membro.id not in tempo_total:
                tempo_total[membro.id] = {"nome": membro.display_name, "tempo": 0}
            tempo_total[membro.id]["tempo"] += dur.total_seconds()

            print(f"📤 {membro.display_name} saiu às {hora} | Tempo: {min}min") # log no terminal
            if canal_atividade:
                await canal_atividade.send(
                    f"🔴 **{membro.display_name}** | Entrou às {hora_entrada} | Saiu às {hora} | ⏱️ {min} min ({h}h)"
                )


@tasks.loop(minutes=10)
async def atualizar_ranking():
    if not canal_logs or len(tempo_total) == 0:
        return

    ordem = sorted(tempo_total.values(), key=lambda x: x["tempo"], reverse=True)
    texto = "🏆 **RANKING DE TEMPO - TROPA DO ENGUÇA** 🏆\n"
    texto += f"Atualizado: {datetime.datetime.now().strftime('%d/%m %H:%M')}\n\n"

    for pos, p in enumerate(ordem, 1):
        h = round(p["tempo"] / 3600, 1)
        m = round((p["tempo"] % 3600) / 60)
        texto += f"{pos}º • {p['nome']} → {h}h {m}min\n"

    await canal_logs.send(texto)


if __name__ == "__main__":
    bot.run(TOKEN)