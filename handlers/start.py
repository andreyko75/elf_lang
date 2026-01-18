"""
Обработчик команды /start и выбора режима работы
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from services.mode_manager import ModeManager


# Глобальный менеджер режимов (будет инициализирован в bot.py)
mode_manager: ModeManager = None


def set_mode_manager(manager: ModeManager):
    """Устанавливает глобальный менеджер режимов"""
    global mode_manager
    mode_manager = manager


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_message = """✨ Добро пожаловать на путь изучения эльфийского языка Elenya.

Здесь слова звучат как шепот леса, а смысл рождается из света и тишины.

Ты можешь прислать:
• 📝 Текст — слово или фразу для перевода
• 🎤 Голосовое сообщение — я распознаю речь и переведу
• 🖼 Изображение — я определю объект и подберу слово на Elenya

Выбери, как мы будем работать дальше:"""
    
    # Создаем inline кнопки
    keyboard = [
        [InlineKeyboardButton("📚 Использовать словарь Elenya", callback_data="mode_dictionary")],
        [InlineKeyboardButton("🌟 Свободный режим (без словаря)", callback_data="mode_free")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /mode - переключение режима"""
    chat_id = update.effective_chat.id
    
    # Создаем inline кнопки для выбора режима
    keyboard = [
        [InlineKeyboardButton("📚 Использовать словарь Elenya", callback_data="mode_dictionary")],
        [InlineKeyboardButton("🌟 Свободный режим (без словаря)", callback_data="mode_free")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_mode = mode_manager.get_mode(chat_id)
    mode_name = mode_manager.get_mode_name(current_mode)
    
    await update.message.reply_text(
        f"Текущий режим: {mode_name}\n\nВыбери новый режим:",
        reply_markup=reply_markup
    )


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline кнопки"""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    data = query.data
    
    if data == "mode_dictionary":
        mode_manager.set_mode(chat_id, ModeManager.DICTIONARY_MODE)
        message = """✅ Выбран режим: Словарь Elenya

Я буду искать переводы в официальном словаре Elenya.
Если слово не найдено, я предупрежу тебя об этом.

Присылай слова, фразы, голосовые сообщения или изображения! 🌿"""
        
    elif data == "mode_free":
        mode_manager.set_mode(chat_id, ModeManager.FREE_MODE)
        message = """✅ Выбран свободный режим

Я буду использовать общие знания модели для перевода.
Переводы могут быть более креативными и гибкими.

Присылай слова, фразы, голосовые сообщения или изображения! ✨"""
    
    else:
        message = "Неизвестная команда"
    
    await query.edit_message_text(text=message)
