from atividade import tempo_total
from utils import formatar_tempo

mensagem_ranking = None


async def atualizar_ranking(canal):

    global mensagem_ranking

    if not tempo_total:
        return

    ranking = sorted(
        tempo_total.values(),
        key=lambda x: x["tempo"],
        reverse=True
    )

    texto = "🏆 **RANKING TROPA DO ENGUIÇA** 🏆\n\n"

    for posicao, jogador in enumerate(ranking, start=1):

        texto += (
            f"**{posicao}º** • "
            f"{jogador['nome']} → "
            f"{formatar_tempo(jogador['tempo'])}\n"
        )

    if mensagem_ranking is None:

        mensagem_ranking = await canal.send(texto)

    else:

        try:
            await mensagem_ranking.edit(content=texto)

        except:

            mensagem_ranking = await canal.send(texto)
