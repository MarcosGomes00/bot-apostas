import os
import requests
from datetime import datetime
from telegram import Bot
from telegram.ext import Application

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

API_KEY = "1"

LIGAS_PRIORITARIAS = [
    "English Premier League",
    "Spanish La Liga",
    "Italian Serie A",
    "German Bundesliga",
    "Brazil Serie A"
]

def buscar_jogos_hoje():
    hoje = datetime.now().strftime("%Y-%m-%d")
    url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/eventsday.php?d={hoje}&s=Soccer"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except:
        return []

    jogos = []

    if data.get("events"):
        for evento in data["events"]:
            if evento.get("strLeague") in LIGAS_PRIORITARIAS:
                jogos.append({
                    "liga": evento.get("strLeague"),
                    "casa": evento.get("strHomeTeam"),
                    "fora": evento.get("strAwayTeam")
                })

    return jogos


async def enviar_analises():
    bot = Bot(TOKEN)
    jogos = buscar_jogos_hoje()

    if not jogos:
        await bot.send_message(
            chat_id=GROUP_ID,
            text="⚠️ Nenhum jogo relevante hoje."
        )
        return

    for jogo in jogos[:2]:
        mensagem = (
            f"📊 ANÁLISE AUTOMÁTICA\n\n"
            f"🏆 {jogo['liga']}\n"
            f"⚽ {jogo['casa']} x {jogo['fora']}\n\n"
            f"🎯 Mercado sugerido: Over 2.5"
        )

        await bot.send_message(
            chat_id=GROUP_ID,
            text=mensagem
        )


def main():
    app = Application.builder().token(TOKEN).build()

    app.create_task(enviar_analises())

    print("Bot iniciado com sucesso.")
    app.run_polling()


if __name__ == "__main__":
    main()
    
