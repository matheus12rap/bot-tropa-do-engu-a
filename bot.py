import os
import datetime
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 🕒 Horário do Brasil corrigido e sem aviso
def hora_brasil():
    return datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=3)

intents = discord.Intents.all()
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Armazena horário de entrada e tempo total
entrada = {}
tempo_total = {}

@bot.event
async def on_ready():
    print(f"✅ Bot conectado: {bot.user}")
    print(f"🕒 Horário configurado para BRASIL")
    global canal_atividade, canal_logs
    canal_atividade = discord.utils.get(bot.guilds[0].channels, name="atividade")
    canal_logs = discord.utils.get(bot.guilds[0].channels, name="logs")
    
    # Inicia as tarefas
    atualizar_tempo_ativos.start()
    atualizar_ranking.start()

@bot.event
async def on_voice_state_update(membro, antigo, novo):
    if membro.bot:
        return

    agora = hora_brasil()
    hora = agora.strftime("%H:%M")

    # 🟢 Entrou na chamada
    if antigo.channel is None and novo.channel is not None:
        entrada[membro.id] = agora
        if membro.id not in tempo_total:
            tempo_total[membro.id] = {"nome": membro.display_name, "tempo": 0}
        if canal_atividade:
            await canal_atividade.send(f"🟢 **{membro.display_name}** | Entrou às {hora}")

    # 🔴 Saiu da chamada
    elif antigo.channel and novo.channel is None:
        if membro.id in entrada:
            ini = entrada.pop(membro.id)
            dur = agora - ini
            segundos = int(dur.total_seconds())
            tempo_total[membro.id]["tempo"] += segundos
            min = segundos // 60
            h = round(segundos / 3600, 2)
            h_ini = ini.strftime("%H:%M")
            if canal_atividade:
                await canal_atividade.send(
                    f"🔴 **{membro.display_name}** | Entrou às {h_ini} | Saiu às {hora} | ⏱️ {min} min ({h}h)"
                )

# ⏱️ Atualiza tempo de quem está na chamada a cada 1 minuto
@tasks.loop(minutes=1)
async def atualizar_tempo_ativos():
    agora = hora_brasil()
    for id_membro, horario_entrada in entrada.items():
        duracao = agora - horario_entrada
        segundos_atuais = int(duracao.total_seconds())
        # Calcula o tempo que já foi somado e atualiza
        tempo_total[id_membro]["tempo"] = (tempo_total[id_membro]["tempo"] - (tempo_total[id_membro]["tempo"] % 60)) + segundos_atuais

# 🏆 Atualiza o ranking completo a cada 15 minutos
@tasks.loop(minutes=15)
async def atualizar_ranking():
    if not canal_logs or not tempo_total:
        return
    # Ordena do maior para o menor tempo
    ordem = sorted(tempo_total.values(), key=lambda x: x["tempo"], reverse=True)
    agora = hora_brasil().strftime("%d/%m às %H:%M")
    texto = f"🏆 **RANKING DE TEMPO - TROPA DO ENGUÇA** 🏆\n🕒 Atualizado: {agora}\n\n"
    for pos, p in enumerate(ordem, 1):
        h = p["tempo"] // 3600
        m = (p["tempo"] % 3600) // 60
        texto += f"{pos}º • {p['nome']} → {h}h {m}min\n"
    await canal_logs.send(texto)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERRO: Token não encontrado! Verifique a variável DISCORD_TOKEN")
    else:
        bot.run(TOKEN)

if __name__ == "__main__":
    bot.run(TOKEN)
