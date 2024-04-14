from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import MessageEntityType

from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.database import DataBase
from modules.logger import Logger
from modules.database import ClientRow
import config as conf
from config import messages_dict, config
from keyboards import sign
from handlers.start import InputStates

local_log = Logger('input_validator', f'{conf.PATH}/log/input_validator.log', level=conf.LOG_LEVEL)

router = Router()

# email введен корректно
@router.message(InputStates.inputing_email, F.entities[...].type == MessageEntityType.EMAIL)
async def valid_email(message: Message, state: FSMContext):
    email: str
    # извлечение email
    for item in message.entities: # type: ignore
        if item.type == MessageEntityType.EMAIL:
            email = item.extract_from(message.text) # type: ignore
            await state.update_data(user_email=email)
            break
    # попытка отправки кода на введенный email
    try:
        pass
    except:
        pass
    else:
        await state.set_state(InputStates.inputing_code) # type: ignore
        await message.answer(messages_dict['code_send']) # type: ignore
        await message.answer(messages_dict['code_request'])  # type: ignore
    
# email введен неверно
@router.message(InputStates.inputing_email)
async def invalid_email(message: Message):
    await message.answer(messages_dict['invalid_email'])    # type: ignore

async def in_pin(message: Message, state: FSMContext):
    pass