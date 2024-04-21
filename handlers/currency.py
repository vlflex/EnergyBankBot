from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

import pandas
from typing import Dict
from currency_converter import CurrencyConverter
from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.logger import Logger
from modules.database import ClientRow
import config as conf
from config import messages_dict, buttons_dict, currencies_dict, config, CURRENCY_QUERY_URL, RUB, MAX_NOMINAL
from keyboards import menu_kb as mkb

local_log = Logger('currency', f'{conf.PATH}/log/currency.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()

# обработка кнопки меню/команды, выбор валюты
@router.message(Command('currency'))
@router.message(F.text.lower() == buttons_dict['currency'].lower())
async def choose_currency(message: Message, client: ClientRow):
    local_log.info(f'Client ask for curency\n{client}')
    await message.answer(messages_dict['currency_choose'],  # type: ignore
                        reply_markup=mkb.choose_currency_kb(),
                        )
    
# обработка валют из словаря
@router.message(F.text.upper().in_(currencies_dict.values()))
async def handle_currency_button(message: Message, client: ClientRow):
    currency_btn = message.text.strip().upper() # type: ignore
    currency = currency_btn[:3] 
    # попытка получения информации 
    try:
        currency_info = currency_get_info(currency_code=currency, currency_icon=currency_btn)
    except Exception as error:
        local_log.exception(f'Fail get info about currency "{currency}":\n{client}\n{error}')
        await message.answer(messages_dict['currency_error'],   # type: ignore
                            reply_markup=mkb.choose_currency_kb(),
                            )
    else:
        await message.answer(
                messages_dict['currency_result'].substitute(**currency_info),   # type: ignore
                parse_mode=ParseMode.HTML,
                reply_markup=mkb.choose_currency_kb(),
        )
        main_log.info(f'Client successfully got info about currency "{currency}":\n{client}')

# функция для получения информации о валюте
def currency_get_info(currency_code: str, currency_icon: str) -> Dict[str, str]:
    xml_res = pandas.read_xml(CURRENCY_QUERY_URL, encoding='cp1251')
    local_log.debug(f'Currency query result\n{xml_res}')
    currency_data = xml_res[xml_res['CharCode'] == currency_code]
    name = f'"{currency_data["Name"].iloc[0]}"'
    nominal = int(currency_data['Nominal'].iloc[0])
    value = float(currency_data['Value'].iloc[0].replace(',', '.'))/nominal if nominal <= MAX_NOMINAL else float(currency_data['Value'].iloc[0].replace(',', '.'))
    return {
        'other_name':name,
        'other_nominal':'' if nominal <= MAX_NOMINAL else f'{nominal:,}',
        'other_currency':currency_icon,
        'our_nominal':f'{value:,.2f}' if value >= 1 else f'{value:,.3f}',
        'our_currency':RUB,
    }