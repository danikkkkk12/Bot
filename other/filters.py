from typing import Any
from aiogram.filters import BaseFilter
from aiogram import types, Bot, F
from aiogram.types import ChatMember
from config import CHANNEL_ID
from database.db import DataBase

class ChatJoinFilter(BaseFilter):
    async def __call__(self, message: types.Message, bot: Bot) -> Any:
        try:
            # Получаем информацию о пользователе в канале
            chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)

            # Проверяем статус пользователя
            if chat_member.status in [ChatMember.Status.MEMBER, ChatMember.Status.CREATOR, ChatMember.Status.ADMINISTRATOR]:
                return True

        except Exception as e:
            # Логируем ошибку, если что-то пошло не так
            print(f"Ошибка при проверке участника канала: {e}")

        # Если пользователь не подписан, отправляем сообщение с предложением подписаться
        await message.answer(
            "Пожалуйста, подпишитесь на наш канал, чтобы продолжить.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Подписаться", url=f"https://t.me/{CHANNEL_ID}")]
            ])
        )
        return False

class RegisteredFilter(BaseFilter):
    async def __call__(self, message: types.Message, bot: Bot) -> Any:
        try:
            # Проверяем, зарегистрирован ли пользователь в базе данных
            user = await DataBase.get_user(message.from_user.id)
            if user is not None:
                return True

        except Exception as e:
            # Логируем ошибку, если что-то пошло не так
            print(f"Ошибка при проверке регистрации пользователя: {e}")

        # Если пользователь не зарегистрирован, отправляем сообщение с предложением зарегистрироваться
        await message.answer(
            "Пожалуйста, зарегистрируйтесь, чтобы продолжить.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Зарегистрироваться", callback_data="register")]
            ])
        )
        return False

@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: types.CallbackQuery, bot: Bot):
    try:
        # Проверяем статус подписки
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=callback.from_user.id)

        if chat_member.status in [ChatMember.Status.MEMBER, ChatMember.Status.CREATOR, ChatMember.Status.ADMINISTRATOR]:
            await callback.answer("Вы подписаны на канал! 🎉", show_alert=True)
        else:
            await callback.answer("Вы ещё не подписались на канал. 😢", show_alert=True)
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        await callback.answer("Произошла ошибка при проверке подписки. 😢", show_alert=True)