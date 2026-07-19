import os
import datetime
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 🕒 Horário do Brasil correto
def hora_brasil():
    return datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=3)

intents = discord.Intents.all()
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Variáveis de controle
entrada = {}          # Guarda quem está na sala e horário
tempo_total = {}      # Guarda tempo acumulado
ja_registrado = set() # Evita repetir mensagens de entrada

@bot.event
async def on_ready():
    print(f"✅ Bot conectado: {bot.user}")
    print(f"🕒 Horário: Brasil")

    servidor = bot.guilds[0]
    global canal_atividade, canal_logs
    canal_atividade = discord.utils.get(servidor.channels, name="atividade")
    canal_logs = discord.utils.get(servidor.channels, name="logs")

    # 🟢 Ao ligar: só registra quem já está na sala, SEM enviar mensagem
    for membro in servidor.members:
        if not membro.bot and membro.voice and membro.voice.channel:
            if membro.id not in entrada:
                entrada[membro.id] = hora_brasil()
            if membro.id not in tempo_total:
                tempo_total[membro.id] = {"nome": membro.display_name, "segundos": 0}

    # Inicia contagem
    contar_tempo.start()
    atualizar_ranking.start()

@bot.event
async def on_voice_state_update(membro, antigo, novo):
    if membro.bot:
        return

    agora = hora_brasil()
    hora_str = agora.strftime("%H:%M")

    # 🟢 Entrou na chamada: envia mensagem SÓ se não tinha registrado antes
    if antigo.channel is None and novo.channel is not None:
        if membro.id not in entrada:
            entrada[membro.id] = agora
            if membro.id not in tempo_total:
                tempo_total[membro.id] = {"nome": membro.display_name, "segundos": 0}
            # Só envia mensagem uma vez
            if membro.id not in ja_registrado:
                ja_registrado.add(membro.id)
                if canal_atividade:
                    await canal_atividade.send(f"🟢 **{membro.display_name}** | Entrou às {hora_str}")

    # 🔴 Saiu da chamada: calcula e soma tempo, limpa registro
    elif antigo.channel and novo.channel is None:
        if membro.id in entrada:
            inicio = entrada.pop(membro.id)
            ja_registrado.discard(membro.id) # Libera para registrar de novo depois

            duracao = agora - inicio
            segundos = int(duracao.total_seconds())
            tempo_total[membro.id]["segundos"] += segundos

            h = segundos // 3600
            m = (segundos % 3600) // 60

            if canal_atividade:
                await canal_atividade.send(
                    f"🔴 **{membro.display_name}** | Entrou às {inicio.strftime('%H:%M')} | Saiu às {hora_str} | ⏱️ {h}h {m}min"
                )

# ⏱️ Conta tempo de quem está na sala a cada 1 minuto
@tasks.loop(minutes=1)
async def contar_tempo():
    agora = hora_brasil()
    for membro_id, inicio in entrada.items():
        duracao = agora - inicio
        segundos = int(duracao.total_seconds())
        tempo_total[membro_id]["segundos"] = segundos

# 🏆 Atualiza ranking a cada 5 minutos
@tasks.loop(minutes=5)
async def atualizar_ranking():
    if not canal_logs or not tempo_total:
        return

    lista_ordenada = sorted(tempo_total.values(), key=lambda x: x["segundos"], reverse=True)
    agora = hora_brasil().strftime("%d/%m às %H:%M")

    texto = f"🏆 **RANKING DE TEMPO - TROPA DO ENGUÇA** 🏆\n🕒 Atualizado: {agora}\n\n"
    for pos, dado in enumerate(lista_ordenada, 1):
        seg = dado["segundos"]
        h = seg // 3600
        m = (seg % 3600) // 60
        texto += f"{pos}º • {dado['nome']} → {h}h {m}min\n"

    await canal_logs.send(texto)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERRO: Token não encontrado!")
    else:
        bot.run(TOKEN)
