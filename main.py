import asyncio
import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.types import Update
from aiohttp import web
from aiohttp.web_runner import AppRunner
from config import BOT_TOKEN
from handlers.client import router as client_router
from handlers.admin import router as admin_router
from database.db import DataBase

logger = logging.getLogger(__name__)

# Вебхук URL и путь
WEBHOOK_HOST = 'https://bot-d92o.onrender.com'  # Замени на твой домен с HTTPS
WEBHOOK_PATH = '/webhook'  # Путь для обработки вебхуков
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

async def handle(request):
    """
    Обработчик входящих вебхуков.
    """
    json_str = await request.json()
    update = Update(**json_str)
    await dp.process_update(update)
    return web.Response()

async def on_startup(bot: Bot):
    """
    Действия при запуске бота.
    """
    # Убираем старый webhook, если был
    await bot.delete_webhook(drop_pending_updates=True)

    # Настраиваем вебхук
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

async def main():
    """
    Основная функция для запуска бота и веб-сервера.
    """
    logging.basicConfig(
        level=logging.INFO,
        format=f'[BOT] {u"%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s"}'
    )
    logger.info("Starting bot...")

    # Инициализация бота и диспетчера
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем роутеры
    dp.include_routers(client_router, admin_router)

    # Регистрируем startup-функцию
    dp.startup.register(on_startup)
    dp.startup.register(DataBase.on_startup)

    # Создаём веб-приложение
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)

    # Запуск с использованием AppRunner
    runner = AppRunner(app)
    await runner.setup()

    # Устанавливаем порт для Render
    port = int(os.getenv("PORT", 10000))
    logger.info(f"Listening on port {port}...")

    # Запускаем сервер
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    # Бесконечный цикл для поддержания работы сервера
    try:
        while True:
            await asyncio.sleep(3600)  # Спим, чтобы не завершать цикл
    except asyncio.CancelledError:
        logger.info("Shutting down...")
    finally:
        # Закрываем ресурсы
        await bot.session.close()
        await runner.cleanup()

if __name__ == '__main__':
    # Используем текущий цикл событий
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    finally:
        loop.close()


