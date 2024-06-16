from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = 'files/img.png'
FONT_PATH = 'files/Roboto-Regular.ttf'
FONT_SIZE = 20
BLACK = (0, 0, 0, 225)
NAME_OF_SET = (205, 212)
EMAIL_OF_SET = (205, 237)
AVATAR_OF_SET = (100, 100)
AVATAR_SIZE = (80, 55)  # Новые размеры аватара
AVATAR_POSITION_2 = (155, 210)  # Новые координаты для второго аватара


def generate_ticket(name, email):
    base = Image.open(TEMPLATE_PATH).convert('RGBA')
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    draw = ImageDraw.Draw(base)
    draw.text(NAME_OF_SET, name, font=font, fill=BLACK)
    draw.text(EMAIL_OF_SET, email, font=font, fill=BLACK)
    response = requests.get(url='https://www.kino-teatr.ru/acter/photo/7/1/48117/263615.jpg')
    avatar_file_like = BytesIO(response.content)
    avatar = Image.open(avatar_file_like)
    avatar.thumbnail(AVATAR_SIZE)
    base.paste(avatar, AVATAR_POSITION_2)
    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file
