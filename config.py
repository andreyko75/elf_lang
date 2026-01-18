"""
Конфигурация бота и загрузка переменных окружения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram (поддерживаем оба названия переменной)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4-turbo"  # используем gpt-4-turbo как актуальную версию

# Пути к файлам
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DICTIONARY_PATH = os.path.join(PROJECT_ROOT, "rag", "data", "elenya_dict.pdf")

# Проверка наличия токенов
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден в .env")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не найден в .env")
