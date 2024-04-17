from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from typing import Sequence, List
from config import buttons_dict

# конструктор клавиатуры
def reply_kb_builder(buttons: Sequence[str], button_in_row: int | List[int] = 2, one_time: bool = True) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for btn in buttons:
        builder.button(text = btn)
    if isinstance(button_in_row, list):
        builder.adjust(*button_in_row)
    else:
        builder.adjust(button_in_row)
    markup = builder.as_markup()
    markup.resize_keyboard = True
    markup.one_time_keyboard = one_time
    return markup

def register_auth_kb():
    return reply_kb_builder([buttons_dict['reg'], buttons_dict['auth']])

def register_kb():
    return reply_kb_builder([buttons_dict['reg']])

def auth_kb():
    return reply_kb_builder([buttons_dict['auth']])

def send_kb():
    return reply_kb_builder([buttons_dict['send_code']])

def send_email_input_kb():
    return reply_kb_builder([buttons_dict['input_email'], buttons_dict['send_code']])

def email_restore_input_pin():
    return reply_kb_builder([buttons_dict['input_pin'], buttons_dict['email_restore']], button_in_row=1)