from aiogram import Router, F
from aiogram.filters import MagicData
from aiogram.types import Message

from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
from modules.database import DataBase
from modules.logger import Logger
from modules.database import ClientRow
import config as conf
from config import messages_dict, config
from keyboards import sign
from handlers import start

local_log = Logger('auth', f'{conf.PATH}/log/auth.log', level=conf.LOG_LEVEL)

router = Router()
# данная часть программы обрабатывает события лишь в том случае
# если пользователь НЕ авторизован и зарегистрирован
router.message.filter(MagicData(F.client.authorized.is_(False)), MagicData(F.client.reg_date))

