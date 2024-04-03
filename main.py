from aiogram import Dispatcher, Bot, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode
import asyncio
from pydantic import SecretStr
from string import Template
from database import DataBase
from config import config


bot: Bot = Bot(config.bot_token.get_secret_value())
dp: Dispatcher = Dispatcher()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())


