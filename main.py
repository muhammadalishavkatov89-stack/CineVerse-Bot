import os
import asyncio
import httpx
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
ADMIN_ID = 8850722729
WEBHOOK_PATH = "/telegram"
PORT = int(os.getenv("PORT", 10000))
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")

app = Application.builder().token(TOKEN).build()
MOVIES = [
    {
        "title": "Avatar",
        "year": 2009,
        "genre": "Fantastika",
        "description": "Pandora sayyorasidagi sarguzasht."
    },
    {
        "title": "Titanic",
        "year": 1997,
        "genre": "Drama",
        "description": "Tarixiy kema sayohati haqidagi film."
    },
    {
        "title": "The Lion King",
        "year": 1994,
        "genre": "Animatsiya",
        "description": "Sher bolasi Simba haqidagi hikoya."
    }
]
def search_movie(query):
    results = []

    for movie in MOVIES:
        if query.lower() in movie["title"].lower():
            results.append(movie)

    return results

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
    text = update.message.text.strip()

    if text == "🔎 Kino qidirish":
        context.user_data["searching_movie"] = True
        await update.message.reply_text(
            "🔎 Qidirmoqchi bo‘lgan kino nomini yozing!"
        )

    elif text == "⭐ Mashhur kinolar":
        context.user_data["searching_movie"] = False
        await update.message.reply_text(
            "⭐ Mashhur kinolar bo‘limi tez orada!"
        )

    elif text == "🎞 Janrlar":
        context.user_data["searching_movie"] = False
        await update.message.reply_text(
            "🎞 Kino janrlari:\n"
            "• Komediya\n"
            "• Sarguzasht\n"
            "• Fantastika\n"
            "• Drama"
        )

    elif text == "ℹ️ Bot haqida":
        context.user_data["searching_movie"] = False
        await update.message.reply_text(
            "🎬 CineVerse — kino olamiga xush kelibsiz!"
        )

    elif context.user_data.get("searching_movie"):
        results = search_movie(text)

        if results:
            for movie in results:
                await update.message.reply_text(
                    f"🎬 {movie['title']}\n"
                    f"📅 Yili: {movie['year']}\n"
                    f"🎭 Janri: {movie['genre']}\n"
                    f"📝 {movie['description']}"
                )
        else:
            await update.message.reply_text(
                "😔 Bu nomdagi kino topilmadi."
            )

    else:
        await update.message.reply_text(
            "Iltimos, pastdagi tugmalardan birini tanlang."
        )



async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text(
            "⛔ Sizda admin huquqi mavjud emas!"
        )
        return

    await update.message.reply_text(
        "🔐 CineVerse Admin Paneliga xush kelibsiz!\n\n"
        "🎬 Admin boshqaruv paneli tayyorlanmoqda."
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
    app.add_handler(CommandHandler("admin", admin_panel))
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