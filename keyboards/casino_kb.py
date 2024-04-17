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

# бросить кость, выбрать ставку, выбрать число
def try_throw_bet_num():
    return reply_kb_builder([buttons_dict['casino_dice'], buttons_dict['casino_bet'], buttons_dict['casino_dice_choice']], button_in_row=[1, 2])
    
# выбрать dice / чет или нечет
def choose_dice():
    numbers = list(range(1,7))
    all_btns = [str(num) for num in numbers]
    all_btns.extend(['Чет', 'Нечет'])
    return reply_kb_builder(all_btns, button_in_row=[3, 3, 2]) # type: ignore


