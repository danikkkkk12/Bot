import asyncio
import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.types import Update
from aiohttp import web
from config import BOT_TOKEN
from handlers.client import router as client_router
from handlers.admin import router as admin_router
from database.db import DataBase

logger = logging.getLogger(__name__)

# Вебхук URL и путь
WEBHOOK_HOST = 'https://bot-d92o.onrender.com'  # Замени на твой домен с HTTPS
WEBHOOK_PATH = '/webhook'  # Путь для обработки вебхуков
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

async def on_start(msg):
    await msg.reply("Привет! Я работаю через вебхук!")

async def on_start_webhook(dp):
    # Устанавливаем вебхук
    await bot.set_webhook(WEBHOOK_URL)

async def handle(request):
    json_str = await request.json()
    update = Update(**json_str)
    await dp.process_update(update)
    return web.Response()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=f'[BOT] '
               f'{u"%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s"}')
    logger.info("Starting bot...")

    dp = Dispatcher()
    bot = Bot(BOT_TOKEN)
    dp.include_routers(client_router, admin_router)

    dp.startup.register(DataBase.on_startup)

    # Убираем старый webhook, если был
    await bot.delete_webhook(drop_pending_updates=True)

    # Настроим вебхук
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

    # Создаём веб-сервер
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)

    # Запуск веб-сервера
    port = int(os.getenv("PORT", 10000))
    logger.info(f"Listening on port {port}...")

    # Запускаем сервер внутри текущего цикла событий
    await web.run_app(app, host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Запуск main без asyncio.run(), так как сервер и бот работают в одном цикле событий
    asyncio.get_event_loop().run_until_complete(main())

