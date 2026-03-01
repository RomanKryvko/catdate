from datetime import datetime, timedelta
import io
import logging
import os
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="hello world")


async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=put_text_over_image())

months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

def get_ordinal_indicator(n: int) -> str:
    if n == 1:
        return 'st'
    elif n == 2:
        return 'nd'
    elif n == 3:
        return 'rd'
    return 'th'

def get_date_string(dt: datetime) -> str:
    return f"{months[dt.month-1]} {dt.day}{get_ordinal_indicator(dt.day)}"

def put_text_over_image() -> bytes:
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    with Image.open('assets/cat.jpg') as img:
        text_size_to_height_ratio = 20
        font_size = img.height / text_size_to_height_ratio
        font = ImageFont.truetype('/usr/share/fonts/noto/NotoSans-Bold.ttf', font_size)

        draw = ImageDraw.Draw(img)

        today_str = f"Damn, it's {get_date_string(today)} already?!"
        tomorrow_str = f"{get_date_string(tomorrow)}? Fuck everything"
        draw.text((img.width/2, font_size/2+20), today_str, fill='black', font=font, anchor='ms')
        draw.multiline_text((img.width/2, font_size*(text_size_to_height_ratio-1)-20), "What's next?\n" + tomorrow_str, fill='black', font=font, align='center', anchor='ms')

        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        return byte_arr.getvalue()

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("Put bot API token in BOT_TOKEN env var.")
        sys.exit(1)

    application = ApplicationBuilder().token(TOKEN).build()
    handlers = [
        CommandHandler('start', start),
        CommandHandler('img', image)
    ]
    for h in handlers:
        application.add_handler(h)

    application.run_polling()

