import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from bot.handlers.start import router as start_router
from bot.handlers.get_pmf import router as pmf_router
from bot.handlers.get_convolution import router as convolution_router

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties())
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.include_routers(
        start_router,
        pmf_router,
        convolution_router
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
