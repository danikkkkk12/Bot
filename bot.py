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
# ID чата для уведомлений (замени на свой)
ADMIN_CHAT_ID = -1002616661905  # Узнать можно через @userinfobot
# Вебхук настройки
WEBHOOK_HOST = 'https://bot-d92o.onrender.com'  # Замени на свой хост
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

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
    bot = request.app['bot']
    try:
        # Логируем метод запроса (GET или POST)
        logger.info(f"Request method: {request.method}")

        # Получаем данные в зависимости от метода
        data = request.query if request.method == 'GET' else await request.post()

        # Логируем все данные
        logger.info(f"Received postback data: {dict(data)}")

        # Функция для преобразования 'null' в None
        def parse_value(value):
            return None if value == 'null' else value

        # Пример обработки данных
        action = data.get('action', 'unknown')
        user_id = parse_value(data.get('user_id'))
        country = data.get('country')
        sub1 = parse_value(data.get('sub1'))
        sub2 = parse_value(data.get('sub2'))
        sub3 = parse_value(data.get('sub3'))
        sub4 = parse_value(data.get('sub4'))
        amount = data.get('amount', 0)

        # Логируем каждое поле
        logger.info(f"Action: {action}")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Country: {country}")
        logger.info(f"Sub1: {sub1}")
        logger.info(f"Sub2: {sub2}")
        logger.info(f"Sub3: {sub3}")
        logger.info(f"Sub4: {sub4}")
        logger.info(f"Amount: {amount}")

        if action == 'registration':
            message = f"🎉 Новая регистрация!\nUser ID: {user_id}\nCountry: {country}"
            await bot.send_message(ADMIN_CHAT_ID, message)
            logger.info(f"Уведомление отправлено в чат администратора: {message}")

        elif action == 'deposit':
            message = f"💰 Новый депозит!\nUser ID: {user_id}\nAmount: {amount}"
            await bot.send_message(ADMIN_CHAT_ID, message)
            logger.info(f"Уведомление отправлено в чат администратора: {message}")

        # Отвечаем партнёрке, что всё ок
        return web.json_response({"status": "ok"})

    except Exception as e:
        logger.error(f"Ошибка при обработке постбека: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def handle_root(request):
    """
    Обработчик для корневого пути.
    """
    return web.Response(text="Server is running")

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
    app.router.add_get('/', handle_root)  # Обработчик для корневого пути

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
