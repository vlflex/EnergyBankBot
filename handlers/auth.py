from aiogram import Router, F
from aiogram.filters import MagicData
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.database import DataBase
from modules.logger import Logger
from modules.database import ClientRow
import config as conf
from config import messages_dict, config, buttons_dict
from keyboards import sign
from handlers.start import InputStates

local_log = Logger('auth', f'{conf.PATH}/log/auth.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()
# данная часть программы обрабатывает события лишь в том случае
# если пользователь НЕ авторизован и зарегистрирован
router.message.filter(MagicData(F.client.authorized.is_(False)), MagicData(F.client.reg_date))

# обработка кнопки "регистрация" (пользователь уже зарегистрирован)
@router.message(F.text.lower() ==buttons_dict['reg'].lower())
async def try_sign_up(message: Message, client: ClientRow):
    local_log.info(f'Registered user try to sign up\n{client}')
    main_log.info(f'Attempt unregistered client to sign up\n{client}')
    await message.reply(messages_dict['auth_offer'], reply_markup=sign.auth_kb()) # type: ignore
    
# обработка кнопки "авторизация"
@router.message(F.text.lower() ==buttons_dict['auth'].lower())
async def login(message: Message, client: ClientRow, state: FSMContext):
    main_log.info(f'Client login\n{client}')
    await message.reply('Введите пин-код')
    await state.set_state(InputStates.inputing_pin)