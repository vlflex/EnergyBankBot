from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import MessageEntityType

from random import randint
from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.database import DataBase
from modules.logger import Logger
from modules.database import ClientRow
from modules.email_sender import EmailSender
import config as conf
from config import messages_dict, config, create_email_form
from keyboards import sign
from handlers.start import InputStates

local_log = Logger('input_validator', f'{conf.PATH}/log/input_validator.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()

# email введен корректно
@router.message(F.entities[...].type == MessageEntityType.EMAIL, InputStates.inputing_email)
async def valid_email(message: Message, state: FSMContext, client: ClientRow):
    user_email: str 
    # извлечение email
    for item in message.entities: # type: ignore
        if item.type == MessageEntityType.EMAIL:
            user_email = item.extract_from(message.text) # type: ignore
            await state.update_data(email = user_email)
            break
    main_log.info(f'Correct email input{user_email}by\n{client}')   # type: ignore
    await message.reply(messages_dict['email_accepted'], reply_markup=sign.send_kb())  # type: ignore
    await state.set_state(InputStates.sending_code)
    
# email введен неверно
@router.message(InputStates.inputing_email)
async def invalid_email(message: Message, client: ClientRow):
    local_log.info(f'Invalid email unput:\n"{message.text}"\nby {client}')   # type: ignore
    await message.reply(messages_dict['invalid_email'])    # type: ignore
    
# отправка кода
@router.message(F.text.lower() == 'отправить код', InputStates.sending_code)
async def code_sender(message: Message, state: FSMContext, client: ClientRow):
    # попытка отправки кода на введенный email
    user_data = await state.get_data()
    personal_code = randint(100_000, 999_999)
    await state.update_data(code = personal_code)
    # генерация содержимого email
    email_to_user = create_email_form(
        email=user_data['email'],
        code=personal_code,
        # reg_date == None => это регистрация
        registration=not(bool(client.reg_date))
    )
    email_success: bool
    with EmailSender() as es:
        email_success = es.send(**email_to_user)
    # код успешно отправлен
    if email_success:
        await message.reply(messages_dict['code_send']) # type: ignore
        await message.answer(messages_dict['code_request'])  # type: ignore
        await state.set_state(InputStates.inputing_code) # type: ignore
    # ошибка отправки
    else:
        await message.reply(messages_dict['code_error'], reply_markup=sign.send_email_input_kb()) # type: ignore

async def in_pin(message: Message, state: FSMContext):
    pass