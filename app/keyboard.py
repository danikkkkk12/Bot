from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import *

# Клавиатура для регистрации
reg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📝 Регистрация', url=REF)],
    [InlineKeyboardButton(text='🆘 Помощь', url=SUPPORT_LINK)]
])

# Клавиатура для депозита после регистрации
deposit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💸 Депозит', url=DEPOSIT_LINK)],
    [InlineKeyboardButton(text='🆘 Помощь', url=SUPPORT_LINK)]
])

# Главное меню после депозита
regget = InlineKeyboardMarkup(inline_keyboard=[ 
    [InlineKeyboardButton(text='💣 Получить сигнал', callback_data='play')],
    [InlineKeyboardButton(text='📌 О боте', callback_data='info'), InlineKeyboardButton(text='🎙 Канал', url=CHANNEL)]
])

# Меню для владельца
owner = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💣 Получить сигнал', callback_data='play')],
    [InlineKeyboardButton(text='📌 О боте', callback_data='info'), InlineKeyboardButton(text='🎙 Канал', url=CHANNEL)],
    [InlineKeyboardButton(text='💻 Панель администратора', callback_data='admin_panel')]
])

# Игры
games = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🚀 LuckyJet', web_app=WebAppInfo(url='https://volneer.github.io/jea/')), 
     InlineKeyboardButton(text='✈️ Aviator', web_app=WebAppInfo(url='https://volneer.github.io/avai/'))],
    [InlineKeyboardButton(text='💣 Mines', web_app=WebAppInfo(url='https://onezelenka.github.io/Blume7Games/mines/')), 
     InlineKeyboardButton(text='👑 RoyalMines', web_app=WebAppInfo(url='https://volneer.github.io/raayl/'))],
    [InlineKeyboardButton(text='💸 Bombucks', web_app=WebAppInfo(url='https://volneer.github.io/bb/'))],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='back')]
])

# Сохранение настроек
save = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Сохранить', callback_data='save'), 
     InlineKeyboardButton(text='🔁 Изменить', callback_data='no_save')]
]) 

# Панель администратора
admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎙 Рассылка', callback_data='spam')],
    [InlineKeyboardButton(text='📊 Статистика', callback_data='stat')],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='back_admin')]
])

# Статистика
stat = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='back_admin')]
])

