from aiogram import Dispatcher, Bot, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode
import asyncio
from pydantic import SecretStr
import sentry_sdk
from string import Template
from database import DataBase

# sentry

# secret str
bot: Bot = Bot('6546159525:AAE0G11LWoL6ZzvqvzlzAkoHqUBtq6DoZ6c')
dp: Dispatcher = Dispatcher()

@dp.message(Command('start'))
async def cmd_start(message: Message):
    pass
        
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())


