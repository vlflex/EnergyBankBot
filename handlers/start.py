from aiogram import Router, F
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.logger import Logger
from modules.database import ClientRow
import config as conf
from config import messages_dict, config
from keyboards import menu_kb, sign

local_log = Logger('start', f'{conf.PATH}/log/start.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()

# группа состояний
class InputStates(StatesGroup):
    inputing_pin = State()
    inputing_email = State()
    inputing_code = State()
    sending_code = State()
    waiting_send_code = State()
    waiting_input_pin = State()

# обработка /start для авторизованных пользователей
@router.message(Command('start'), MagicData(F.client.authorized.is_(True)))
async def cmd_start(message: Message, client: ClientRow, state: FSMContext):
    await state.clear()
    main_log.info(f'Greet with\n{client}')
    await message.answer(messages_dict['greet'].substitute(name = message.from_user.full_name), # type: ignore
                        reply_markup= menu_kb.main_menu_kb()
                        ) 

# обработка /start для НЕавторизованных пользователей
@router.message(Command('start'), MagicData(F.client.authorized.is_(False)))
async def cmd_start_unauth(message: Message, client: ClientRow, state: FSMContext):
    await state.clear()
    main_log.info(f'Greet with unauthorized client\n{client}')
    await message.answer(messages_dict['unauth_greet'].substitute(name = message.from_user.full_name), # type: ignore
                        reply_markup=sign.register_auth_kb())

