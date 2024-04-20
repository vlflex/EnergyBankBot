from aiogram import Router, F
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.logger import Logger
from modules.database import ClientRow, DataBase
import config as conf
from config import messages_dict, config, buttons_dict
from keyboards import menu_kb as mkb, sign
from handlers.start import cmd_start, InputStates

local_log = Logger('menu', f'{conf.PATH}/log/menu.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()
router.message.filter(MagicData(F.client.authorized.is_(True)))

# отображение баланса
@router.message(Command('balance'))
@router.message(F.text.lower() == buttons_dict['balance'].lower())
async def balance_info(message: Message, client: ClientRow):
    main_log.info(f'Client ask balance\n{client}')
    await message.answer(messages_dict['menu_balance'].substitute(balance="{:,}".format(client.balance)), # type: ignore
                        parse_mode=ParseMode.HTML,
                        reply_markup=mkb.to_menu_kb()
                        )
    
# обработка кнопки возвращения в меню
@router.message(F.text.lower() == buttons_dict['menu'].lower())
async def go_to_menu(message: Message, client: ClientRow, state: FSMContext):
    local_log.info(f'Open menu\n{client}')
    await cmd_start(message, client, state)
    