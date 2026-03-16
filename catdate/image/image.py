import io
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from catdate.util.string_util import get_date_string

def draw_outlined_text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, main: str, secondary: str, font: ImageFont.FreeTypeFont, anchor: str, align: str, outline: int = 1):
    x = xy[0]
    y = xy[1]
    draw.text((x+outline, y), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x-outline, y), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x, y+outline), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x, y-outline), text, fill=secondary, font=font, anchor=anchor, align=align)

    draw.text(xy, text, fill=main, font=font, anchor=anchor, align=align)


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

