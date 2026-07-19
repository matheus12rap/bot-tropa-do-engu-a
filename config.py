import os
from dotenv import load_dotenv

load_dotenv()

# Token do Discord
TOKEN = os.getenv("DISCORD_TOKEN")

# Nome dos canais
CANAL_ATIVIDADE = "atividade"
CANAL_LOGS = "logs"

# Tempo mínimo para contar presença (10 minutos)
TEMPO_MINIMO = 600
