"""
Главный файл Telegram-бота для изучения языка Elenya
"""
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# Импорты модулей проекта
import config
from services.mode_manager import ModeManager
from services.router import OpenAIRouter
from utils.stt import SpeechToText
from utils.vision import VisionProcessor
from rag.loader import DictionaryLoader
from rag.query import DictionaryQuery

# Импорты handlers
from handlers import start, text, voice, image


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Главная функция запуска бота"""
    
    print("🚀 Запуск бота Elenya...")
    
    # 1. Инициализация RAG системы
    print("📚 Загрузка словаря Elenya...")
    dictionary_loader = DictionaryLoader()
    vectorstore = dictionary_loader.load_dictionary()
    dictionary_query = DictionaryQuery(vectorstore)
    
    # 2. Инициализация сервисов
    print("⚙️  Инициализация сервисов...")
    mode_manager = ModeManager()
    router = OpenAIRouter(dictionary_query)
    stt = SpeechToText()
    vision = VisionProcessor()
    
    # 3. Передаем зависимости в handlers
    start.set_mode_manager(mode_manager)
    text.set_dependencies(router, mode_manager)
    voice.set_dependencies(router, mode_manager, stt)
    image.set_dependencies(router, mode_manager, vision)
    
    # 4. Создаем приложение
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # 5. Регистрируем handlers
    
    # Команды
    application.add_handler(CommandHandler("start", start.start_handler))
    application.add_handler(CommandHandler("mode", start.mode_handler))
    
    # Callback queries (нажатия на кнопки)
    application.add_handler(CallbackQueryHandler(start.callback_query_handler))
    
    # Голосовые сообщения
    application.add_handler(MessageHandler(filters.VOICE, voice.voice_handler))
    
    # Изображения
    application.add_handler(MessageHandler(filters.PHOTO, image.image_handler))
    
    # Текстовые сообщения (должны быть последними)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text.text_handler))
    
    # 6. Запуск бота
    print("✅ Бот запущен и готов к работе!")
    print("Нажмите Ctrl+C для остановки")
    
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        logger.exception("Критическая ошибка при запуске бота")
