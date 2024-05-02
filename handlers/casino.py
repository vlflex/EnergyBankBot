from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, MagicData
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.enums import ParseMode

from datetime import datetime
from re import compile
from typing import Dict
from random import choice
from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.database import DataBase, ClientRow
from modules.logger import Logger
import config as conf
from config import messages_dict, config, buttons_dict, photos_dict, stickers_dict, try_photos
from keyboards import casino_kb as ckb
from filters.casino_filter import HaveBetFilter, EnoughMoneyFilter, HaveDiceNumFilter, CorrectDiceChoice
from filters.validation import MatchPatternFilter

local_log = Logger('casino', f'{conf.PATH}/log/casino.log', level=conf.LOG_LEVEL)

router = Router()
# лишь для авторизованных
router.message.filter(MagicData(F.client.authorized.is_(True)))
# коэффициент для dice (одно число)
DICE_ONE_COEF = 10
# коэффициент для dice (чет/нечет)
DICE_DIV_COEF = 2
# коэффицента для слотов
SLOT_COEF = 100
# коэффициент для slots
class CasinoStates(StatesGroup):
    base_state = State()
    inputing_bet = State()
    inputing_dice_num = State()
    
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
                        reply_markup= ckb.try_spin_throw_bet()) 
    await message.answer_photo(photo=choice(tuple(photos_dict.values()))) # type: ignore
    await state.set_state(CasinoStates.base_state)
    
# бросить кость
@router.message(F.text.lower() == buttons_dict['casino_dice'].lower(), CasinoStates.base_state, HaveBetFilter(), HaveDiceNumFilter())
async def play_dice(message: Message, state: FSMContext, client: ClientRow):
    dice_msg = await message.answer_dice(DiceEmoji.DICE, reply_markup=ckb.try_throw_bet_num())
    
    dice_score = dice_msg.dice.value    # type: ignore
    player_data = await state.get_data()
    player_bet = player_data['bet']
    dice_choice = player_data['dice_num']
    # запрет, если ставка больше баланса
    if player_bet > client.balance:
        await message.answer(messages_dict['casino_bet_more_balance'].substitute(bet="{:,}".format(player_bet)),  # type: ignore
                            reply_markup=ckb.set_bet_kb(),
                            )  
        await message.answer_sticker(sticker=choice(tuple(stickers_dict.values())))
        return
    # проверка значений
    # выбрано чет/нечет
    if isinstance(dice_choice, str):
        # определение остатка в соответсвии с выбором
        dice_rem = 0  if dice_choice.lower() == 'чет' else 1
        if dice_score % 2 == dice_rem:
            await win(message, state, client, dice = True)
        else:
            await lose(message, state, client, dice = True)
    # выпало выбранное число
    elif dice_score == dice_choice:
        await win(message, state, client, dice = True)
    else:
        await lose(message, state, client, dice = True)

# выбор числа для броска кости
@router.message(F.text.lower().lower() == buttons_dict['casino_dice_choice'].lower(), CasinoStates.base_state, HaveBetFilter(), HaveDiceNumFilter())
@router.message(F.text.lower().lower() == buttons_dict['casino_dice'].lower(), CasinoStates.base_state, HaveBetFilter())
async def start_input_dice(message: Message, state: FSMContext, client: ClientRow):
    player_data = await state.get_data()
    local_log.info(f'Input dice num\n{client}\n{player_data["bet"]}')
    await message.answer(
                        messages_dict['casino_dice_input'].substitute(num=DICE_DIV_COEF, even = DICE_ONE_COEF), # type: ignore
                        reply_markup=ckb.choose_dice(),  
                        parse_mode=ParseMode.HTML,
                        )    
    await state.set_state(CasinoStates.inputing_dice_num)
    
# ввод числа для кости (удачно)
@router.message(CasinoStates.inputing_dice_num, CorrectDiceChoice())   # type: ignore
async def success_dice_input(message: Message, state: FSMContext, client: ClientRow):
    local_log.info(f'Dice choice accepted: {message.text}\n{client}')
    await message.reply(messages_dict['casino_choice_accepted'], reply_markup=ckb.try_throw_bet_num())    # type: ignore
    # сохранение выбора
    # число
    try:
        await state.update_data(dice_num=int(message.text)) # type: ignore
    # чет/нечет
    except Exception:
        await state.update_data(dice_num=message.text) # type: ignore
        
    await state.set_state(CasinoStates.base_state)

# ввод числа для кости (неудачно)
@router.message(CasinoStates.inputing_dice_num)
async def fail_dice_input(message: Message, state: FSMContext, client: ClientRow):
    local_log.info(f'Dice invalid number: {message.text}\n{client}')
    await message.reply(messages_dict['casino_dice_fail_input'], reply_markup=ckb.choose_dice())    # type: ignore
    
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
    # нулевая ставка
    if bet == 0:
        await message.answer(messages_dict['casino_bet_zero'],  # type: ignore
                            reply_markup=ckb.set_bet_kb(),
                            )  
    # баланс больше ставки
    elif client.balance >= bet:
        await state.update_data(bet=bet)
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
    local_log.info(f'Invalid bet input: {message.text}\n{client}')
    await message.reply(messages_dict['casino_invalid_bet'])    # type: ignore
    
# попытка играть без ставки
@router.message(F.text.lower().in_([buttons_dict['casino_dice'].lower(), buttons_dict['casino_slot'].lower()]), CasinoStates.base_state)
async def no_bet(message: Message, client: ClientRow):
    await message.reply(messages_dict['casino_no_bet'], reply_markup=ckb.set_bet_kb()) # type: ignore
    
# выигрыш
async def win(message: Message, state: FSMContext, client: ClientRow, dice: bool):
    user_data = await state.get_data()
    bet = user_data['bet']
    win_amount: float
    trans_msg = messages_dict['pay_casino_dice_win'] if dice else messages_dict['pay_casino_slot_win']
    if dice:
        dice_choice = user_data['dice_num']
        win_amount = bet * DICE_ONE_COEF if isinstance(dice_choice, int) else bet * DICE_DIV_COEF
        await message.answer_photo(photo=try_photos['stonks'])
        await message.answer(messages_dict['casino_win'].substitute(win=win_amount, bet = bet)) # type: ignore
    else:
        win_amount = bet * SLOT_COEF
        for _ in range(3):
            await message.answer_photo(photo=try_photos['ultra_stonks'])
        await message.answer(messages_dict['casino_win'].substitute(win=win_amount, bet = bet)) # type: ignore
    # обновление баланса
    with DataBase(config.db_name.get_secret_value()) as db:
        db.update(
            id = client.id,
            balance=client.balance+win_amount   # type: ignore
        )
        db.add_trans(
            type_id=db.ACCRUAL_ID,
            client_id=client.id,
            source_id=db.CASINO_ID,
            amount=win_amount,  # type: ignore
            date=datetime.now(),
            desc=trans_msg, # type: ignore
        )
    local_log.info(f'Player won (dice={dice}) {win_amount} with state {bet}\n{client}')

# проигрыш
async def lose(message: Message, state: FSMContext, client: ClientRow, dice: bool):
    user_data = await state.get_data()
    bet = user_data['bet']
    trans_msg = messages_dict['pay_casino_dice_lose'] if dice else messages_dict['pay_casino_slot_lose']
    await message.answer_photo(photo=try_photos['not_stonks'])
    await message.answer(messages_dict['casino_lose'].substitute(bet = bet)) # type: ignore
    # обновление баланса
    with DataBase(config.db_name.get_secret_value()) as db:
        db.update(
            id = client.id,
            balance= 0 if bet == client.balance else client.balance-bet
        )
        db.add_trans(
            type_id=db.DEBIT_ID,
            client_id=client.id,
            source_id=db.CASINO_ID,
            amount=-bet,  # type: ignore
            date=datetime.now(),
            desc=trans_msg, # type: ignore
        )
    local_log.info(f'Player lose {bet}\n{client}')