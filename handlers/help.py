from aiogram import Router, F
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from fuzzywuzzy import process
from typing import Dict
from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.logger import Logger
from modules.database import ClientRow
import config as conf
from config import messages_dict, buttons_dict, questions_dict
from handlers.start import InputStates

local_log = Logger('help', f'{conf.PATH}/log/help.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()
router.message.filter(MagicData(F.client.authorized.is_(True)))

# функция сравнивает запрос и находит наиболее подходящую строку (ответ)
@local_log.wrapper()
def find_relevant_question(data_dict: Dict[str ,str], query: str):
    best_match = process.extractOne(query, data_dict.keys())
    return data_dict[best_match[0]]    # type: ignore

# обработка команды 
@router.message(Command('help'))
@router.message(F.text.lower() == buttons_dict['help'].lower())
async def cmd_help(message: Message, state: FSMContext, client: ClientRow):
    await message.answer(messages_dict['help'])   # type: ignore
    await state.set_state(InputStates.inputing_help_query)
    main_log.info(f'Client ask help\n{client}')

# отправка ответа
@router.message(InputStates.inputing_help_query)
async def success_query(message: Message, state: FSMContext, client: ClientRow):
    answer = find_relevant_question(data_dict=questions_dict, query = message.text) # type: ignore
    await message.reply(answer)    
    local_log.info(f'Client got question answer:\n{answer}\n{client}')