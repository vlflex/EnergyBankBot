from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

from sys import path
path.append('../') 
from modules.database import DataBase, ClientRow
from modules.logger import Logger
from config import config as conf, LOG_LEVEL

local_log = Logger('data_getters', 'D:/Университет/Учебная практика/Bank bot/log/data_getters.log', level=LOG_LEVEL)
class GetClient(BaseMiddleware):
    """Search client in the database and get/add info about user
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        with DataBase(conf.db_name.get_secret_value()) as db:
            user = data["event_from_user"]
            client_row = db.select(user.id)
            if not client_row:
                db.add(user.id) 
                local_log.info(f'Client({user.id}) was not in the database. He has been added')
                client_row = db.select(user.id)
            else:
                local_log.info(f'Client({user.id}) has been found in the database\nReturn {client_row}')
                
            data["client"]: ClientRow | None = client_row # type: ignore
            
        return await handler(event, data)