"""
Обработчик голосовых сообщений
"""
from telegram import Update
from telegram.ext import ContextTypes
import os
from services.router import OpenAIRouter
from services.mode_manager import ModeManager
from utils.stt import SpeechToText


# Глобальные объекты (будут инициализированы в bot.py)
router: OpenAIRouter = None
mode_manager: ModeManager = None
stt_processor: SpeechToText = None


def set_dependencies(openai_router: OpenAIRouter, mode_mgr: ModeManager, stt: SpeechToText):
    """Устанавливает зависимости"""
    global router, mode_manager, stt_processor
    router = openai_router
    mode_manager = mode_mgr
    stt_processor = stt


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик голосовых сообщений"""
    chat_id = update.effective_chat.id
    
    # Отправляем сообщение о начале обработки
    processing_msg = await update.message.reply_text("🎤 Распознаю голосовое сообщение...")
    
    try:
        # Получаем файл голосового сообщения
        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)
        
        # Сохраняем временно
        temp_path = f"/tmp/voice_{chat_id}_{voice.file_id}.ogg"
        await voice_file.download_to_drive(temp_path)
        
        # Распознаем речь
        recognized_text = stt_processor.transcribe(temp_path)
        
        # Удаляем временный файл
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if not recognized_text:
            await processing_msg.edit_text("❌ Не удалось распознать речь. Попробуй еще раз.")
            return
        
        # Показываем распознанный текст
        await processing_msg.edit_text(f"📝 Распознано: {recognized_text}\n\n⏳ Ищу перевод...")
        
        # Проверяем режим работы
        use_dictionary = mode_manager.is_dictionary_mode(chat_id)
        
        # Получаем перевод через роутер
        answer, found_in_dictionary = router.translate(
            text=recognized_text,
            use_dictionary=use_dictionary
        )
        
        # Формируем финальный ответ
        final_answer = f"📝 Распознано: {recognized_text}\n\n{answer}"
        
        # Если используем словарь и слово не найдено - предупреждаем
        if use_dictionary and not found_in_dictionary:
            final_answer += "\n\n⚠️ Слово не найдено в словаре Elenya, перевод дан по общему контексту."
        
        # Отправляем результат
        await processing_msg.delete()
        await update.message.reply_text(final_answer)
        
    except Exception as e:
        print(f"❌ Ошибка обработки голосового сообщения: {e}")
        await processing_msg.edit_text("❌ Произошла ошибка при обработке голосового сообщения.")
