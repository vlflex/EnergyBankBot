from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, MagicData
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.enums import ParseMode

from re import compile
from typing import Dict
from random import choice
from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.database import DataBase, ClientRow
from modules.logger import Logger
import config as conf
from config import messages_dict, config, buttons_dict, photos_dict, stickers_dict
from keyboards import casino_kb as ckb
from filters.casino_filter import SetBetFilter, EnoughMoneyFilter
from filters.validation import MatchPatternFilter

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
# сделать ставку
@router.message(F.text.lower() == buttons_dict['casino_bet'].lower(), CasinoStates.inputing_bet)
@router.message(F.text.lower() == buttons_dict['casino_bet'].lower(), CasinoStates.base_state)
async def input_bet(message: Message, state: FSMContext, client: ClientRow):
    local_log.info(f'Player start input bet\n{client}')
    await message.reply(messages_dict['casino_input_bet'])  # type: ignore
    await state.set_state(CasinoStates.inputing_bet)
    
# ввод ставки (удачно) и проверка суммы
@router.message(CasinoStates.inputing_bet, MatchPatternFilter(compile(r'^[0-9]+$')))
async def check_bet_input(message: Message, state: FSMContext, client: ClientRow):
    bet = int(message.text) # type: ignore
    # баланс больше ставки
    if client.balance >= bet:
        await state.update_data(bet=bet)
        with DataBase(config.db_name.get_secret_value()) as db:
            db.update(
                    id = client.id,
                    balance=client.balance - bet
                    )
        local_log.info(f'Player successfully set a bet {bet}\n{client}')
        await message.reply(messages_dict['casino_bet_accepted'], # type: ignore
                            reply_markup=ckb.try_spin_throw_bet())  
        await state.set_state(CasinoStates.base_state)
    # недостаточно средств
    else:
        local_log.info(f'Players setting bet fail {bet}\n{client}')
        await message.reply(messages_dict['casino_noenough'].substitute(balance = client.balance, bet=bet),    # type: ignore
                            reply_markup=ckb.set_bet_kb(),
                            parse_mode=ParseMode.HTML,
                            ) 
        await message.answer_sticker(sticker=choice(tuple(stickers_dict.values())))
        
# ввод ставки (неудача)
@router.message(CasinoStates.inputing_bet)
async def invalid_bet_input(message: Message, state: FSMContext, client: ClientRow):
    await message.reply(messages_dict['casino_invalid_bet'])    # type: ignore
    
# попытка играть без ставки
@router.message(F.text.lower().in_([buttons_dict['casino_dice'].lower(), buttons_dict['casino_slot'].lower()]), CasinoStates.base_state)
async def no_bet(message: Message, client: ClientRow):
    await message.reply(messages_dict['casino_no_bet'], reply_markup=ckb.set_bet_kb()) # type: ignore
    
