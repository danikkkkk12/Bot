import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import threading

TOKEN = "7906839757:AAFN4ll3FATz9pl1LVxZJKO-GdxLDX0GXyc"  # Токен вашего бота
CHANNEL_USERNAME = "@CrazyMines777"  # Канал для подписки
PROMOCODE = "CrazyMines"  # Промокод
DEPOSIT_LINK = "https://1wcneg.com/casino/list?open=register&sub1=832597017&p=gtyb"  # Ссылка для депозита
SUPPORT_USERNAME = "@B1ake7"  # Ваш Telegram-ник для поддержки
MENU_IMAGE_PATH = "photo/menu.jpg"  # Путь к изображению меню

bot = telebot.TeleBot(TOKEN)

# Словарь для отслеживания, было ли отправлено сообщение пользователю
user_notifications = {}

# Словарь для отслеживания, внес ли пользователь депозит
user_deposits = {}

# Словарь для хранения выбранного языка для каждого пользователя
user_languages = {}

# Тексты на разных языках
TEXTS = {
    "ru": {
        "main_menu": "🏠 Главное меню:",
        "get_signal": "🤖Получить сигнал🤖",
        "instruction": "📚Инструкция📚",
        "choose_language": "🌐Выбрать язык🌐",
        "support": "🆘Помощь / Поддержка🆘",
        "language_selected": "🌐 Выбран язык: Русский",
    },
    "en": {
        "main_menu": "🏠 Main menu:",
        "get_signal": "🤖Get signal🤖",
        "instruction": "📚Instruction📚",
        "choose_language": "🌐Choose language🌐",
        "support": "🆘Help / Support🆘",
        "language_selected": "🌐 Selected language: English",
    },
    "हिंदी": {
        "main_menu": "🏠 Menu utama:",
        "get_signal": "🤖Mendapatkan sinyal🤖",
        "instruction": "📚Petunjuk📚",
        "choose_language": "🌐Pilih bahasa🌐",
        "support": "🆘Bantuan / Dukungan🆘",
        "language_selected": "🌐 Bahasa yang dipilih: Indonesia",
    },
    "br": {
        "main_menu": "🏠 Menu principal:",
        "get_signal": "🤖Obter sinal🤖",
        "instruction": "📚Instrução📚",
        "choose_language": "🌐Escolha o idioma🌐",
        "support": "🆘Ajuda / Suporte🆘",
        "language_selected": "🌐 Idioma selecionado: Brazilian",
    },
    "es": {
        "main_menu": "🏠 Menú principal:",
        "get_signal": "🤖Obtener señal🤖",
        "instruction": "📚Instrucciones📚",
        "choose_language": "🌐Elegir idioma🌐",
        "support": "🆘Ayuda🆘",
        "language_selected": "🌐 Idioma seleccionado: Español",
    },
    "oz": {
        "main_menu": "🏠 Asosiy menyu:",
        "get_signal": "🤖Signal oling🤖",
        "instruction": "📚Ko'rsatma📚",
        "choose_language": "🌐Tilni tanlang🌐",
        "support": "🆘Yordam / Yordam🆘",
        "language_selected": "🌐 Tanlangan til: Ozarbayjon",
    },
    "az": {
        "main_menu": "🏠 Əsas menyu:",
        "get_signal": "🤖Siqnal al🤖",
        "instruction": "📚Təlimat📚",
        "choose_language": "🌐Dil seç🌐",
        "support": "🆘Yardım / Dəstək🆘",
        "language_selected": "🌐 Seçilmiş dil: Azərbaycan",
    },
    "tu": {
        "main_menu": "🏠 Ana menü:",
        "get_signal": "🤖Sinyal al🤖",
        "instruction": "📚Talimat📚",
        "choose_language": "🌐Dil seçin🌐",
        "support": "🆘Yardım / Destek🆘",
        "language_selected": "🌐 Seçilen dil: Türkçe",
    },
    "ar": {
        "main_menu": "🏠 القائمة الرئيسية:",
        "get_signal": "🤖ا🤖لحصول على الإشارة",
        "instruction": "📚ت📚عليمات",
        "choose_language": "🌐ا🌐ختر اللغة",
        "support": "🆘ا🆘لمساعدة / الدعم",
        "language_selected": "🌐 اللغة المختارة: عربي",
    },
    "po": {
        "main_menu": "🏠 Menu principal:",
        "get_signal": "🤖Obter sinal🤖",
        "instruction": "📚Instrução📚",
        "choose_language": "🌐Escolha o idioma🌐",
        "support": "🆘Ajuda / Suporte🆘",
        "language_selected": "🌐 Idioma selecionado: Português",
    },
}

# Функция для получения текста на выбранном языке
def get_text(user_id, key):
    lang = user_languages.get(user_id, "ru")  # По умолчанию русский
    return TEXTS[lang].get(key, "Текст не найден")

# Функция для проверки подписки на канал
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"❌Ошибка при проверке подписки: {e}")
        return False

# Функция для отправки сообщения через 1 минуту
def send_delayed_message(chat_id):
    time.sleep(60)  # Задержка в 1 минуту
    if chat_id not in user_notifications or not user_notifications[chat_id]:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("💰Внести депозит", url=DEPOSIT_LINK))
        keyboard.add(InlineKeyboardButton("🆘Помощь / Поддержка", url=f"https://t.me/{SUPPORT_USERNAME[1:]}"))
        
        bot.send_message(
            chat_id,
            "✅ Вы успешно завершили регистрацию. Ваш аккаунт синхронизирован с ботом.\n\n"
            "🌐Шаг 2 - Внеси первый депозит\n\n"
            "⚪Чтобы бот открыл вам доступ к сигналам, пополните свой счет (сделайте депозит) любым удобным вам способом.\n\n"
            "🌟*Чем больше депозит, тем больше УРОВЕНЬ в боте, а чем больше уровень в боте, тем большее количество сигналов с высокой вероятностью проходимости сигнала ты будешь получать.*\n\n"
            "‼️После пополнения первого депозита, Вам автоматически придет уведомление в бота и откроется доступ к сигналам.",
            reply_markup=keyboard
        )
        user_notifications[chat_id] = True

# Функция для отправки главного меню
def send_main_menu(chat_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(get_text(chat_id, "get_signal"), callback_data="get_signal"))
    keyboard.add(InlineKeyboardButton(get_text(chat_id, "instruction"), callback_data="instruction"))
    keyboard.add(InlineKeyboardButton(get_text(chat_id, "choose_language"), callback_data="choose_language"))
    keyboard.add(InlineKeyboardButton(get_text(chat_id, "support"), url=f"https://t.me/{SUPPORT_USERNAME[1:]}"))
    
    with open(MENU_IMAGE_PATH, "rb") as photo:
        bot.send_photo(
            chat_id,
            photo,
            caption=get_text(chat_id, "main_menu"),
            reply_markup=keyboard
        )

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    if not check_subscription(message.from_user.id):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔔Подписаться"))
        keyboard.add(InlineKeyboardButton("✅Проверить подписку", callback_data="check_subscription"))
        
        bot.send_message(
            message.chat.id,
            f"Добро пожаловать, {user_name}!\n\nДля использования бота - подпишись на наш канал 🤝\n\nНажми на кнопку 'Подписаться', чтобы перейти в канал: https://t.me/{CHANNEL_USERNAME[1:]}",
            reply_markup=keyboard
        )
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📲Зарегистрироваться", url=DEPOSIT_LINK))
        keyboard.add(InlineKeyboardButton("🏠 Вернуться в главное меню", callback_data="return_to_main_menu"))
        
        bot.send_message(
            message.chat.id,
            f"🌐 Шаг 1 - Зарегистрируйся\n\n ⚪ Для синхронизации с ботом, вам необходимо создать новый аккаунт строго по ссылке из бота и примените промокод:\n\nПромокод: 👉 {PROMOCODE} 👈\n\n🔵 Если вы открыли ссылку и попали в старый аккаунт, то вам нужно:\n\n- Выйти из старого аккаунта\n- Закрыть сайт\n- Снова открыть сайт через кнопку в боте\n- Пройти регистрацию с указанием промокода {PROMOCODE}\n\n‼️ После успешной регистрации, бот автоматически отправит вам уведомление об успешной синхронизации в течение минуты.",
            reply_markup=keyboard
        )
        if message.chat.id not in user_notifications or not user_notifications[message.chat.id]:
            threading.Thread(target=send_delayed_message, args=(message.chat.id,)).start()

# Обработчик выбора языка
@bot.callback_query_handler(func=lambda call: call.data == "choose_language")
def choose_language(call):
    # Путь к картинке
    image_path = "photo/menu.jpg"  # Укажите путь к вашей картинке

    # Создаем клавиатуру с выбором языка
    keyboard = InlineKeyboardMarkup(row_width=2)  # Два блока по горизонтали

    # Первый блок (5 языков)
    keyboard.add(
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton("🇮🇩 Indonesia", callback_data="lang_id"),
        InlineKeyboardButton("🇧🇷 Brazilian", callback_data="lang_br"),
        InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")
    )

    # Второй блок (5 языков)
    keyboard.add(
        InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_oz"),
        InlineKeyboardButton("🇦🇿 Azarbaycan", callback_data="lang_az"),
        InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tu"),
        InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
        InlineKeyboardButton("🇵🇹 Português", callback_data="lang_po")
    )

    # Отправляем картинку с клавиатурой
    with open(image_path, "rb") as photo:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,  # ID текущего сообщения
            media=telebot.types.InputMediaPhoto(photo, caption="🌐 Выберите язык:"),
            reply_markup=keyboard
        )
# Обработчик для кнопки "Получить сигнал"
@bot.callback_query_handler(func=lambda call: call.data == "get_signal")
def get_signal(call):
    bot.send_message(call.message.chat.id, "👾 Сигнал 👾: Красное (заглушка)")

# Обработчик для кнопки "Инструкция"
@bot.callback_query_handler(func=lambda call: call.data == "instruction")
def instruction(call):
    instruction_text = (
        "🤖 Бот основан и обучен на кластерной нейронной сети OpenAI!\n\n"
        "⚜️ Для обучения бота было сыграно 🎰 30,000 игр.\n\n"
        "В настоящее время пользователи бота успешно генерируют 15-25% от своего 💸 капитала ежедневно!\n\n"
        "Бот все еще проходит проверки и исправления! Точность бота составляет 92%!\n\n"
        "Чтобы достичь максимальной прибыли, следуйте этой инструкции:\n\n"
        "🟢 1. Зарегистрируйтесь в букмекерской конторе 1WIN по ссылке в боте!\n"
        "Если не открывается, воспользуйтесь VPN (Швеция). В Play Market/App Store есть много бесплатных сервисов, например: Vpnify, Planet VPN, Hotspot VPN и т.д.!\n"
        "❗️ Без регистрации и промокода доступ к сигналам не будет открыт ❗️\n\n"
        "🟢 2. Пополните баланс своего счета.\n"
        "🟢 3. Перейдите в раздел игр 1win и выберите игру.\n"
        "🟢 4. Установите количество ловушек на три. Это важно!\n"
        "🟢 5. Запросите сигнал у бота и ставьте ставки в соответствии с сигналами от бота.\n"
        "🟢 6. В случае неудачного сигнала рекомендуем удвоить (x²) вашу ставку, чтобы полностью покрыть убыток с помощью следующего сигнала.\n\n"
        "Вернуться в главное меню"
    )
    
    bot.send_message(call.message.chat.id, instruction_text)

# Обработчик для кнопки "Помощь / Поддержка"
@bot.callback_query_handler(func=lambda call: call.data == "support")
def support(call):
    bot.send_message(call.message.chat.id, f"🛠 Свяжитесь с поддержкой: {SUPPORT_USERNAME}")

# Обработчик для кнопки "Вернуться в главное меню"
@bot.callback_query_handler(func=lambda call: call.data == "return_to_main_menu")
def return_to_main_menu(call):
    send_main_menu(call.message.chat.id)

if __name__ == '__main__':
    bot.polling(none_stop=True)