import os
import datetime
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks

# Carrega o token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 🕒 Fuso horário BRASIL (UTC-3)
def agora_brasil():
    return datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=3)

# Permissões necessárias
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Armazena dados de forma segura
entrada = {}          # {id_membro: horario_entrada}
tempo_total = {}      # {id_membro: {"nome": "...", "segundos": 0}}

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como: {bot.user}")
    print(f"🕒 Horário: Brasil")

    global canal_atividade, canal_logs
    servidor = bot.guilds[0]
    canal_atividade = discord.utils.get(servidor.channels, name="atividade")
    canal_logs = discord.utils.get(servidor.channels, name="logs")

    # Ao ligar, só registra quem já está na sala, sem enviar mensagem
    for membro in servidor.members:
        if not membro.bot and membro.voice and membro.voice.channel:
            if membro.id not in entrada:
                entrada[membro.id] = agora_brasil()
            if membro.id not in tempo_total:
                tempo_total[membro.id]["segundos"] = max(
    tempo_total[membro.id]["segundos"],
    segundos
)

    # Inicia as funções
    atualizar_tempo.start()
    gerar_ranking.start()

@bot.event
async def on_voice_state_update(membro, estado_antigo, estado_novo):
    if membro.bot:
        return

    agora = agora_brasil()
    hora = agora.strftime("%H:%M")

    # 🟢 Entrou na chamada
    if estado_antigo.channel is None and estado_novo.channel is not None:
        if membro.id not in entrada:
            entrada[membro.id] = agora
            if membro.id not in tempo_total:
                tempo_total[membro.id] = {"nome": membro.display_name, "segundos": 0}
            # Envia mensagem apenas uma vez
            if canal_atividade:
                await canal_atividade.send(f"🟢 **{membro.display_name}** | Entrou às {hora}")

    # 🔴 Saiu da chamada
    elif estado_antigo.channel is not None and estado_novo.channel is None:
        if membro.id in entrada:
            horario_entrada = entrada.pop(membro.id)
            duracao = agora - horario_entrada
            segundos = int(duracao.total_seconds())

            # Soma o tempo total
            if membro.id not in tempo_total:
                tempo_total[membro.id] = {"nome": membro.display_name, "segundos": 0}
            tempo_total[membro.id]["segundos"] += segundos

            # Converte para horas e minutos
            h = segundos // 3600
            m = (segundos % 3600) // 60

            if canal_atividade:
                await canal_atividade.send(
                    f"🔴 **{membro.display_name}** | Entrou às {horario_entrada.strftime('%H:%M')} | Saiu às {hora} | ⏱️ {h}h {m}min"
                )

# ⏱️ Atualiza o tempo de quem está na sala a cada 1 minuto
@tasks.loop(minutes=1)
async def atualizar_tempo():
    agora = agora_brasil()

    for id_membro, horario_entrada in entrada.items():
        if id_membro not in tempo_total:
            continue

        # Tempo desde a última entrada
        segundos_atuais = int((agora - horario_entrada).total_seconds())

        # Atualiza apenas o tempo atual da sessão
        tempo_total[id_membro]["segundos"] = segundos_atuais

# 🏆 Gera o ranking completo a cada 5 minutos
@tasks.loop(minutes=5)
async def gerar_ranking():
    if not canal_logs or not tempo_total:
        return

    # Ordena do maior para o menor tempo
    lista_ordenada = sorted(tempo_total.values(), key=lambda x: x["segundos"], reverse=True)
    agora = agora_brasil().strftime("%d/%m às %H:%M")

    texto = f"🏆 **RANKING DE TEMPO - TROPA DO ENGUÇA** 🏆\n🕒 Atualizado: {agora}\n\n"
    for posicao, dados in enumerate(lista_ordenada, 1):
        seg = dados["segundos"]
        h = seg // 3600
        m = (seg % 3600) // 60
        texto += f"{posicao}º • {dados['nome']} → {h}h {m}min\n"

    await canal_logs.send(texto)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERRO: Token não encontrado! Verifique as variáveis.")
    else:
        bot.run(TOKEN)
