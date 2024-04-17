from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from typing import Sequence, List
from config import buttons_dict
from keyboards.sign import reply_kb_builder

# клавиатура для главного меню
def main_menu_kb():
    return reply_kb_builder([
        buttons_dict['pay'],
        buttons_dict['balance'],
        buttons_dict['history'],
        buttons_dict['calculator'],
        buttons_dict['settings'],
        buttons_dict['currency'],
    ],
        button_in_row=3,               
    )
    
# переход в меню
def to_menu_kb():
    return reply_kb_builder([buttons_dict['menu']])