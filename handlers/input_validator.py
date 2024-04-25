from aiogram import Router, F, Bot
from aiogram.filters import MagicData
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import MessageEntityType, ParseMode

from decimal import Decimal
from datetime import date, datetime
from random import randint
from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.database import DataBase
from modules.logger import Logger
from modules.database import ClientRow
from modules.email_sender import EmailSender
import config as conf
from config import messages_dict, config, create_email_form, buttons_dict
from keyboards import sign
from handlers.start import InputStates, cmd_start
from handlers.auth import login
from handlers.pay import pay_attempt
from filters.validation import MatchPatternFilter, MatchCodeFilter, TimerFilter, MatchPinCodeFilter, RestoringPinFilter, HaveMoneyToPayFilter, PositiveAmountFilter

local_log = Logger('input_validator', f'{conf.PATH}/log/input_validator.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()

# email введен корректно
@router.message(F.entities[...].type == MessageEntityType.EMAIL, InputStates.inputing_email)
async def valid_email(message: Message, state: FSMContext, client: ClientRow):
    user_email: str 
    # извлечение email
    for item in message.entities: # type: ignore
        if item.type == MessageEntityType.EMAIL:
            user_email = item.extract_from(message.text).strip() # type: ignore
            await state.update_data(email = user_email.lower())
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
@router.message(F.text.lower() ==  buttons_dict['send_code'].lower(), InputStates.sending_code)
async def code_sender(message: Message, state: FSMContext, client: ClientRow):
    # попытка отправки кода на введенный email
    user_data = await state.get_data()
    personal_code = randint(100_000, 999_999)
    await state.update_data(code = personal_code)
    # генерация содержимого email
    email_to_user = create_email_form(
        email=user_data['email'] if not client.email else client.email,
        code=personal_code,
        # reg_date == None => это регистрация
        registration=not(bool(client.reg_date))
    )
    email_success: bool
    with EmailSender() as es:
        email_success = es.send(**email_to_user)
    # код успешно отправлен
    if email_success:
        main_log.info(f'Email code ({personal_code}) has been sent successfully to {user_data["email"] if not client.email else client.email}\n{client}')
        await message.reply(messages_dict['code_send']) # type: ignore
        await message.answer(messages_dict['code_request'])  # type: ignore
        await state.set_state(InputStates.inputing_code) # type: ignore
        # сохранения отправки сообщения для таймера
        await state.update_data(start_timer=datetime.now())
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
    attempts = user_data.get('code_attempts', 0)
    await state.update_data(code_attempts=attempts+1)
    local_log.info(f'Invalid code input ({attempts+1}/{conf.CODE_ATTEMPTS}):\n"{message.text} / {user_data["code"]}"\nby {client}')   # type: ignore
    await message.answer(messages_dict['invalid_code']) # type: ignore
    # превышено число попыток 
    if attempts+2>= conf.CODE_ATTEMPTS:
        await state.set_state(InputStates.waiting_send_code)
    
# ожидание повторной отправки кода
@router.message(InputStates.waiting_send_code, TimerFilter(conf.CODE_COOLDOWN))
async def timer(message: Message, client: ClientRow, state: FSMContext, time_last: int):
    local_log.info(f'Waiting for sending code, last: {time_last}\n{client}')
    if time_last > 0:
        await message.reply(messages_dict['multiple_invalid_code'].substitute(time=time_last),  # type: ignore
                            reply_markup=sign.send_kb(),
                            parse_mode=ParseMode.HTML,
                            ) # type: ignore
    else:
        local_log.info(f'Timer is over: {time_last}')
        await state.update_data(code_attempts=0)
        await state.set_state(InputStates.sending_code)
        await code_sender(message=message, client=client, state=state)

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
    
# успешный ввод нового pin и его сброс
@router.message(InputStates.inputing_pin, MagicData(F.client.reg_date), RestoringPinFilter(), MatchPatternFilter(r'\b\d{4}\b')) # type: ignore
async def pincode_reset(message: Message, state: FSMContext, client: ClientRow):
    pin = int(message.text) # type: ignore
    # обновление данных пользователя 
    row_updated: int = 0
    with DataBase(config.db_name.get_secret_value()) as db:
        db.update(
                    id = message.from_user.id, # type: ignore
                    pincode=pin,
                    email=client.email,
                )
        row_updated = db.cur.rowcount
    if row_updated:
        main_log.info(f'Success pin restore, created pin: {message.text}\nby {client}')
        await message.answer(messages_dict['restore_success']) # type: ignore
        await state.clear()
    else:
        main_log.warning(f'Fail pin restore, created pin: {message.text}\nby {client}')
        await message.answer(messages_dict['restore_fail']) # type: ignore
        await message.answer(messages_dict['pin_request'])  # type: ignore


# ввод pincode для регистрации (неудача)
@router.message(InputStates.inputing_pin, RestoringPinFilter()) # type: ignore
@router.message(InputStates.inputing_pin, MagicData(F.client.reg_date.is_(None))) # type: ignore
async def invalid_pincode_register(message: Message, client: ClientRow):
    local_log.info(f'Invalid pincode creation:\n"{message.text}"\nby {client}')   # type: ignore
    await message.answer(messages_dict['invalid_pin']) # type: ignore
    
# ввод pincode для авторизации (успешно)
@router.message(InputStates.inputing_pin, MatchPinCodeFilter()) # type: ignore
async def auth_success(message: Message, state: FSMContext, client: ClientRow):
    user_data = await state.get_data()
    change_pin = user_data.get('new_pin', False)
    if not change_pin:
        with DataBase(config.db_name.get_secret_value()) as db:
            db.update(id = client.id, authorized=True)
        main_log.info(f'Successful authorization by\n {client}')
        await cmd_start(message, client, state)
    else:
        await state.update_data(restore_pin=True)
        await state.set_state(InputStates.inputing_pin)
        main_log.info(f'Successful pin-code input by\n{client}')
        await message.answer(messages_dict['pin_create'])   # type: ignore
    
# восстановление pin через email
@router.message(InputStates.waiting_input_pin, MagicData(F.client.reg_date), F.text == buttons_dict['email_restore'])
async def email_restore_pin(message: Message, state: FSMContext, client: ClientRow):
    await state.update_data(restore_pin=True)
    await code_sender(message=message, client=client, state=state)
    
# ввод pincode для авторизации (неудача)
@router.message(InputStates.inputing_pin, MagicData(F.client.reg_date)) # type: ignore
async def auth_fail(message: Message, state: FSMContext, client: ClientRow):
    user_data = await state.get_data()
    attempts = user_data.get('pin_attempts', 0)
    await state.update_data(pin_attempts=attempts+1)
    local_log.info(f'Invalid pin-code input ({attempts+1}/{conf.CODE_ATTEMPTS}):\n"{message.text} / {client.pincode}"\nby {client}')   # type: ignore
    await message.answer(messages_dict['invalid_pin']) # type: ignore
    # превышено число попыток 
    if attempts+2>= conf.CODE_ATTEMPTS:
        await state.update_data(start_timer=datetime.now())
        await state.set_state(InputStates.waiting_input_pin)

# ожидание повторной отправки кода
@router.message(InputStates.waiting_input_pin, TimerFilter(conf.CODE_COOLDOWN))
async def pin_timer(message: Message, client: ClientRow, state: FSMContext, time_last: int):
    local_log.info(f'Waiting for pin input, last: {time_last}\n{client}')
    if time_last > 0:
        await message.reply(messages_dict['multiple_invalid_pin'].substitute(time=time_last),  # type: ignore
                            reply_markup=sign.email_restore_input_pin(),
                            parse_mode=ParseMode.HTML,
                            )
    else:
        local_log.info(f'Timer is over: {time_last}')
        await state.update_data(pin_attempts=0)
        await state.set_state(InputStates.inputing_pin)
        await login(message=message, client=client, state=state)
        
# ввод суммы для платежа: успех, совершение платежа
@router.message(InputStates.inputing_pay_amount, MatchPatternFilter(r'^\d+(\.|\,)?\d*$'), HaveMoneyToPayFilter(), PositiveAmountFilter())   # type: ignore
async def pay_input_success(message: Message, client: ClientRow, state: FSMContext, bot: Bot):
    await message.reply(messages_dict['pay_attempt'])   # type: ignore
    main_log.info(f'Go to try transfer: {message.text}\n{client}')
    amount = Decimal(message.text)    # type: ignore
    await state.update_data(pay_amount=amount)
    await pay_attempt(message, client, state, bot)

# ввод суммы для платежа: недостаточно средств
@router.message(InputStates.inputing_pay_amount, MatchPatternFilter(r'^\d+(\.|\,)?\d*$'), PositiveAmountFilter())   # type: ignore
async def pay_input_not_enough_money(message: Message, client: ClientRow, state: FSMContext):
    local_log.info(f'Client have no enough money: {message.text}\n{client}')
    await message.reply(messages_dict['pay_input_nomoney']) # type: ignore

# ввод суммы для платежа: неверный формат
@router.message(InputStates.inputing_pay_amount)
async def pay_input_invalid(message: Message, client: ClientRow):
    local_log.info(f'Client invalid input: {message.text}\n{client}')
    await message.reply(messages_dict['pay_input_invalid']) # type: ignore