import io
from datetime import datetime, timedelta
from math import sqrt
from PIL import Image, ImageDraw, ImageFont, ImageFile
from catdate.util.string_util import get_date_string, split_line_by_words

def draw_outlined_text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, main: str, secondary: str, font: ImageFont.FreeTypeFont, anchor: str, align: str, outline: int = 1):
    x, y = xy
    draw.text((x+outline, y), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x-outline, y), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x, y+outline), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x, y-outline), text, fill=secondary, font=font, anchor=anchor, align=align)

    draw.text(xy, text, fill=main, font=font, anchor=anchor, align=align)


def draw_top_and_bottom_text(img: ImageFile.ImageFile, toptext: str, bottomtext: str):
    draw = ImageDraw.Draw(img)

    longest = toptext if len(toptext) > len(bottomtext) else bottomtext

    BOX_OFFSET = 0.05
    x_offset = img.width * BOX_OFFSET
    y_offset = img.height * BOX_OFFSET
    box_height = img.height / 6 + y_offset
    box_width = img.width - 2 * x_offset

    font_size = sqrt(box_height * box_width / len(longest))
    font_file = '/usr/share/fonts/noto/NotoSans-Bold.ttf'
    font = ImageFont.truetype(font_file, font_size)
    if font.getlength(longest) > box_width:
        text = longest
        _, _, right, bottom =  draw.multiline_textbbox((0, 0), text, font)

        while (right > box_width or bottom > box_height) and font.size > 0:
            split_text = split_line_by_words(text, int(right), int(box_width))
            _, _, right, bottom =  draw.multiline_textbbox((0, 0), split_text, font)
            font_size -= 1
            font = ImageFont.truetype(font_file, font_size)
        font = ImageFont.truetype(font_file, font_size)

    toptext = split_line_by_words(toptext, int(font.getlength(toptext)), int(box_width))
    bottomtext = split_line_by_words(bottomtext, int(font.getlength(bottomtext)), int(box_width))

    asc, desc = font.getmetrics()
    line_height = (asc + desc)

    text_x = img.width / 2
    toptext_y = line_height
    bottomtext_y = img.height - (bottomtext.count("\n") * line_height)

    draw_outlined_text(draw=draw, xy=(text_x, toptext_y), text=toptext, main='black', secondary='white', font=font, anchor='ms', align='center')
    draw_outlined_text(draw=draw, xy=(text_x, bottomtext_y), text=bottomtext, main='black', secondary='white', font=font, anchor='ms', align='center')


def put_text_over_image() -> bytes:
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    with Image.open('assets/cat.jpg') as img:
        today_str = f"Damn, it's {get_date_string(today)} already?!"
        tomorrow_str = f"What's next?\n{get_date_string(tomorrow)}? Fuck everything"
        draw_top_and_bottom_text(img, today_str, tomorrow_str)

        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        img.show()
        return byte_arr.getvalue()

