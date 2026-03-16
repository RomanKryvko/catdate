from datetime import datetime
import math

def get_ordinal_indicator(n: int) -> str:
    if n == 1:
        return 'st'
    elif n == 2:
        return 'nd'
    elif n == 3:
        return 'rd'
    return 'th'


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

def get_date_string(dt: datetime) -> str:
    return f"{months[dt.month-1]} {dt.day}{get_ordinal_indicator(dt.day)}"


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
