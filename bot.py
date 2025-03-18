import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramRetryAfter
from aiohttp import web
from app.handlers import router1  # Импортируем роутер
from config import TOKEN  # Импортируем токен бота

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Вебхук настройки
WEBHOOK_HOST = 'https://bot-d92o.onrender.com'  # Замени на свой хост
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# ID чата для уведомлений (замени на свой)

async def handle_webhook(request):
    """
    Обработчик входящих вебхуков от Telegram.
    """
    dp = request.app['dp']
    bot = request.app['bot']
    try:
        json_str = await request.json()
        update = types.Update(**json_str)
        await dp.feed_update(bot, update)
        return web.Response()
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {e}")
        return web.Response(status=500)

async def handle_postback(request):
    """
    Обработчик входящих постбеков от партнёрки.
    """
    bot = request.app['bot']
    try:
        # Получаем данные из GET-запроса (или POST, если нужно)
        data = request.query  # Для GET-запросов
        # Если данные в JSON (POST), используй: data = await request.json()

        # Логируем данные
        logger.info(f"Received postback data: {data}")

        # Пример обработки данных
        action = data.get('action')
        user_id = data.get('user_id')
        amount = data.get('amount')

        if action == 'registration':
            message = f"🎉 Новая регистрация!\nUser ID: {user_id}"
            await bot.send_message(ADMIN_ID, message)

        elif action == 'deposit':
            message = f"💰 Новый депозит!\nUser ID: {user_id}\nAmount: {amount}"
            await bot.send_message(ADMIN_ID, message)

        # Отвечаем партнёрке, что всё ок
        return web.json_response({"status": "ok"})

    except Exception as e:
        logger.error(f"Ошибка при обработке постбека: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

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
    # Инициализация бота и диспетчера
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router1)  # Подключаем роутер

    # Устанавливаем вебхук при старте
    await on_startup(bot)

    # Создаём веб-приложение
    app = web.Application()
    app['dp'] = dp
    app['bot'] = bot

    # Добавляем обработчики
    app.router.add_post(WEBHOOK_PATH, handle_webhook)  # Для вебхуков Telegram
    app.router.add_get('/postback', handle_postback)  # Для постбеков от партнёрки
    app.router.add_post('/postback', handle_postback)  # Если партнёрка отправляет POST

    # Запуск веб-сервера
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 10000))  # Порт для Render
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