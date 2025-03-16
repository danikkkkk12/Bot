from aiogram import types, Bot, F, Router
from aiogram.types import ChatMember
from config import CHANNEL_ID, CHANNEL_URL
import logging

# Логирование
logger = logging.getLogger(__name__)

router = Router()

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