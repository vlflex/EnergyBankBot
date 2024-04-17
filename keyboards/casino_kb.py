from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from typing import Sequence
from config import buttons_dict
from keyboards.sign import reply_kb_builder

# кнопка для прокрутки автомата
def try_spin_throw_bet():
    return reply_kb_builder([buttons_dict['casino_slot'], buttons_dict['casino_dice'], buttons_dict['casino_bet']])

# сделать ставку
def set_bet_kb():
    return reply_kb_builder([buttons_dict['casino_bet']])
