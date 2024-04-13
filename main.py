from aiogram import Dispatcher, Bot
import asyncio
from config import config
from handlers import start, register, auth
from middlewares.data_getters import GetClient

bot: Bot = Bot(config.bot_token.get_secret_value())
dp: Dispatcher = Dispatcher()
dp.message.outer_middleware(GetClient())

async def main():
    dp.include_routers(
            start.router,
            auth.router,
            register.router,
            )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())


