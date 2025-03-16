import asyncio
import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.types import Update
from aiohttp import web
from aiohttp.web_runner import AppRunner
from config import BOT_TOKEN
from handlers.client import router as client_router  # Импортируем роутер из client.py
from handlers.admin import router as admin_router    # Импортируем роутер из admin.py
from other.filters import router as filters_router  # Импортируем роутер из filters.py
from database.db import DataBase

# Настройка логирования
logger = logging.getLogger(__name__)

# Вебхук URL и путь
WEBHOOK_HOST = 'https://bot-d92o.onrender.com'  # Замени на твой домен с HTTPS
WEBHOOK_PATH = '/webhook'  # Путь для обработки вебхуков
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

async def handle(request):
    """
    Обработчик входящих вебхуков.
    """
    dp = request.app['dp']  # Получаем Dispatcher из контекста
    bot = request.app['bot']  # Получаем Bot из контекста
    json_str = await request.json()
    update = Update(**json_str)
    await dp.feed_update(bot, update)  # Передаём bot и update
    return web.Response()

async def on_startup(bot: Bot):
    """
    Действия при запуске бота.
    """
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(WEBHOOK_URL)
        logger.info(f"Webhook set to {WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"Ошибка при настройке вебхука: {e}")

async def on_shutdown(bot: Bot, runner: AppRunner):
    """
    Действия при завершении работы бота.
    """
    try:
        await bot.session.close()
        await runner.cleanup()
        logger.info("Bot shutdown completed.")
    except Exception as e:
        logger.error(f"Ошибка при завершении работы бота: {e}")

async def main():
    """
    Основная функция для запуска бота и веб-сервера.
    """
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format=f'[BOT] {u"%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s"}'
    )
    logger.info("Starting bot...")

    try:
        # Инициализация бота и диспетчера
        bot = Bot(BOT_TOKEN)
        dp = Dispatcher()

        # Подключаем роутеры
        dp.include_routers(
            client_router,  # Роутер из client.py
            admin_router,   # Роутер из admin.py
            filters_router  # Роутер из filters.py
        )

        # Регистрируем startup-функции
        dp.startup.register(on_startup)
        dp.startup.register(DataBase.on_startup)

        # Создаём веб-приложение
        app = web.Application()
        app['dp'] = dp  # Передаём Dispatcher в контекст приложения
        app['bot'] = bot  # Передаём Bot в контекст приложения
        app.router.add_post(WEBHOOK_PATH, handle)

        # Запуск веб-сервера
        runner = AppRunner(app)
        await runner.setup()

        port = int(os.getenv("PORT", 10000))
        logger.info(f"Listening on port {port}...")

        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()

        # Бесконечный цикл для поддержания работы сервера
        while True:
            await asyncio.sleep(3600)

    except asyncio.CancelledError:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        # Завершение работы бота
        await on_shutdown(bot, runner)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    finally:
        loop.close()