from aiogram import Router, F
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.logger import Logger
from modules.database import ClientRow
from modules.account import DepositAccount, CreditAccount
import config as conf
from config import messages_dict, config, buttons_dict
from keyboards import menu_kb as mkb
from handlers.start import cmd_start, InputStates

local_log = Logger('calculator', f'{conf.PATH}/log/calculator.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()
router.message.filter(MagicData(F.client.authorized.is_(True)))

@router.message(Command('calculator'))
@router.message(F.text.lower() == buttons_dict['calculator'].lower())   # type: ignore
async def choose_account_type(message: Message, client: ClientRow):
    await message.answer(
                messages_dict['calc_choose'],   # type: ignore
                reply_markup=mkb.credit_deposite_kb(),
                ) 
    main_log.info(f'Client use calculator\n{client}')
    
# обработка кнопок выбора счета
@router.message(F.text.lower() == buttons_dict['calc_credit'].lower())
@router.message(F.text.lower() == buttons_dict['calc_deposite'].lower())
async def account_input(message: Message, state: FSMContext, client: ClientRow):
    await state.update_data(account=message.text)
    await message.answer(messages_dict['calc_input_sum'])   # type: ignore
    local_log.info(f'Start input account\n{client}')
    await state.set_state(InputStates.inputing_calc_sum)
    
# выбор искомых данных
@router.message(InputStates.choosing_data)
async def choose_data(message: Message, state: FSMContext, client: ClientRow):
    await message.answer(messages_dict['calc_choose_data'],# type: ignore
                        reply_markup=mkb.months_amount_kb(),
                        parse_mode=ParseMode.HTML,
                        )  
    local_log.info(f'Choose data\n{client}')
