from aiogram import Router, F
from aiogram.filters import StateFilter, MagicData, BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import MessageEntityType

from datetime import date
from random import randint
import re
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

# фильтр для проверки соответствия строке шаблону
class MatchPatternFilter(BaseFilter):
    def __init__(self, pattern: re.Pattern):  
        self.__pattern = pattern
    
    async def __call__(self, message: Message):
        return bool(re.match(self.__pattern, message.text)) # type: ignore

# фильтр для проверки кода
class MatchCodeFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        user_data = await state.get_data()
        user_code: int | None = user_data.get('code', None)
        return message.text.strip() == str(user_code) if user_code else False # type: ignore

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
    local_log.info(f'Invalid email input:\n"{message.text}"\nby {client}')   # type: ignore
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
        main_log.info(f'Email code ({personal_code}) has been sent successfully to {user_data["email"]}\n{client}')
        await message.reply(messages_dict['code_send']) # type: ignore
        await message.answer(messages_dict['code_request'])  # type: ignore
        await state.set_state(InputStates.inputing_code) # type: ignore
    # ошибка отправки
    else:
        local_log.warning(f'Failed email sending code {user_data["email"]} failed\n{client}')
        await message.reply(messages_dict['code_error'], reply_markup=sign.send_email_input_kb()) # type: ignore
        
# успешный ввод кода с почты
@router.message(InputStates.inputing_code, MatchCodeFilter())
async def valid_code(message: Message, state: FSMContext, client: ClientRow):
    main_log.info(f'Correct input of email code: {message.text}\nby {client}')
    await message.reply(messages_dict['code_accepted']) # type: ignore
    await message.answer(messages_dict['pin_create'])   # type: ignore
    await state.set_state(InputStates.inputing_pin)
    
# неудачный ввода кода с почты
@router.message(InputStates.inputing_code)
async def invlid_code(message: Message, state: FSMContext, client: ClientRow):
    user_data = await state.get_data()
    local_log.info(f'Invalid code input:\n"{message.text}/{user_data["code"]}"\nby {client}')   # type: ignore
    await message.answer(messages_dict['invalid_code']) # type: ignore
    
# ввод pincode для регистрации (успешно)
@router.message(InputStates.inputing_pin, MagicData(F.client.reg_date.is_(None)), MatchPatternFilter(r'\b\d{4}\b')) # type: ignore
async def success_register(message: Message, state: FSMContext, client: ClientRow):
    pin = int(message.text) # type: ignore
    user_data = await state.get_data()
    # обновление данных пользователя
    row_updated: int = 0
    with DataBase(config.db_name.get_secret_value()) as db:
        db.update(
                    id = message.from_user.id, # type: ignore
                    pincode=pin,
                    email=user_data['email'],
                    balance=randint(0, 10_000),
                    reg_date=date.today()
                )
        row_updated = db.cur.rowcount
    if row_updated:
        main_log.info(f'Success register, created pin: {message.text}\nby {client}')
        await message.answer(messages_dict['reg_success']) # type: ignore
        await state.clear()
    else:
        main_log.warning(f'Fail register, created pin: {message.text}\nby {client}')
        await message.answer(messages_dict['reg_fail']) # type: ignore
        await message.answer(messages_dict['pin_request'])  # type: ignore
        
# ввод pincode для регистрации (неудача)
@router.message(InputStates.inputing_pin, MagicData(F.client.reg_date.is_(None)))
async def invalid_pincode_register(message: Message, client: ClientRow):
    local_log.info(f'Invalid pincode creation:\n"{message.text}"\nby {client}')   # type: ignore
    await message.answer(messages_dict['invalid_pin']) # type: ignore