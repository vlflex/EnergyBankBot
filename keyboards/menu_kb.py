from aiogram.types import KeyboardButtonRequestUser
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import buttons_dict, currencies_dict
from keyboards.sign import reply_kb_builder
from aiogram.filters.callback_data import CallbackData

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

# выбор пользователя для оплаты
def choose_pay_target_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(
        text = buttons_dict['pay_target'],
        request_user=KeyboardButtonRequestUser(
            request_id = 1,
            user_is_bot = False,
        )
    )
    markup = builder.as_markup()
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    return markup

# клавиатура выбора валюты 
def choose_currency_kb():
    return reply_kb_builder(
        buttons=[
        currencies_dict['USD'], currencies_dict['EUR'], currencies_dict['CNY'], currencies_dict['INR'],
        currencies_dict['UAH'], currencies_dict['BYN'], currencies_dict['KZT'], currencies_dict['UZS'],
        currencies_dict['JPY'], currencies_dict['GBP'], currencies_dict['AED'], currencies_dict['TRY'],
        buttons_dict['menu'], buttons_dict['curency_other'],
        ],
        button_in_row=[4, 4, 4, 2])
    
# формат данных для работы слайдера
class SliderCallback(CallbackData, prefix="slider"):
    action: str
    client_id: int

def history_slider_kb(id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text='⬅', callback_data=SliderCallback(action='left', client_id = id))
    builder.button(text='➡', callback_data=SliderCallback(action='right', client_id = id))
    markup = builder.as_markup()
    return markup

# меню настроек
def settings_menu_kb(notifications: bool):
    return reply_kb_builder(
        [
            buttons_dict['sets_pincode'],
            buttons_dict['sets_nots_on'] if notifications else buttons_dict['sets_nots_off'],
            buttons_dict['sets_exit'],
            buttons_dict['menu'],
        ],
    )
# кнопка выйти и меню
def menu_exit_kb():
    return reply_kb_builder(
        [
            buttons_dict['sets_exit'],
            buttons_dict['menu'],
        ],
    )
    
# выбор типа счета для рассчета
def credit_deposite_kb():
    return reply_kb_builder(
        [
            buttons_dict['calc_credit'],
            buttons_dict['calc_deposite'],
        ],
    )
    
# кнопки для рассчета кредита
def months_amount_kb():
    return reply_kb_builder(
        [
            buttons_dict['calc_months'],
            buttons_dict['calc_fill'],
        ],
    )