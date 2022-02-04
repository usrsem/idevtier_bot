from aiogram import executor
from handlers import dp
from loguru import logger as log

if __name__ == '__main__':
    log.info("Start polling :)")
    executor.start_polling(dp, skip_updates=True)
