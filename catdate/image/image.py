import io
from datetime import datetime, timedelta
import logging
from PIL import Image, ImageDraw, ImageFont, ImageFile
from catdate.util.string_util import get_date_string, split_line_by_words

logger = logging.getLogger(__name__)

def draw_outlined_text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, main: str, secondary: str, font: ImageFont.FreeTypeFont, anchor: str, align: str, outline: int = 1):
    x, y = xy
    draw.text((x+outline, y), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x-outline, y), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x, y+outline), text, fill=secondary, font=font, anchor=anchor, align=align)
    draw.text((x, y-outline), text, fill=secondary, font=font, anchor=anchor, align=align)

    draw.text(xy, text, fill=main, font=font, anchor=anchor, align=align)


def find_max_font_size(draw: ImageDraw.ImageDraw, text: str, font_path: str, box_width: float, box_height: float, min_size: int = 10, max_size: int = 200):
    best = min_size
    i = 0
    while min_size < max_size:
        mid = (min_size + max_size) // 2
        font = ImageFont.truetype(font_path, mid)

        _, _, w, _ = draw.multiline_textbbox((0, 0), text, font)
        wrapped = split_line_by_words(text, int(w), int(box_width))
        _, _, w, h = draw.multiline_textbbox((0, 0), wrapped, font)

        if w <= box_width and h <= box_height:
            best = mid
            min_size = mid + 1
        else:
            max_size = mid - 1
        i += 1

    logging.info(f"Computed font size {best} in {i} iterations.")
    return best


def draw_top_and_bottom_text(img: ImageFile.ImageFile, toptext: str, bottomtext: str):
    draw = ImageDraw.Draw(img)

    longest = toptext if len(toptext) > len(bottomtext) else bottomtext

    BOX_OFFSET = 0.08
    x_offset = img.width * BOX_OFFSET
    y_offset = img.height * BOX_OFFSET
    box_height = img.height / 6 + y_offset
    box_width = img.width - 2 * x_offset

    font_file = '/usr/share/fonts/noto/NotoSans-Bold.ttf'
    font_size = find_max_font_size(draw, longest, font_file, box_width, box_height)

    font = ImageFont.truetype(font_file, font_size)
    toptext = split_line_by_words(toptext, int(font.getlength(toptext)), int(box_width))
    bottomtext = split_line_by_words(bottomtext, int(font.getlength(bottomtext)), int(box_width))

    text_x = img.width / 2
    toptext_y = y_offset
    bottomtext_y = img.height - y_offset

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

