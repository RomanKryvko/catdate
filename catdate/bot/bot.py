import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from catdate.image.image import put_text_over_image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="hello world")


async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=put_text_over_image())


def run_bot(token: str):
    application = ApplicationBuilder().token(token).build()
    handlers = [
        CommandHandler('start', start),
        CommandHandler('img', image)
    ]
    for h in handlers:
        application.add_handler(h)

    application.run_polling()

