from aiogram import Router, F
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.logger import Logger
from modules.database import ClientRow, DataBase
import config as conf
from config import messages_dict, config, buttons_dict
from keyboards import menu_kb as mkb
from handlers.start import cmd_start, InputStates

local_log = Logger('settings', f'{conf.PATH}/log/settings.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()
router.message.filter(MagicData(F.client.authorized.is_(True)))

# отображение меню 
@router.message(F.text.lower() == buttons_dict['settings'].lower())
@router.message(Command('settings'))
async def settings_menu(message: Message, client: ClientRow):
    await message.answer(
                messages_dict['sets_choose'],    # type: ignore
                reply_markup=mkb.settings_menu_kb(client.notifications),
                )  
    
# включение или выключение уведомлений
@router.message(F.text.lower() == buttons_dict['sets_nots_on'].lower())
@router.message(F.text.lower() == buttons_dict['sets_nots_off'].lower())
async def switch_notifications(message: Message, client: ClientRow):
    update_result: bool
    with DataBase(config.db_name.get_secret_value()) as db:
        db.update(
                id = client.id,
                notifications=not client.notifications,
        )
        update_result = bool(db.cur.rowcount)
    # успешное обновление записи
    if update_result:
        main_log.info(f'Successful switch notifications\n{client}')
        await message.reply(
                    messages_dict['sets_updates'], # type: ignore
                    reply_markup=mkb.settings_menu_kb(not client.notifications),
                    )  
    else:
        local_log.warning(f'Update client row error\n{client}')
        await message.reply(
                    messages_dict['sets_nots_error'],    # type: ignore
                    reply_markup=mkb.settings_menu_kb(not client.notifications),
        )
        
# выход из аккаунта
@router.message(F.text.lower() == buttons_dict['sets_exit'].lower())
async def account_exit(message: Message, state: FSMContext, client: ClientRow):
    user_data = await state.get_data()
    exit_try = user_data.get('exit', False)
    # первая попытка выхода
    if not exit_try:
        await message.reply(
            messages_dict['sets_exit_warning'],  # type: ignore
            reply_markup=mkb.menu_exit_kb(),
        )
        await state.update_data(exit=True)
        local_log.info(f'Client want to exit from account\n{client}')
    # вторая попытка выхода: выход
    else:
        with DataBase(config.db_name.get_secret_value()) as db:
            db.update(
                id = client.id,
                authorized=False,
            )
        main_log.info(f'Client has exited from account\n{client}')
            
# смена пин-кода
@router.message(F.text.lower() == buttons_dict['sets_pincode'].lower())
async def change_pin(message: Message, state: FSMContext, client: ClientRow):
    main_log.info(f'Client changing pic-code\n{client}')
    await state.set_state(InputStates.inputing_pin)
    await state.update_data(new_pin = True)
    await message.reply(messages_dict['pin_request'])  # type: ignore
    
# 