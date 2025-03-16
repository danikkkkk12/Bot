from typing import Any
from aiogram.filters import BaseFilter
from aiogram import types, Bot, F, Router
from aiogram.types import ChatMember, InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_ID, CHANNEL_URL
import logging
import asyncio

# Логирование
logger = logging.getLogger(__name__)

# Создаём экземпляр Router
router = Router()

class ChatJoinFilter(BaseFilter):
    """
    Фильтр для проверки, подписан ли пользователь на канал.
    Если пользователь не подписан, отправляет сообщение с предложением подписаться.
    """
    async def __call__(self, message: types.Message, bot: Bot) -> Any:
        try:
            # Получаем информацию о пользователе в канале
            chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)

            # Проверяем статус пользователя
            if chat_member.status in [ChatMember.Status.MEMBER, ChatMember.Status.CREATOR, ChatMember.Status.ADMINISTRATOR]:
                return True

        except Exception as e:
            # Логируем ошибку, если что-то пошло не так
            logger.error(f"Ошибка при проверке участника канала: {e}")

        # Если пользователь не подписан, отправляем сообщение с предложением подписаться
        await message.answer(
            "Пожалуйста, подпишитесь на наш канал, чтобы продолжить.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Подписаться", url=CHANNEL_URL)]
            ])
        )
        return False

class RegisteredFilter(BaseFilter):
    """
    Фильтр для проверки, зарегистрирован ли пользователь в базе данных.
    Если пользователь не зарегистрирован, отправляет сообщение с предложением зарегистрироваться.
    """
    async def __call__(self, message: types.Message, bot: Bot) -> Any:
        try:
            # Проверяем, зарегистрирован ли пользователь в базе данных
            user = await DataBase.get_user(message.from_user.id)
            if user is not None:
                return True

        except Exception as e:
            # Логируем ошибку, если что-то пошло не так
            logger.error(f"Ошибка при проверке регистрации пользователя: {e}")

        # Если пользователь не зарегистрирован, отправляем сообщение с предложением зарегистрироваться
        await message.answer(
            "Пожалуйста, зарегистрируйтесь, чтобы продолжить.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Зарегистрироваться", callback_data="register")]
            ])
        )
        return False

# Обработчик для проверки подписки на канал
@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: types.CallbackQuery, bot: Bot):
    """
    Обработчик для проверки подписки пользователя на канал.
    Отправляет уведомление о статусе подписки.
    """
    try:
        # Добавляем небольшую задержку для обновления статуса
        await asyncio.sleep(2)  # Задержка 2 секунды

        # Проверяем статус подписки
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=callback.from_user.id)

        # Логируем статус подписки для отладки
        logger.info(f"Статус подписки пользователя {callback.from_user.id}: {chat_member.status}")

        # Проверяем, подписан ли пользователь
        if chat_member.status in [ChatMember.Status.MEMBER, ChatMember.Status.CREATOR, ChatMember.Status.ADMINISTRATOR]:
            await callback.answer("Вы подписаны на канал! 🎉", show_alert=True)
        else:
            # Если пользователь не подписан, отправляем сообщение с предложением подписаться
            await callback.answer("Вы ещё не подписались на канал. 😢", show_alert=True)
            await callback.message.answer(
                "Пожалуйста, подпишитесь на наш канал, чтобы продолжить.",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="Подписаться", url=CHANNEL_URL)]
                ])
            )
    except Exception as e:
        # Логируем ошибку, если что-то пошло не так
        logger.error(f"Ошибка при проверке подписки: {e}")
        await callback.answer("Произошла ошибка при проверке подписки. 😢", show_alert=True)