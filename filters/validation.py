from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from decimal import Decimal
from datetime import datetime
from sys import path
import config as conf
from modules.logger import Logger
from modules.database import ClientRow
import re
from typing import Union, Any, Dict 

local_log = Logger('input_validator', f'{conf.PATH}/log/input_validator.log', level=conf.LOG_LEVEL)

# фильтр для проверки соответствия строке шаблону
class MatchPatternFilter(BaseFilter):
    def __init__(self, pattern: re.Pattern):  
        self.__pattern = pattern
    
    async def __call__(self, message: Message):
        local_log.debug(f'MatchPatternFilter\tmessage: {self.__pattern}\tpattern:{message.text}')
        return bool(re.match(self.__pattern, message.text)) # type: ignore

# фильтр для проверки кода
class MatchCodeFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        user_data = await state.get_data()
        user_code: int | None = user_data.get('code', None)
        local_log.debug(f'MatchCodeFilter\tmessage: {message.text.strip()}\tcode: {user_code}') # type: ignore
        return message.text.strip() == str(user_code) if user_code else False # type: ignore

# фильтр для проверки завершения таймера
class TimerFilter(BaseFilter):
    def __init__(self, dur: int):
        self.__duration = dur
    
    async def __call__(self, message: Message, state: FSMContext) -> Union[bool, Dict[str, Any]]:
        user_data = await state.get_data()
        user_time: datetime | None = user_data.get('start_timer', None)
        if not user_time:
            local_log.warning(f'Can not find "start_timer" value\nUser data: {user_data}')
            return False
        else:
            diff_sec = (datetime.now() - user_time).seconds
            local_log.debug(f'EndTimerFilter\t last: {diff_sec}\tstart timer: {user_time}')
            return {'time_last': self.__duration - diff_sec}
        
# фильтр для проверки соответствия пин-коду
class MatchPinCodeFilter(BaseFilter):
    async def __call__(self, message: Message, client: ClientRow):
        if not client.pincode:
            return False
        else:
            return message.text.strip() == client.pincode   # type: ignore
        
# фильтр проверяющий: восстанавливает ли пользователь pincode
class RestoringPinFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        user_data = await state.get_data()
        restore_flag = user_data.get('restore_pin', False)
        return bool(restore_flag)
    
# фильтр для проверки: достаточно ли денег на счету клиента
@local_log.wrapper()
class HaveMoneyToPayFilter(BaseFilter):
    async def __call__(self, message: Message, client: ClientRow):
        pay_amount = None
        try:
            pay_amount = Decimal(message.text)  # type: ignore
        except Exception:
            return False
        else:
            return pay_amount <= client.balance # type: ignore
        
# фильтр для проверки: сумма перевода - положительна
@local_log.wrapper()
class PositiveAmountFilter(BaseFilter):
    async def __call__(self, message: Message):
        pay_amount = None
        try:
            pay_amount = Decimal(message.text)  # type: ignore
        except Exception:
            return False
        else:
            return pay_amount > 0
        
# проверка: является ли строка числом с плавающей точкой
@local_log.wrapper()
class PositiveFloatFilter(BaseFilter):
    async def __call__(self, message: Message):
        float_num = None
        try:
            msg = message.text.replace(',', '.') # type: ignore
            float_num = Decimal(msg)  # type: ignore
        except Exception:
            return False
        else:
            return {'float_value': float_num} if float_num > 0 else False
        
@local_log.wrapper()
class GoalGreaterSumFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext):
        user_data = await state.get_data()
        user_sum = user_data.get('account_sum', None)
        assert user_sum is not None
        try:
            goal_amount = int(message.text) # type: ignore
        except Exception:
            return False
        else:
            return goal_amount > user_sum