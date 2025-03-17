import sqlite3
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
import app.keyboard as kb
from aiogram.types import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import *
router1 = Router()

def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQU
        )
    ''')
    conn.commit()
    conn.close()

setup_database()

class spam(StatesGroup):
     message = State()

def add_user_all(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Пользователь {user_id} успешно добавлен."}
    except sqlite3.IntegrityError:
        conn.close()
        return {"status": "error", "message": f"Пользователь {user_id} уже существует."}
    except sqlite3.Error as e:
        conn.close()
        return {"status": "error", "message": f"Ошибка базы данных: {e}"}
    except Exception as e:
        conn.close()
        return {"status": "error", "message": f"Непредвиденная ошибка: {e}"}

def get_all_users_all():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users
    except sqlite3.OperationalError as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return []
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return []
    
def add_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Пользователь {user_id} успешно добавлен."}
    except sqlite3.IntegrityError:
        conn.close()
        return {"status": "error", "message": f"Пользователь {user_id} уже существует."}
    except sqlite3.Error as e:
        conn.close()
        return {"status": "error", "message": f"Ошибка базы данных: {e}"}
    except Exception as e:
        conn.close()
        return {"status": "error", "message": f"Непредвиденная ошибка: {e}"}


@router1.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    add_user(user_id) 
    with open('start.jpg', 'rb') as photo:
            await message.answer_photo(FSInputFile('start.jpg'),
                caption=f'Добро пожаловать в бота {NAME}!\n\nДля начала работы вам необходимо зарегистрировать новый аккаунт на 1win, чтобы бот выдавал верные сигналы! \n\nНажмите на кнопку "Регистрация" ниже, зарегистрируйте аккаунт и нажмите на кнопку "Готово"!',
                parse_mode='html',
                reply_markup=kb.reg
            )
    

@router1.callback_query(F.data == 'yes')
async def yes_reg(callback: CallbackQuery):
    with open('start.jpg', 'rb') as photo:
        await callback.message.answer_photo(FSInputFile('start.jpg'),
                    caption=f'✅ Регистрация прошла успешно! \n\n🕹 Вы попали в главное меню:',
                    parse_mode='html',
                    reply_markup=kb.regget
                    )               
        
            
@router1.callback_query(F.data == 'play')
async def games(callback: CallbackQuery):
    with open('start.jpg', 'rb') as photo:
            await callback.message.delete()
            await callback.message.answer_photo(FSInputFile('start.jpg'),
                caption=f'Выберите игру:',
                parse_mode='html',
                reply_markup=kb.games
                )
            
@router1.callback_query(F.data == 'back')
async def manual(callback: CallbackQuery):
    with open('start.jpg', 'rb') as photo:
            await callback.message.delete()
            await callback.message.answer_photo(FSInputFile('start.jpg'),
                caption=f'🕹 Вы попали в главное меню:',
                parse_mode='html',
                reply_markup=kb.regget
                )
            
@router1.message(Command('admin'))
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer('💻 Панель администратора: ', reply_markup=kb.admin_panel)
    else:
        await message.answer('❌ У вас нет доступа!')

@router1.callback_query(F.data == 'spam')
async def admin_panel(callback: CallbackQuery, state: FSMContext):
     await callback.message.edit_text('Введите сообщение для рассылки: ')
     await state.set_state(spam.message)

@router1.message(spam.message)
async def spam_go(message: Message, state: FSMContext, bot: Bot):
    spam_text = message.text
    users = get_all_users_all()
    try:
            for user_id in users:
                await bot.send_message(user_id, spam_text)
            await message.answer("✅ Рассылка завершена!", reply_markup=kb.admin_panel)
            await state.clear()
    except Exception as e:
            await message.answer(f"Ошибка во время рассылки: {e}")
            await state.clear()

@router1.callback_query(F.data == 'stat')
async def users_handler(callback: CallbackQuery):
    await callback.answer('')
    if callback.from_user.id == ADMIN_ID:
        total_users = len(get_all_users_all())
        await callback.message.edit_text(f"📊 Кол-во пользователей: {total_users}", reply_markup=kb.stat)
    else:
        await callback.answer("❌ У вас нет доступа.", show_alert=True)

@router1.callback_query(F.data == 'back_admin')
async def back_admin(callback: CallbackQuery):
    await callback.message.edit_text('💻 Панель администратора: ', reply_markup=kb.admin_panel)
