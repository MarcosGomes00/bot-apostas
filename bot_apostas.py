from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler
import random
import time
import threading

TOKEN = '8413563055:AAE-OrByO3ErSbfU882ExbhzgzVy0T1XKMQ'
GROUP_ID = -1003773773236

palpites = {}


def envio_automatico(bot):
    jogos = [
        ("Barcelona x PSG", "Over 2.5", 1.90),
        ("City x Bayern", "Ambas Marcam", 1.75),
        ("Inter x Milan", "Under 3.5", 1.65),
    ]

    jogo_id = 2

    while True:
        jogo = random.choice(jogos)

        enviar_call(
            bot,
            jogo_id,
            jogo[0],
            jogo[1],
            jogo[2],
            1,
            "Alta",
            "Bet365"
        )

        jogo_id += 1
        time.sleep(3600)  # 1 hora


def enviar_call(bot, jogo_id, jogo, mercado, odd, stake, confianca, melhor_casa):
    palpites[jogo_id] = {
        'jogo': jogo,
        'mercado': mercado,
        'status': 'ativo'
    }

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

    bot.send_message(
        chat_id=GROUP_ID,
        text=mensagem,
        reply_markup=markup
    )


def callback_handler(update, context):
    query = update.callback_query
    query.answer()

    data = query.data

    if data.startswith("usar_"):
        jogo_id = int(data.split("_")[1])
        palpites[jogo_id]['status'] = 'usado'

        query.edit_message_text(
            text=f"{query.message.text}\n\n✅ Marcado como usada"
        )


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CallbackQueryHandler(callback_handler))

    print("Bot iniciado...")

    # Thread para envio automático
    thread = threading.Thread(target=envio_automatico, args=(updater.bot,))
    thread.start()

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
