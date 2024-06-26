from aiogram import Router, F, Bot
from aiogram.filters import Command, MagicData
from aiogram.types import Message, chat
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from datetime import datetime
from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.logger import Logger
from modules.database import ClientRow, DataBase
import config as conf
from config import messages_dict, config, buttons_dict
from keyboards import menu_kb as mkb, sign
from handlers.start import cmd_start, InputStates

local_log = Logger('pay', f'{conf.PATH}/log/pay.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()
router.message.filter(MagicData(F.client.authorized.is_(True)))

# выбор пользователя для оплаты
@router.message(Command('pay'))
@router.message(F.text.lower() == buttons_dict['pay'].lower())
async def start_pay(message: Message, state: FSMContext, client: ClientRow):
    main_log.info(f'Client use pay option\n{client}')
    await message.answer(messages_dict['pay_target_choice'], # type: ignore
                        reply_markup=mkb.choose_pay_target_kb())

# проверка: является ли выбранный пользователь клиентов банка
@router.message(F.user_shared)
async def check_target_user(message: Message, state: FSMContext, client: ClientRow):
    target_id = message.user_shared.user_id # type: ignore
    target_client: ClientRow | None
    with DataBase(config.db_name.get_secret_value()) as db:
        target_client = db.select(target_id)
    # пользователь - не клиент банка
    if not target_client:
        local_log.info(f'Target user is not a bank client\n{target_client}\n{client}')
        await message.answer(messages_dict['pay_target_no_client'], # type: ignore
                            reply_markup=mkb.choose_pay_target_kb())
    # id получатель равен клиенту
    elif target_id == client.id:
        local_log.info(f'Client inputed himself\n{target_client}\n{client}')
        await message.answer(messages_dict['pay_self_refuse'],  # type: ignore
                            reply_markup=mkb.choose_pay_target_kb())
    # получатель - клиент банка
    elif target_client.reg_date:
        main_log.info('Target user is a bank client')
        await message.answer(messages_dict['pay_target_accepted'])  # type: ignore
        await message.answer(messages_dict['pay_amount']) # type: ignore
        await state.update_data(pay_target_client = target_client)
        await state.set_state(InputStates.inputing_pay_amount)
        
# совершение платежа 
async def pay_attempt(message: Message, client: ClientRow, state: FSMContext, bot: Bot):
    await state.set_state(None)
    user_data = await state.get_data()
    pay_amount = user_data.get('pay_amount', None)
    pay_getter: ClientRow = user_data.get('pay_target_client', None)
    sender_row: int = 0
    getter_row: int = 0
    
    if not pay_amount and not pay_getter:
        local_log.warning(f'Can not find pay_amount or pay_getter:\n{user_data}\n{client}')
        await message.answer(messages_dict['pay_input_fail'],   # type: ignore
                            reply_markup=mkb.choose_pay_target_kb()   
                            )   # type: ignore
    else:
        main_log.info(f'Attempt to pay transfer, amount: {pay_amount}\nto {pay_getter}\nfrom {client}')
        with DataBase(config.db_name.get_secret_value()) as db:
            # списание с отправителя
            db.update(
                    id = client.id,
                    balance = client.balance - pay_amount
            )
            sender_row = db.cur.rowcount
            # добавление транзакции
            db.add_trans(
                type_id=db.DEBIT_ID,
                client_id=client.id,
                source_id=db.TRANSFER_ID,
                amount=-pay_amount,
                date=datetime.now(),
                desc=messages_dict['pay_transaction_sender'].substitute(getter=pay_getter.id),  # type: ignore
            )
            # начисление получателю
            db.update(
                    id = pay_getter.id,
                    balance = pay_getter.balance + pay_amount
            )
            getter_row = db.cur.rowcount
            # добавление транзакции
            db.add_trans(
                type_id=db.ACCRUAL_ID,
                client_id=pay_getter.id,
                source_id=db.TRANSFER_ID,
                amount=pay_amount,
                date=datetime.now(),
                desc=messages_dict['pay_transaction_getter'].substitute(sender=client.id),  # type: ignore
            )
    # проверка на успешность платежа
    if sender_row and getter_row:
        main_log.info(f'Successful transfer\nto {pay_getter}\nby {client}')
        # уведомление отправителю
        await message.answer(messages_dict['pay_sender_success'], # type: ignore
                            reply_markup=mkb.to_menu_kb()
                            )    
        # уведомление получателю
        if pay_getter.notifications:
            sender_username = f'@{message.from_user.username}'    # type: ignore
            local_log.info(f'Send transfer notification\nto {pay_getter}')
            await bot.send_message(
                chat_id=pay_getter.id,
                text=messages_dict['pay_getter_success'].substitute(amount = f'{pay_amount:,}', sender = sender_username), # type: ignore
                parse_mode=ParseMode.HTML,
            ) 
    else:
        local_log.error(f'Transfer update data error:\n{user_data}\n{client}')
        await message.answer(messages_dict['pay_input_fail'], # type: ignore
                            reply_markup=mkb.choose_pay_target_kb() 
                            )   