"""
Обработчик текстовых сообщений
"""
from telegram import Update
from telegram.ext import ContextTypes
from services.router import OpenAIRouter
from services.mode_manager import ModeManager


# Глобальные объекты (будут инициализированы в bot.py)
router: OpenAIRouter = None
mode_manager: ModeManager = None


def set_dependencies(openai_router: OpenAIRouter, mode_mgr: ModeManager):
    """Устанавливает зависимости"""
    global router, mode_manager
    router = openai_router
    mode_manager = mode_mgr


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    chat_id = update.effective_chat.id
    user_text = update.message.text
    
    # Проверяем режим работы
    use_dictionary = mode_manager.is_dictionary_mode(chat_id)
    
    # Отправляем сообщение о начале обработки
    processing_msg = await update.message.reply_text("⏳ Ищу перевод...")
    
    # Получаем перевод через роутер
    answer, found_in_dictionary = router.translate(
        text=user_text,
        use_dictionary=use_dictionary
    )
    
    # Формируем финальный ответ
    final_answer = answer
    
    # Если используем словарь и слово не найдено - предупреждаем
    if use_dictionary and not found_in_dictionary:
        final_answer += "\n\n⚠️ Слово не найдено в словаре Elenya, перевод дан по общему контексту."
    
    # Удаляем сообщение о обработке и отправляем результат
    await processing_msg.delete()
    await update.message.reply_text(final_answer)
