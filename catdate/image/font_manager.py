import os
import subprocess
from functools import lru_cache
from PIL import ImageFont

def get_font_file(family: str, style: str) -> str | None:
    try:
        result = subprocess.run(
        ["fc-match", "-f", "%{file}", f"{family}:style={style}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
        return result.stdout.strip()
    except Exception:
        return None


def get_from_assets(family: str, style: str, dir: str='assets/fonts') -> str | None:
    font_name = f"{family}-{style}".lower()

    for root, _, files in os.walk(dir):
        for file in files:
            if font_name in file.lower():
                return os.path.join(root, file)
    return None


@lru_cache(128)
def get_font(family: str, style: str, size: float) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    fontfile = get_font_file(family, style)
    if fontfile is None:
        fontfile = get_from_assets(family, style)
        if fontfile is None:
            return ImageFont.load_default(size)

    return ImageFont.truetype(fontfile, size)

