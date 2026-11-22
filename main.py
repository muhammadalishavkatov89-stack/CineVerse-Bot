from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "9076497920:AAEqqyrmURvnYJAWztGkFeR_OaNspyO5YZA"


# START FUNKSIYASI
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


# TUGMALAR ISHLASHI
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


# BOTNI ISHGA TUSHIRISH
def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler)
    )

    print("🎬 CineVerse bot ishga tushdi!")

    app.run_polling()


if __name__ == "__main__":
    main()
