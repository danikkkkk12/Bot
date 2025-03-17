from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import *

reg = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📝 Регистрация', url=REF)],
    [InlineKeyboardButton(text='✅ Готово', callback_data='yes')]
])

regget = InlineKeyboardMarkup(inline_keyboard=[ 
    [InlineKeyboardButton(text='💣 Получить сигнал', callback_data='play')],
    [InlineKeyboardButton(text='📌 О боте', callback_data='info'), InlineKeyboardButton(text='🎙 Канал', url=CHANNEL)]
])

owner = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💣 Получить сигнал', callback_data='play')],
    [InlineKeyboardButton(text='📌 О боте', callback_data='info'), InlineKeyboardButton(text='🎙 Канал', url=CHANNEL)],
    [InlineKeyboardButton(text='💻 Панель администратора', callback_data='admin_panel')]
])

games = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🚀 LuckyJet', web_app=WebAppInfo(url='https://volneer.github.io/jea/')), InlineKeyboardButton(text='✈️ Aviator', web_app=WebAppInfo(url='https://volneer.github.io/avai/'))],
    [InlineKeyboardButton(text='💣 Mines', web_app=WebAppInfo(url='https://onezelenka.github.io/Blume7Games/mines/')), InlineKeyboardButton(text='👑 RoyalMines', web_app=WebAppInfo(url='https://volneer.github.io/raayl/'))],
    [InlineKeyboardButton(text='💸 Bombucks', web_app=WebAppInfo(url='https://volneer.github.io/bb/'))],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='back')]
])

save = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Сохранить', callback_data='save'), InlineKeyboardButton(text='🔁 Изменить', callback_data='no_save')]
]) 

admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎙 Рассылка', callback_data='spam')],
    [InlineKeyboardButton(text='📊 Статистика', callback_data='stat')]
])

stat = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='back_admin')]
])