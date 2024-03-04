from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
import sys
sys.path.append('../') 
from database import DataBase
from user import User
from config import messages_dict
from keyboards import sign

router = Router()
db = DataBase('data/clients.db')
user: User

# обработка команды старт
@router.message(Command('start'))
async def cmd_start(message: Message):
    global user
    user = db.get_user(message.from_user.id)    # type: ignore
    await message.answer(messages_dict['greet'].substitute(name = message.from_user.full_name),
                        reply_markup=sign.get_register_auth_keyboard())

