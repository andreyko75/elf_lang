"""
Обработчик изображений
"""
from telegram import Update
from telegram.ext import ContextTypes
import os
from services.router import OpenAIRouter
from services.mode_manager import ModeManager
from utils.vision import VisionProcessor


# Глобальные объекты (будут инициализированы в bot.py)
router: OpenAIRouter = None
mode_manager: ModeManager = None
vision_processor: VisionProcessor = None


def set_dependencies(
    openai_router: OpenAIRouter, 
    mode_mgr: ModeManager, 
    vision: VisionProcessor
):
    """Устанавливает зависимости"""
    global router, mode_manager, vision_processor
    router = openai_router
    mode_manager = mode_mgr
    vision_processor = vision


async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик изображений"""
    chat_id = update.effective_chat.id
    
    # Отправляем сообщение о начале обработки
    processing_msg = await update.message.reply_text("🖼 Анализирую изображение...")
    
    try:
        # Получаем файл изображения (самого большого размера)
        photo = update.message.photo[-1]  # берем самое большое разрешение
        photo_file = await context.bot.get_file(photo.file_id)
        
        # Сохраняем временно
        temp_path = f"/tmp/photo_{chat_id}_{photo.file_id}.jpg"
        await photo_file.download_to_drive(temp_path)
        
        # Анализируем изображение
        detected_object = vision_processor.analyze_image(temp_path)
        
        # Удаляем временный файл
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if not detected_object:
            await processing_msg.edit_text("❌ Не удалось определить объект на изображении.")
            return
        
        # Показываем что определили
        await processing_msg.edit_text(
            f"👁 Определено: {detected_object}\n\n⏳ Ищу перевод на Elenya..."
        )
        
        # Проверяем режим работы
        use_dictionary = mode_manager.is_dictionary_mode(chat_id)
        
        # Получаем перевод через роутер
        answer, found_in_dictionary = router.translate(
            text=detected_object,
            use_dictionary=use_dictionary,
            context=f"Это объект на изображении: {detected_object}"
        )
        
        # Формируем финальный ответ
        final_answer = f"👁 На изображении: {detected_object}\n\n{answer}"
        
        # Если используем словарь и слово не найдено - предупреждаем
        if use_dictionary and not found_in_dictionary:
            final_answer += "\n\n⚠️ Слово не найдено в словаре Elenya, перевод дан по общему контексту."
        
        # Отправляем результат
        await processing_msg.delete()
        await update.message.reply_text(final_answer)
        
    except Exception as e:
        print(f"❌ Ошибка обработки изображения: {e}")
        await processing_msg.edit_text("❌ Произошла ошибка при обработке изображения.")
