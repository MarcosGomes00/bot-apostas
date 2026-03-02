import os
import requests
import json
import math
import asyncio
from datetime import datetime
from telegram.ext import Application

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

API_KEY = "1"
HISTORICO_FILE = "historico.json"
ODD_MEDIA = 1.90

LIGAS_PRIORITARIAS = [
    "English Premier League",
    "Spanish La Liga",
    "Italian Serie A",
    "German Bundesliga",
    "Brazil Serie A"
]

def carregar():
    try:
        with open(HISTORICO_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def salvar(data):
    with open(HISTORICO_FILE, "w") as f:
        json.dump(data, f, indent=4)

def buscar_jogos():
    hoje = datetime.now().strftime("%Y-%m-%d")
    url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/eventsday.php?d={hoje}&s=Soccer"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()
    except:
        return []

    jogos = []

    if data and data.get("events"):
        for e in data["events"]:
            if e.get("strLeague") in LIGAS_PRIORITARIAS:
                jogos.append({
                    "id": e.get("idEvent"),
                    "liga": e.get("strLeague"),
                    "casa": e.get("strHomeTeam"),
                    "fora": e.get("strAwayTeam"),
                    "gols_casa": e.get("intHomeScore"),
                    "gols_fora": e.get("intAwayScore")
                })

    return jogos

def poisson_over25(lmb):
    p0 = math.exp(-lmb)
    p1 = math.exp(-lmb) * lmb
    p2 = (math.exp(-lmb) * lmb**2) / 2
    return round((1 - (p0 + p1 + p2)) * 100, 2)

def lambda_geral():
    hist = carregar()
    finalizados = [h for h in hist if h.get("total_gols") is not None]
    if len(finalizados) == 0:
        return 2.6
    return sum(h["total_gols"] for h in finalizados) / len(finalizados)

async def enviar_entrada(app):
    jogos = buscar_jogos()
    if not jogos:
        return

    lmb = lambda_geral()
    prob = poisson_over25(lmb)

    if prob < 60:
        return

    jogo = jogos[0]

    mensagem = (
        f"📊 ENTRADA\n\n"
        f"🏆 {jogo['liga']}\n"
        f"⚽ {jogo['casa']} x {jogo['fora']}\n"
        f"🎯 Over 2.5\n"
        f"🧮 Probabilidade: {prob}%"
    )

    await app.bot.send_message(chat_id=GROUP_ID, text=mensagem)

    hist = carregar()
    hist.append({
        "id": jogo["id"],
        "data": datetime.now().strftime("%Y-%m-%d"),
        "liga": jogo["liga"],
        "total_gols": None,
        "resultado": None
    })
    salvar(hist)

async def atualizar_resultados():
    hist = carregar()
    jogos = buscar_jogos()

    for h in hist:
        if h["resultado"] is None:
            for jogo in jogos:
                if jogo["id"] == h["id"] and jogo["gols_casa"] and jogo["gols_fora"]:
                    total = int(jogo["gols_casa"]) + int(jogo["gols_fora"])
                    h["total_gols"] = total
                    h["resultado"] = "win" if total >= 3 else "loss"

    salvar(hist)

async def relatorio_diario(app):
    while True:
        await asyncio.sleep(86400)  # 24 horas

        hoje = datetime.now().strftime("%Y-%m-%d")
        hist = carregar()

        entradas_hoje = [h for h in hist if h.get("data") == hoje]
        finalizadas = [h for h in entradas_hoje if h.get("resultado") in ["win", "loss"]]

        total = len(finalizadas)
        acertos = len([h for h in finalizadas if h["resultado"] == "win"])
        erros = len([h for h in finalizadas if h["resultado"] == "loss"])

        lucro = (acertos * (ODD_MEDIA - 1)) - (erros * 1)
        roi = round((lucro / total) * 100, 2) if total > 0 else 0
        taxa = round((acertos / total) * 100, 2) if total > 0 else 0

        geral = [h for h in hist if h.get("resultado") in ["win", "loss"]]
        taxa_geral = round((len([h for h in geral if h["resultado"] == "win"]) / len(geral)) * 100, 2) if len(geral) > 0 else 0

        mensagem = (
            f"📊 RELATÓRIO DIÁRIO\n\n"
            f"🎯 Total: {total}\n"
            f"✅ Acertos: {acertos}\n"
            f"❌ Erros: {erros}\n\n"
            f"📈 Taxa: {taxa}%\n"
            f"💰 Lucro: {round(lucro,2)} unidades\n"
            f"📊 ROI: {roi}%\n\n"
            f"🔥 Taxa Geral Sistema: {taxa_geral}%"
        )

        await app.bot.send_message(chat_id=GROUP_ID, text=mensagem)

async def loop_principal(app):
    while True:
        await enviar_entrada(app)
        await atualizar_resultados()
        await asyncio.sleep(1800)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.create_task(loop_principal(app))
    app.create_task(relatorio_diario(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
