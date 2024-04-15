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

local_log = Logger('register', f'{conf.PATH}/log/register.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()
# данная часть программы обрабатывает события лишь в том случае
# если пользователь НЕ авторизован и НЕ зарегистрирован
router.message.filter(MagicData(F.client.authorized.is_(False)), MagicData(F.client.reg_date.is_(None)))

# обработка кнопки "авторизация" (пользователь не зарегистрирован)
@router.message(F.text.lower() == buttons_dict['auth'].lower())
async def try_login(message: Message, client: ClientRow):
    local_log.info(f'Unregistered user try to log in\n{client}')
    main_log.info(f'Attempt unregistered client to log in\n{client}')
    await message.reply(messages_dict['reg_offer'], # type: ignore
                            reply_markup=sign.register_kb()
                            ) 
    
# обработка кнопки "регистрация"
@router.message(F.text.lower().in_([buttons_dict['reg'].lower(), buttons_dict['input_email'].lower()]))
async def sign_up(message: Message, client: ClientRow, state: FSMContext):
    main_log.info(f'Client registration\n{client}')
    await message.reply('Введите email')
    await state.set_state(InputStates.inputing_email)
    