from aiogram import Router, F
from aiogram.filters import Command, MagicData
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.exceptions import AiogramError

from math import ceil
from typing import Dict
from datetime import datetime
from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.logger import Logger
from modules.database import ClientRow, DataBase
import config as conf
from config import messages_dict, config, buttons_dict
from keyboards import menu_kb as mkb, sign
from handlers.start import cmd_start, InputStates

local_log = Logger('history', f'{conf.PATH}/log/history.log', level=conf.LOG_LEVEL)
main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

router = Router()
router.message.filter(MagicData(F.client.authorized.is_(True)))
current_page: Dict[int, int] = {}

# отправка сообщения
@router.message(F.text.lower() == buttons_dict['history'].lower())
@router.message(Command('history'))
async def show_history(message: Message, client: ClientRow):
    main_log.info(f'Client want to get history\n{client}')
    with DataBase(config.db_name.get_secret_value()) as db:
        trans = db.select_client_trans(client.id)
    # клиент не совершал транзакций
    if len(trans) == 0:
        await message.answer(messages_dict['history_empty'])    # type: ignore
        return
    table = DataBase.generate_trans_table(trans[:conf.TRANS_PAGE_COUNT])
    await message.answer(
        table,
        reply_markup=mkb.history_slider_kb(client.id))
    global current_page
    current_page[client.id] = 0
        
# обработка прокрутки
@router.callback_query(mkb.SliderCallback.filter())
async def handler_slider_callback(
                        callback: CallbackQuery, 
                        callback_data: mkb.SliderCallback,
                        ):
    client_id = callback_data.client_id
    size = conf.TRANS_PAGE_COUNT
    lim_slide = False
    with DataBase(config.db_name.get_secret_value()) as db:
        trans = db.select_client_trans(client_id)
    groups_count = ceil(len(trans) // size) 
    global current_page
    ind = current_page[client_id]
    match callback_data.action:
        case 'right':
            # текущая страница - последняя
            if ind == (groups_count - 1):
                new_ind = ind
                lim_slide = True
            # переход к следующей странице
            else:
                new_ind = ind + 1
            # new_ind = ind + 1 if ind < (groups_count - 1) else ind
            local_log.info(f'Handle "right" button by #{client_id}\nind: {ind}\tnew_ind: {new_ind}\ttrans_count: {len(trans)}\tgroups_count: {groups_count}')
        case 'left':
            # текущая страница - первая
            if ind == 0:
                new_ind = ind
                lim_slide = True
            # переход к предыдущей странице
            else:
                new_ind = ind - 1
            # new_ind = ind - 1 if ind > 0 else ind
            local_log.info(f'Handle "left" button by #{client_id}\nind: {ind}\tnew_ind: {new_ind}\ttrans_count: {len(trans)}\tgroups_count: {groups_count}')
    current_page[client_id] = new_ind
            
    try:
        table = DataBase.generate_trans_table(trans[new_ind*size:(new_ind+1)*size])
        await callback.message.edit_text(table) # type: ignore
        await callback.message.edit_reply_markup(reply_markup=mkb.history_slider_kb(client_id))   # type: ignore
        # отправка ответа
        if lim_slide:
            await callback.answer(messages_dict['history_first_page']) if (new_ind == 0) and (callback_data.action == 'left')  else await callback.answer(messages_dict['history_last_page']) # type: ignore
        else:
            await callback.answer() 
            
    except AiogramError as error:
        local_log.exception(f'Aiogram exception\n{error}')
    except Exception as error:
        local_log.exception(f'Another exceptions\n{error}')
    else:
        local_log.debug('Successful handle the button')