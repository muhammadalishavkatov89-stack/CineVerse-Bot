import os
import asyncio
import httpx
from supabase import create_client
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
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
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
    user_id = update.effective_user.id
        # FOYDALANUVCHI: KINO KODI
    if text.isdigit() and not (
    user_id == ADMIN_ID and (
        context.user_data.get("awaiting_movie_code")
        or context.user_data.get("awaiting_delete_code")
    )
):
        try:
            result = supabase.table("movies").select(
                "file_id, title"
            ).eq("movie_code", text).execute()

            if result.data:
                movie = result.data[0]

                await update.message.reply_video(
                    video=movie["file_id"],
                    caption=f"🎬 {movie['title'] or 'Nomsiz kino'}"
                )
            else:
                await update.message.reply_text(
                    "😔 Bunday kodli kino topilmadi."
                )

        except Exception as e:
            print("Kino qidirish xatosi:", e)
            await update.message.reply_text(
                "❌ Kinoni topishda xatolik yuz berdi."
            )
        return

    # ADMIN: KINO QO'SHISH
    if text == "🎬 Kino qo‘shish" and user_id == ADMIN_ID:
        context.user_data["awaiting_movie_video"] = True
        await update.message.reply_text(
            "🎬 Kino videosini yuboring!"
        )
        return

    # ADMIN: KINOLAR RO'YXATI
    elif text == "📋 Kinolar ro‘yxati" and user_id == ADMIN_ID:
        try:
            result = supabase.table("movies").select(
                "movie_code, title"
            ).execute()

            movies = result.data

            if movies:
                message = "📋 Kinolar ro‘yxati:\n\n"
                for movie in movies:
                    message += (
                        f"🔢 Kod: {movie['movie_code']}\n"
                        f"🎬 Nomi: {movie['title'] or 'Nomsiz'}\n\n"
                    )
                await update.message.reply_text(message)
            else:
                await update.message.reply_text(
                    "Hozircha kinolar mavjud emas."
                )

        except Exception as e:
            print("Supabase xatosi:", e)
            await update.message.reply_text(
                "❌ Kinolarni yuklashda xatolik!"
            )
        return

    # ADMIN: KINO O'CHIRISH
    elif text == "🗑 Kino o‘chirish" and user_id == ADMIN_ID:
        context.user_data["awaiting_delete_code"] = True
        await update.message.reply_text(
            "🗑 O‘chirmoqchi bo‘lgan kino kodini yozing:"
        )
        return

    # ADMIN: KINO KODINI SAQLASH
    elif context.user_data.get("awaiting_movie_code") and user_id == ADMIN_ID:
        code = text

        if not code.isdigit():
            await update.message.reply_text(
                "❌ Kino kodi faqat raqamlardan iborat bo‘lsin!"
            )
            return

        try:
            supabase.table("movies").insert({
                "movie_code": code,
                "title": context.user_data.get("movie_title"),
                "file_id": context.user_data["movie_file_id"]
            }).execute()

            context.user_data.pop("awaiting_movie_code", None)
            context.user_data.pop("movie_file_id", None)
            context.user_data.pop("movie_title", None)

            await update.message.reply_text(
                f"✅ Kino muvaffaqiyatli saqlandi!\n"
                f"🔢 Kino kodi: {code}"
            )

        except Exception as e:
            print("Kino saqlash xatosi:", e)
            await update.message.reply_text(
                "❌ Bu kod band bo‘lishi yoki saqlashda xatolik yuz bergan bo‘lishi mumkin."
            )
        return

    # ADMIN: KINO O'CHIRISH KODI
    elif context.user_data.get("awaiting_delete_code") and user_id == ADMIN_ID:
        try:
            result = supabase.table("movies").delete().eq(
                "movie_code", text
            ).execute()

            context.user_data.pop("awaiting_delete_code", None)

            if result.data:
                await update.message.reply_text(
                    "✅ Kino katalogdan o‘chirildi!"
                )
            else:
                await update.message.reply_text(
                    "😔 Bunday kodli kino topilmadi."
                )

        except Exception as e:
            print("O‘chirish xatosi:", e)
            await update.message.reply_text(
                "❌ Kinoni o‘chirishda xatolik!"
            )
        return

    # BOSH MENYU
    elif text == "⬅️ Bosh menyu":
        await start(update, context)
        return

    # FOYDALANUVCHI MENYUSI
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

    keyboard = [
        ["🎬 Kino qo‘shish"],
        ["📋 Kinolar ro‘yxati", "🗑 Kino o‘chirish"],
        ["⬅️ Bosh menyu"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🔐 CineVerse Admin Panel\n\n"
        "Kerakli amalni tanlang:",
        reply_markup=reply_markup
    )

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.user_data.get("awaiting_movie_video"):
        return

    video = update.message.video

    if video is None:
        return

    context.user_data["movie_file_id"] = video.file_id
    context.user_data["movie_title"] = update.message.caption or "Nomsiz kino"

    context.user_data["awaiting_movie_video"] = False
    context.user_data["awaiting_movie_code"] = True

    await update.message.reply_text(
        "✅ Video qabul qilindi!\n\n"
        "🔢 Endi kino uchun raqamli kod yuboring:"
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

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL yoki SUPABASE_KEY topilmadi")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(MessageHandler(filters.VIDEO, video_handler))
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