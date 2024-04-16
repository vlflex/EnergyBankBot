from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, MagicData
from aiogram.enums.dice_emoji import DiceEmoji

from typing import Dict
from random import choice
from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.database import DataBase, ClientRow
from modules.logger import Logger
import config as conf
from config import messages_dict, config, buttons_dict, photos_dict, stickers_dict
from keyboards import casino_kb as ckb

local_log = Logger('casino', f'{conf.PATH}/log/casino.log', level=conf.LOG_LEVEL)

router = Router()
# лишь для авторизованных
router.message.filter(MagicData(F.client.authorized.is_(True)))

class CasinoStates(StatesGroup):
    base_state = State()
    inputing_bet = State()
    
# у пользователя 0 на счету
@router.message(Command('casino'), MagicData(F.client.balance.__le__(0)))
async def no_money(message: Message, client: ClientRow):
    local_log.info(f'Client is bancrupt\n{client}')
    await message.answer(messages_dict['casino_nomoney'])   # type: ignore
    await message.answer_video(video='BAACAgIAAxkBAAIDrmYfAxXStXK7qBlT-jMMzlswIvaiAAKDTAACN6f4SO_ahTUpAAGuhTQE')
    await message.answer_sticker(sticker=choice(tuple(stickers_dict.values())))
# вход в казино
@router.message(Command('casino'))
async def cmd_casion(message: Message, state: FSMContext, client: ClientRow):
    local_log.info(f'Enter to the casino\n{client}')
    await message.answer(messages_dict['casino_greet'], # type: ignore
                        reply_markup= ckb.try_spin_throw()) 
    await message.answer_photo(photo=choice(tuple(photos_dict.values()))) # type: ignore
    await state.set_state(CasinoStates.base_state)
