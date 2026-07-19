from utils import agora, formatar_tempo

entrada = {}
tempo_total = {}


async def usuario_entrou(member):
    entrada[member.id] = agora()

    if member.id not in tempo_total:
        tempo_total[member.id] = {
            "nome": member.display_name,
            "tempo": 0
        }


async def usuario_saiu(member):
    if member.id not in entrada:
        return None

    inicio = entrada.pop(member.id)

    segundos = int((agora() - inicio).total_seconds())

    tempo_total[member.id]["tempo"] += segundos

    return {
        "entrada": inicio,
        "saida": agora(),
        "tempo": segundos,
        "texto": formatar_tempo(segundos)
    }
