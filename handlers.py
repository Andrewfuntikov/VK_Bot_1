"""
Handler - функция, которая принимает нна вход text (текст входящего сообщения) и context (dict), а возвращает bool:
True если шаг пройден, False если данные введены не правильно.
"""
import re

re_name = re.compile(r'^[\w\-\s]{3, 30}$')
re_email = re.compile(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b")


def handle_name(text, context):
    match = re.match(re_name, text)
    if match:
        context['name'] = text
        return True
    else:
        return False


def handle_email(text, context):
    matches = re.findall(re_email, text)
    if len(matches) > 0:
        context['email'] = matches[0]
        return True
    else:
        return False
