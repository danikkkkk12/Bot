import sqlite3
import aiohttp  # Импортируем aiohttp для асинхронных HTTP-запросов
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
import app.keyboard as kb
from aiogram.types import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import *

router1 = Router()

# Настройка базы данных
def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

setup_database()

# Состояния для FSM
class SpamState(StatesGroup):
    message = State()

# Добавление пользователя
def add_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return {"status": "success", "message": f"Пользователь {user_id} успешно добавлен."}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": f"Пользователь {user_id} уже существует."}
    except sqlite3.Error as e:
        return {"status": "error", "message": f"Ошибка базы данных: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Непредвиденная ошибка: {e}"}
    finally:
        conn.close()

# Получение всех пользователей
def get_all_users():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = [row[0] for row in cursor.fetchall()]
        return users
    except sqlite3.OperationalError as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return []
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return []
    finally:
        conn.close()

# Асинхронная функция для проверки регистрации пользователя с использованием aiohttp
async def check_registration(user_id):
    api_url = f"https://1wcneg.com/gtyb/api/check_registration?user_id={user_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("registered", False)
                else:
                    return False
    except Exception as e:
        print(f"Ошибка при проверке регистрации: {e}")
        return False

# Команда /start
@router1.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    add_user(user_id)
    with open('start.jpg', 'rb') as photo:
        await message.answer_photo(
            FSInputFile('start.jpg'),
            caption=(
                f'Добро пожаловать в бота {NAME}!'

                '🌐Шаг 1 - Зарегистрируйся '

                '⚪ Для синхронизации с ботом, вам необходимо создать новый аккаунт строго по ссылке из бота и примините промокод:'

                'Промокод: 👉MinesCrazy👈 '

                '🔵Если вы открыли ссылку и попали в старый аккаунт, то вам нужно:'

                '-Выйти из старого аккаунта'

                '-Закрыть сайт'

                '-Снова открыть сайт через кнопку в боте'

                '-Пройти регистрцию с указанием промокода MinesCrazy '

                '‼️После успешной регистрации, бот автоматически отправит вам уведомление об успешной синхронизации!'
            ),
            parse_mode='html',
            reply_markup=kb.reg
        )

# Обработка кнопки "Регистрация прошла успешно"
@router1.callback_query(F.data == 'yes')
async def yes_reg(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    if await check_registration(user_id):
        with open('success.jpg', 'rb') as photo:
            await callback.message.answer_photo(
                FSInputFile('success.jpg'),
                caption=(
                    "✅ Вы успешно завершили регистрацию. Ваш аккаунт синхронизирован с ботом.\n\n"
                    "🌐Шаг 2 - Внеси первый депозит\n\n"
                    "⚪Чтобы бот открыл вам доступ к сигналам, пополните свой счет (сделайте депозит) любым удобным вам способом.\n\n"
                    "🌟*Чем больше депозит, тем больше УРОВЕНЬ в боте, а чем больше уровень в боте, тем большее количество сигналов с высокой вероятностью проходимости сигнала ты будешь получать.*\n\n"
                    "‼️После пополнения первого депозита, Вам автоматически придет уведомление в бота и откроется доступ к сигналам."
                ),
                parse_mode='Markdown',
                reply_markup=kb.regget
            )
    else:
        await callback.answer("❌ Вы не зарегистрированы! Пожалуйста, зарегистрируйтесь по ссылке.", show_alert=True)


# Обработка кнопки "Игры"
@router1.callback_query(F.data == 'play')
async def games(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    if await check_registration(user_id):
        with open('start.jpg', 'rb') as photo:
            await callback.message.delete()
            await callback.message.answer_photo(
                FSInputFile('start.jpg'),
                caption='Выберите игру:',
                parse_mode='html',
                reply_markup=kb.games
            )
    else:
        await callback.answer("❌ Вы не зарегистрированы! Пожалуйста, зарегистрируйтесь.", show_alert=True)

# Обработка кнопки "Назад"
@router1.callback_query(F.data == 'back')
async def back(callback: CallbackQuery):
    with open('start.jpg', 'rb') as photo:
        await callback.message.delete()
        await callback.message.answer_photo(
            FSInputFile('start.jpg'),
            caption='🕹 Вы попали в главное меню:',
            parse_mode='html',
            reply_markup=kb.regget
        )

# Команда /admin
@router1.message(Command('admin'))
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer('💻 Панель администратора: ', reply_markup=kb.admin_panel)
    else:
        await message.answer('❌ У вас нет доступа!')

# Обработка кнопки "Рассылка"
@router1.callback_query(F.data == 'spam')
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите сообщение для рассылки: ')
    await state.set_state(SpamState.message)

# Обработка сообщения для рассылки
@router1.message(SpamState.message)
async def spam_go(message: Message, state: FSMContext, bot: Bot):
    spam_text = message.text
    users = get_all_users()
    try:
        for user_id in users:
            await bot.send_message(user_id, spam_text)
        await message.answer("✅ Рассылка завершена!", reply_markup=kb.admin_panel)
    except Exception as e:
        await message.answer(f"Ошибка во время рассылки: {e}")
    finally:
        await state.clear()

# Обработка кнопки "Статистика"
@router1.callback_query(F.data == 'stat')
async def users_handler(callback: CallbackQuery):
    if callback.from_user.id == ADMIN_ID:
        total_users = len(get_all_users())
        await callback.message.edit_text(f"📊 Кол-во пользователей: {total_users}", reply_markup=kb.stat)
    else:
        await callback.answer("❌ У вас нет доступа.", show_alert=True)

# Обработка кнопки "Назад" в админке
@router1.callback_query(F.data == 'back_admin')
async def back_admin(callback: CallbackQuery):
    await callback.message.edit_text('💻 Панель администратора: ', reply_markup=kb.admin_panel)
