from datetime import datetime, timedelta
import io
import logging
import math
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

def draw_outlined_text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, main: str, secondary: str, font: ImageFont.FreeTypeFont, anchor: str, align: str, outline: int = 1):
    x = xy[0]
    y = xy[1]
    draw.text((x+outline, y), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x-outline, y), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x, y+outline), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x, y-outline), text, fill=secondary, font=font, anchor=anchor, align=align)

    draw.text(xy, text, fill=main, font=font, anchor=anchor, align=align)


def split_lines(text: str, char_to_px: float) -> str:
    parts = []
    start = 0
    for i in range(1, math.ceil(char_to_px)):
        idx = math.floor(i * len(text) / char_to_px)
        parts.append(text[start:idx])
        start = idx

    parts.append(text[start:])
    return "\n".join(parts)

def split_line_by_words(text: str, textlength: int, maxlength: int) -> str:
    if textlength < maxlength:
        return text

    char_to_px = textlength / maxlength
    prev = 0
    parts: list[str] = []

    while prev < len(text):
        start_idx = prev + math.floor((len(text) - prev) / char_to_px)

        if start_idx >= len(text):
            parts.append(text[prev:])
            break

        if text[start_idx] == " ":
            parts.append(text[prev:start_idx])
            prev = start_idx + 1
            continue

        space_left = text.rfind(" ", prev, start_idx)

        if space_left != -1:
            parts.append(text[prev:space_left])
            prev = space_left + 1
            continue

        space_right = text.find(" ", start_idx)

        if space_right == -1:
            parts.append(text[prev:])
            break

        parts.append(text[prev:space_right])
        prev = space_right + 1

    return "\n".join(parts)

def put_text_over_image() -> bytes:
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    with Image.open('assets/cat.jpg') as img:
        text_size_to_height_ratio = 20
        font_size = img.height / text_size_to_height_ratio
        font = ImageFont.truetype('/usr/share/fonts/noto/NotoSans-Bold.ttf', font_size)

        draw = ImageDraw.Draw(img)

        today_str = f"Damn, it's {get_date_string(today)} already?!"
        tomorrow_str = f"What's next?\n{get_date_string(tomorrow)}? Fuck everything"
        draw_outlined_text(draw=draw, xy=(img.width/2, font_size/2+20), text=today_str, main='black', secondary='white', font=font, anchor='ms', align='center')
        draw_outlined_text(draw=draw, xy=(img.width/2, font_size*(text_size_to_height_ratio-1)-20), text=tomorrow_str, main='black', secondary='white', font=font, anchor='ms', align='center')

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


