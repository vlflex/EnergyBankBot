from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

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

@router.message(InputStates.inputing_email)
async def in_email(message: Message, state: FSMContext):
    pass
    
@router.message(InputStates.inputing_pin)
async def in_pin(message: Message, state: FSMContext):
    pass