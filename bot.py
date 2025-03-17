import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.exceptions import TelegramRetryAfter
from aiohttp import web
from app.handlers import router1
from config import TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Вебхук настройки
WEBHOOK_HOST = 'https://bot-d92o.onrender.com'  # Замени на свой хост
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

async def handle(request):
    """
    Обработчик входящих вебхуков.
    """
    dp = request.app['dp']
    bot = request.app['bot']
    json_str = await request.json()
    update = Update(**json_str)
    await dp.feed_update(bot, update)
    return web.Response()

async def on_startup(bot: Bot):
    """
    Установка вебхука при старте.
    """
    try:
        # Удаляем старый вебхук и отключаем обработку ожидающих обновлений
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Добавляем задержку перед установкой вебхука
        await asyncio.sleep(1)
        
        # Устанавливаем новый вебхук
        await bot.set_webhook(WEBHOOK_URL)
        logger.info(f"Webhook установлен на {WEBHOOK_URL}")
    except TelegramRetryAfter as e:
        # Обработка ошибки "Too Many Requests"
        logger.warning(f"Ошибка: {e}. Повторная попытка через {e.retry_after} секунд.")
        await asyncio.sleep(e.retry_after)
        await on_startup(bot)
    except Exception as e:
        logger.error(f"Ошибка при установке вебхука: {e}")

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router1)

    # Устанавливаем вебхук при старте
    await on_startup(bot)

    # Создаём веб-приложение
    app = web.Application()
    app['dp'] = dp
    app['bot'] = bot
    app.router.add_post(WEBHOOK_PATH, handle)

    # Запуск веб-сервера
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    logger.info(f"Бот запущен на порту {port}...")
    
    # Бесконечный цикл для поддержания работы бота
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bye Bye')