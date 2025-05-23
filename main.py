import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from middleware import log_middleware
from handlers import dp_router



load_dotenv()
bot = Bot(token=os.getenv("TG_TOKEN"))
dp = Dispatcher()
dp.update.middleware(log_middleware)
dp.include_router(dp_router)


if __name__ == "__main__":
    dp.run_polling(bot)