import os
import requests
from datetime import datetime
from telegram.ext import Updater

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

API_KEY = "1"  # TheSportsDB pública

LIGAS_PRIORITARIAS = [
    "English Premier League",
    "Spanish La Liga",
    "Italian Serie A",
    "German Bundesliga",
    "Brazil Serie A"
]

# ================================
# BUSCAR JOGOS DO DIA
# ================================

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
            liga = evento.get("strLeague")

            if liga in LIGAS_PRIORITARIAS:
                jogos.append({
                    "liga": liga,
                    "casa": evento.get("strHomeTeam"),
                    "fora": evento.get("strAwayTeam")
                })

    return jogos

# ================================
# SISTEMA DE SCORE BASE (Evolutivo depois)
# ================================

def calcular_score_base(jogo):
    score = 60

    # Times grandes tendem a jogos mais movimentados
    if any(time in jogo["casa"] for time in ["City", "Barcelona", "Real", "Bayern"]):
        score += 10

    if any(time in jogo["fora"] for time in ["City", "Barcelona", "Real", "Bayern"]):
        score += 10

    # Liga ofensiva
    if "Premier" in jogo["liga"] or "Bundesliga" in jogo["liga"]:
        score += 10

    if score > 95:
        score = 95

    return score

# ================================
# ENVIO AUTOMÁTICO
# ================================

def enviar_analises(bot):
    jogos = buscar_jogos_hoje()

    if not jogos:
        bot.send_message(chat_id=GROUP_ID, text="⚠️ Nenhum jogo relevante encontrado hoje.")
        return

    candidatos = []

    for jogo in jogos:
        score = calcular_score_base(jogo)

        if score >= 75:
            candidatos.append((jogo, score))

    candidatos.sort(key=lambda x: x[1], reverse=True)

    # ====================
    # ENTRADAS SIMPLES
    # ====================

    for jogo, score in candidatos[:2]:
        mensagem = (
            f"📊 ANÁLISE AUTOMÁTICA\n\n"
            f"🏆 Liga: {jogo['liga']}\n"
            f"⚽ {jogo['casa']} x {jogo['fora']}\n\n"
            f"🔥 Score: {score}%\n"
            f"🎯 Mercado sugerido: Over 2.5\n"
            f"📈 Perfil: Agressivo Controlado"
        )

        bot.send_message(chat_id=GROUP_ID, text=mensagem)

    # ====================
    # MÚLTIPLA
    # ====================

    if len(candidatos) >= 2 and candidatos[0][1] >= 85 and candidatos[1][1] >= 85:
        jogo1 = candidatos[0][0]
        jogo2 = candidatos[1][0]

        mensagem_multipla = (
            f"🔥 MÚLTIPLA DO DIA\n\n"
            f"1️⃣ {jogo1['casa']} x {jogo1['fora']} - Over 2.5\n"
            f"2️⃣ {jogo2['casa']} x {jogo2['fora']} - Over 2.5\n\n"
            f"⚡ Estratégia Agressiva"
        )

        bot.send_message(chat_id=GROUP_ID, text=mensagem_multipla)

# ================================
# MAIN
# ================================

def main():
    updater = Updater(TOKEN)
    print("Bot automático iniciado...")

    enviar_analises(updater.bot)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
