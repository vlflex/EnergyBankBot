from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from datetime import datetime
from sys import path
import config as conf
from modules.logger import Logger
from modules.database import ClientRow
import re
from typing import Union, Any, Dict 

local_log = Logger('casino_filter', f'{conf.PATH}/log/casino_filter.log', level=conf.LOG_LEVEL)

# проверка: сделана ли ставка
class HaveBetFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        user_data = await state.get_data()
        bet = user_data.get('bet', False)
        return bool(bet)

# проверка: достаточно ли средств у клиента
@local_log.wrapper()
class EnoughMoneyFilter(BaseFilter):
    async def __call__(self, message: Message, client: ClientRow) -> bool:    # type: ignore
        bet: int
        try:
            bet = int(message.text) # type: ignore
        except Exception:
            return False
        else:
            return bet >= client.balance
        
# проверка: введено ли число для броска кости
class HaveDiceNumFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        user_data = await state.get_data()
        bet = user_data.get('dice_num', False)
        return bool(bet)
        
# проверка ввод значения dice
@local_log.wrapper()
class  CorrectDiceChoice(BaseFilter):
    async def __call__(self, message: Message):
        dice_choice: int
        try:
            dice_choice = int(message.text) # type: ignore
        except Exception:
            if message.text.strip().lower() == 'чет' or  message.text.strip().lower() == 'нечет':   # type: ignore
                return True
            else:
                return False
        else:
            return 1 <= dice_choice <= 6
            