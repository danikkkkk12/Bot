from typing import Any
from aiogram.filters import BaseFilter
from aiogram import types, Bot
from aiogram.types import ChatMemberStatus  # Импортируем ChatMemberStatus

from config import CHANNEL_ID
from database.db import DataBase


class ChatJoinFilter(BaseFilter):
    async def __call__(self, message: types.Message, bot: Bot) -> Any:
        try:
            # Получаем информацию о пользователе в канале
            chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)

            # Проверяем статус пользователя
            if chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
                return True

        except Exception as e:
            # Логируем ошибку, если что-то пошло не так
            print(f"Ошибка при проверке участника канала: {e}")

        return False


class RegisteredFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> Any:
        try:
            # Проверяем, зарегистрирован ли пользователь в базе данных
            user = await DataBase.get_user(message.from_user.id)
            return user is not None

        except Exception as e:
            # Логируем ошибку, если что-то пошло не так
            print(f"Ошибка при проверке регистрации пользователя: {e}")
            return False
