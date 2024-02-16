from aiogram import Dispatcher, Bot, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode
import asyncio
from pydantic import SecretStr
import sentry_sdk
from string import Template
from database import DataBase
import sentry_sdk

sentry_sdk.init(
    dsn="https://77424977a50d8cd32312624d13bc12f8@o4506209236484096.ingest.sentry.io/4506755171352576",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
dp: Dispatcher = Dispatcher()

@dp.message(Command('start'))
async def cmd_start(message: Message):
    pass
        
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())


