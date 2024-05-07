from aiogram import Dispatcher, Bot
import asyncio
from config import config
import config as conf
from handlers import start, register, auth, input_validator as iv, casino, menu, pay, currency, history, settings, calculator, help
from handlers import casino
from middlewares.data_getters import GetClient
from modules.logger import Logger

main_log = Logger('main', f'{conf.PATH}/log/main.log', level=conf.LOG_LEVEL)

bot: Bot = Bot(config.bot_token.get_secret_value())
dp: Dispatcher = Dispatcher()
dp.message.outer_middleware(GetClient())

async def main():
    dp.include_routers(
            start.router,
            menu.router,
            casino.router,
            help.router,
            calculator.router,
            settings.router,
            history.router,
            pay.router,
            currency.router,
            iv.router,
            auth.router,
            register.router,
            )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as error:
        main_log.exception(f'Main exception:\n{error}')

