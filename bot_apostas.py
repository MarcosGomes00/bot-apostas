import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes

TOKEN = '8413563055:AAE-OrByO3ErSbfU882ExbhzgzVy0T1XKMQ'
GROUP_ID = -1003773773236

palpites = {}
import random

async def envio_automatico(application):
    jogos = [
        ("Barcelona x PSG", "Over 2.5", 1.90),
        ("City x Bayern", "Ambas Marcam", 1.75),
        ("Inter x Milan", "Under 3.5", 1.65),
    ]

    jogo_id = 2

    while True:
        jogo = random.choice(jogos)

        await enviar_call(
            application,
            jogo_id,
            jogo[0],
            jogo[1],
            jogo[2],
            1,
            "Alta",
            "Bet365"
        )

        jogo_id += 1

        await asyncio.sleep(3600)

async def enviar_call(application, jogo_id, jogo, mercado, odd, stake, confianca, melhor_casa):
    palpites[jogo_id] = {'jogo': jogo, 'mercado': mercado, 'status': 'ativo'}

    teclado = [[InlineKeyboardButton("Marcar como usada", callback_data=f"usar_{jogo_id}")]]
    markup = InlineKeyboardMarkup(teclado)

    mensagem = (
        f"🎯 Aposta do dia\n"
        f"📅 {jogo}\n"
        f"💰 Mercado: {mercado}\n"
        f"💵 Odd: {odd}\n"
        f"📊 Confiança: {confianca}\n"
        f"✅ Melhor casa: {melhor_casa}"
    )

    await application.bot.send_message(
        chat_id=GROUP_ID,
        text=mensagem,
        reply_markup=markup
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("usar_"):
        jogo_id = int(data.split("_")[1])
        palpites[jogo_id]['status'] = 'usado'

        await query.edit_message_text(
            text=f"{query.message.text}\n\n✅ Marcado como usada"
        )

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CallbackQueryHandler(callback_handler))

    print("Bot iniciado...")

    application.run_polling()


if __name__ == "__main__":
    main()
