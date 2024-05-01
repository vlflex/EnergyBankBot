from aiogram import Router, F
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.utils.formatting import as_marked_section, as_key_value

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
async def choose_account_type(message: Message, client: ClientRow, state: FSMContext):
    await message.answer(
                messages_dict['calc_choose'],   # type: ignore
                reply_markup=mkb.credit_deposite_kb(),
                ) 
    await state.clear()
    main_log.info(f'Client use calculator\n{client}')
    
# обработка кнопок выбора счета
@router.message(F.text.lower() == buttons_dict['calc_credit'].lower())
@router.message(F.text.lower() == buttons_dict['calc_deposite'].lower())
async def account_input(message: Message, state: FSMContext, client: ClientRow):
    await state.update_data(account=message.text)
    await message.answer(messages_dict['calc_input_sum'])   # type: ignore
    local_log.info(f'Start input account\n{client}')
    await state.set_state(InputStates.inputing_calc_sum)

# вычисление количества месяцев
@router.message(F.text.lower() == buttons_dict['calc_months'].lower(), InputStates.choosing_data)
async def calculate_months(message: Message, state: FSMContext, client: ClientRow):
    await message.answer(messages_dict['calc_input_fill'])  # type: ignore
    await state.set_state(InputStates.inputing_calc_fill)
    await state.update_data(calc_months = True)
    local_log.info(f'Months calculation has been chosen\n{client}')

# вычисление суммы пополнения
@router.message(F.text.lower() == buttons_dict['calc_fill'].lower(), InputStates.choosing_data)
async def calculate_fill(message: Message, state: FSMContext, client: ClientRow):
    await message.answer(messages_dict['calc_input_months'])  # type: ignore
    await state.set_state(InputStates.inputing_calc_months)
    await state.update_data(calc_fill = True)
    local_log.info(f'Fill calculation has been chosen\n{client}')

# выбор искомых данных
@router.message(InputStates.choosing_data)
async def choose_data(message: Message, state: FSMContext, client: ClientRow):
    await message.answer(messages_dict['calc_choose_data'],# type: ignore
                        reply_markup=mkb.months_amount_kb(),
                        parse_mode=ParseMode.HTML,
                        )  
    local_log.info(f'Choose data\n{client}')
    
# вычисление выбранных данных
async def calculate_data(message: Message, state: FSMContext, client: ClientRow):
    # получение сохраненных данных
    user_data = await state.get_data()
    type_ = user_data['account']
    sum_ = float(user_data['account_sum'])
    rate = float(user_data['account_rate'])
    calc_month = user_data.get('calc_months', False)
    calc_fill = user_data.get('calc_fill', False) 
    fill = float(user_data.get('account_fill', 0))
    months = user_data.get('account_months', 0)
    account = None
    # вычисления в зависимости от типа счета
    if type_ == buttons_dict['calc_credit']:
        account = CreditAccount(sum_, rate, fill)
    elif type_ == buttons_dict['calc_deposite']:
        goal = user_data['account_goal']
        account = DepositAccount(sum_, rate, fill, goal)
    assert account is not None
    local_log.info(f'Account var: {account}\n{client}')
    # сообщение о введенных данных
    start_data_msg = as_marked_section(
        messages_dict['calc_inputed_data'],
        as_key_value(messages_dict['calc_start_sum'], f'{sum_:,.0f}'),
        as_key_value(messages_dict['calc_rate'], f'{rate:,.2f}%'),   
        as_key_value(messages_dict['calc_fill'], f'{fill:,.0f}') if calc_month
        else as_key_value(messages_dict['calc_months'], f'{months:,.0f}'),
        marker=messages_dict['calc_marker'],    # type: ignore
    )
    # получение вычисляемых данных
    if calc_month:
        try:
            await message.answer(
                            **start_data_msg.as_kwargs(),
                            )
            months_count = account.get_months_to_paid() if isinstance(account, CreditAccount) else account.get_months_to_achieve()
        except ValueError:
            await message.answer(messages_dict['calc_error'])   # type: ignore
        else:
            await message.answer(
                    messages_dict['calc_month_result'].substitute(months=f'{months_count:,}'),    # type: ignore
                    parse_mode=ParseMode.HTML,
                    )
            main_log.info(f'Calculator has showen a result: {months_count}\n{client}')
    elif calc_fill:
        await message.answer(
                        **start_data_msg.as_kwargs(),
                        )
        fill_amount = account.get_fill_to_paid(months) if isinstance(account, CreditAccount) else account.get_fill_to_achieve(months)
        await message.answer(
                            messages_dict['calc_fill_result'].substitute(fill=f'{fill_amount:,.0f}'),    # type: ignore
                            parse_mode=ParseMode.HTML,
                            )
        main_log.info(f'Calculator has showen a result: {fill_amount}\n{client}')