from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from typing import Sequence

# конструктор клавиатуры
def __reply_kb_builder(buttons: Sequence[str], button_in_row: int = 2, one_time: bool = True) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for btn in buttons:
        builder.button(text = btn)
    builder.adjust(button_in_row)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    markup.one_time_keyboard = one_time
    return markup

def register_auth_kb():
    return __reply_kb_builder(['Регистрация', 'Авторизация'])

def register_kb():
    return __reply_kb_builder(['Регистрация'])

def auth_kb():
    return __reply_kb_builder(['Авторизация'])