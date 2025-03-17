import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiohttp import web
from app.handlers import router1
from config import TOKEN

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
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен на {WEBHOOK_URL}")

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

    print(f"Бот запущен на порту {port}...")
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bye Bye')
