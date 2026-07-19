from datetime import datetime
from zoneinfo import ZoneInfo

def agora():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))

def formatar_tempo(segundos):
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    return f"{horas}h {minutos}min"
