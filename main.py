import os
from aiohttp import web
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/telegram"
PORT = int(os.getenv("PORT", 10000))
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")

app = Application.builder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔎 Kino qidirish", "⭐ Mashhur kinolar"],
        ["🎞 Janrlar", "ℹ️ Bot haqida"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🎬 CineVerse olamiga xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🔎 Kino qidirish":
        await update.message.reply_text(
            "🔎 Qidirmoqchi bo‘lgan kino nomini yozing!"
        )

    elif text == "⭐ Mashhur kinolar":
        await update.message.reply_text(
            "⭐ Mashhur kinolar bo‘limi tez orada!"
        )

    elif text == "🎞 Janrlar":
        await update.message.reply_text(
            "🎞 Kino janrlari:\n"
            "• Komediya\n"
            "• Sarguzasht\n"
            "• Fantastika\n"
            "• Drama"
        )

    elif text == "ℹ️ Bot haqida":
        await update.message.reply_text(
            "🎬 CineVerse — kino olamiga xush kelibsiz!"
        )

    else:
        await update.message.reply_text(
            "Iltimos, pastdagi tugmalardan birini tanlang."
        )


async def telegram_webhook(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="OK")


async def health(request):
    return web.Response(text="CineVerse ishlayapti!")


async def on_startup(application):
    await application.bot.set_webhook(
        url=BASE_URL + WEBHOOK_PATH
    )


async def on_cleanup(application):
    await application.bot.delete_webhook()


async def main():
    if not TOKEN or not BASE_URL:
        raise RuntimeError("BOT_TOKEN yoki RENDER_EXTERNAL_URL topilmadi")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler)
    )

    await app.initialize()
    await app.start()
    await on_startup(app)

    server = web.Application()
    server.router.add_post(WEBHOOK_PATH, telegram_webhook)
    server.router.add_get("/", health)

    runner = web.AppRunner(server)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print("🎬 CineVerse webhook ishga tushdi!")

    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())