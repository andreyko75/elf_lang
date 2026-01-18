# Developer Guide — Elenya Bot

Руководство для разработчиков и расширения функционала.

## Быстрые команды

### Разработка

```bash
# Активировать окружение
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Проверить настройку
python test_setup.py

# Запустить бота
python bot.py

# Остановить бота
Ctrl+C
```

### Очистка

```bash
# Очистить кеш Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Очистить ChromaDB (при необходимости)
rm -rf chroma/

# Очистить временные файлы
rm -rf /tmp/voice_* /tmp/photo_*
```

## Добавление нового функционала

### 1. Новый тип сообщений

**Пример: Обработка документов**

1. Создайте handler:

```python
# handlers/document.py
from telegram import Update
from telegram.ext import ContextTypes

async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик документов"""
    document = update.message.document
    # ... ваша логика
    await update.message.reply_text("Документ получен!")
```

2. Зарегистрируйте в `bot.py`:

```python
from handlers import document

application.add_handler(MessageHandler(filters.Document.ALL, document.document_handler))
```

### 2. Новый режим работы

**Пример: Режим "Обучение"**

1. Добавьте режим в `services/mode_manager.py`:

```python
class ModeManager:
    DICTIONARY_MODE = "dictionary"
    FREE_MODE = "free"
    LEARNING_MODE = "learning"  # новый режим
```

2. Обновите логику в `services/router.py`:

```python
def translate(self, text, use_dictionary=True, learning_mode=False):
    if learning_mode:
        # особая логика для режима обучения
        pass
```

3. Добавьте кнопку в `handlers/start.py`:

```python
keyboard = [
    [InlineKeyboardButton("Режим обучения", callback_data="mode_learning")]
]
```

### 3. Новая утилита

**Пример: Text-to-Speech**

1. Создайте файл `utils/tts.py`:

```python
from openai import OpenAI
import config

class TextToSpeech:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def synthesize(self, text: str, voice: str = "alloy") -> bytes:
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        return response.content
```

2. Используйте в handler:

```python
from utils.tts import TextToSpeech

tts = TextToSpeech()
audio_data = tts.synthesize("Привет!")
# Отправить audio_data пользователю
```

## Структура кода

### Naming conventions

```python
# Классы: PascalCase
class ModeManager:
    pass

# Функции и методы: snake_case
def translate_text():
    pass

# Константы: UPPER_SNAKE_CASE
TELEGRAM_TOKEN = "..."

# Приватные методы: _snake_case
def _build_prompt():
    pass
```

### Docstrings

```python
def translate(text: str, use_dictionary: bool = True) -> tuple[str, bool]:
    """
    Переводит текст с/на Elenya
    
    Args:
        text: Текст для перевода
        use_dictionary: Использовать ли словарь
        
    Returns:
        Tuple: (ответ бота, найдено ли в словаре)
    """
    pass
```

### Type hints

```python
from typing import Optional, List, Dict

def search(query: str, k: int = 3) -> tuple[List[str], bool]:
    pass

def get_mode(chat_id: int) -> Optional[str]:
    pass
```

## Debugging

### Логирование

Добавьте в начало файла:

```python
import logging
logger = logging.getLogger(__name__)

# В коде
logger.info("Обработка сообщения")
logger.error(f"Ошибка: {e}")
logger.debug(f"Данные: {data}")
```

### Уровни логов в bot.py

```python
# Для разработки
logging.basicConfig(level=logging.DEBUG)

# Для продакшна
logging.basicConfig(level=logging.INFO)
```

### Print debugging

```python
# Временный дебаг
print(f"🔍 DEBUG: {variable}")

# Удалить перед коммитом!
```

## Тестирование

### Ручное тестирование

Создайте тестового бота через @BotFather и используйте отдельный токен в `.env`:

```env
TELEGRAM_TOKEN=TEST_BOT_TOKEN_HERE
```

### Unit тесты (будущее расширение)

```python
# tests/test_mode_manager.py
import pytest
from services.mode_manager import ModeManager

def test_set_mode():
    manager = ModeManager()
    manager.set_mode(123, ModeManager.DICTIONARY_MODE)
    assert manager.get_mode(123) == ModeManager.DICTIONARY_MODE
```

### Тестовые данные

```python
# Тестовые chat_id
TEST_CHAT_ID = 999999

# Тестовые тексты
TEST_TEXTS = [
    "звезда",
    "elen",
    "sela-lin",
]
```

## Работа с RAG

### Изменение размера чанков

В `rag/loader.py`:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # увеличить для больших контекстов
    chunk_overlap=50,    # увеличить для лучшей связности
)
```

### Изменение количества результатов

В `rag/query.py`:

```python
def search(self, query: str, k: int = 3):  # изменить k
    results = self.vectorstore.similarity_search_with_score(query, k=k)
```

### Порог релевантности

```python
# В rag/query.py
if score < 1.5:  # уменьшить для более строгого отбора
    relevant_results.append(doc.page_content)
```

## Работа с OpenAI API

### Изменение модели

В `config.py`:

```python
# Для GPT-4
OPENAI_MODEL = "gpt-4-turbo"

# Для экономии (GPT-3.5)
OPENAI_MODEL = "gpt-3.5-turbo"

# Для больших контекстов
OPENAI_MODEL = "gpt-4-turbo-preview"
```

### Параметры генерации

В `services/router.py`:

```python
response = self.client.chat.completions.create(
    model=config.OPENAI_MODEL,
    temperature=0.7,      # креативность (0-2)
    max_tokens=500,       # макс. длина ответа
    top_p=1.0,            # nucleus sampling
    frequency_penalty=0,  # штраф за повторы
    presence_penalty=0,   # штраф за новые темы
)
```

### Обработка ошибок API

```python
from openai import OpenAIError, RateLimitError

try:
    response = self.client.chat.completions.create(...)
except RateLimitError:
    # Превышен лимит запросов
    await update.message.reply_text("Слишком много запросов. Подождите.")
except OpenAIError as e:
    # Другие ошибки API
    logger.error(f"OpenAI error: {e}")
```

## Работа с Telegram API

### Форматирование сообщений

```python
# Markdown
await update.message.reply_text(
    "*жирный* _курсив_ `код`",
    parse_mode="Markdown"
)

# HTML
await update.message.reply_text(
    "<b>жирный</b> <i>курсив</i> <code>код</code>",
    parse_mode="HTML"
)
```

### Inline кнопки

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = [
    [InlineKeyboardButton("Кнопка 1", callback_data="data1")],
    [InlineKeyboardButton("Кнопка 2", callback_data="data2")]
]
reply_markup = InlineKeyboardMarkup(keyboard)

await update.message.reply_text("Выбери:", reply_markup=reply_markup)
```

### Reply клавиатура

```python
from telegram import ReplyKeyboardMarkup

keyboard = [
    ["Вариант 1", "Вариант 2"],
    ["Вариант 3"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

await update.message.reply_text("Выбери:", reply_markup=reply_markup)
```

## Performance оптимизация

### Кэширование

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_operation(param: str) -> str:
    # Результат будет закэширован
    return result
```

### Асинхронность

Все handlers уже асинхронные (`async/await`).

### Батчинг запросов

```python
# Вместо множества запросов
for text in texts:
    result = await translate(text)

# Сделать один запрос с несколькими текстами
results = await translate_batch(texts)
```

## Деплой

### Переменные окружения в продакшне

```bash
# Не используйте .env в продакшне!
export TELEGRAM_TOKEN="..."
export OPENAI_API_KEY="..."

python bot.py
```

### Systemd service (Linux)

```ini
# /etc/systemd/system/elenya-bot.service
[Unit]
Description=Elenya Telegram Bot
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/path/to/elf_lang
Environment="TELEGRAM_TOKEN=..."
Environment="OPENAI_API_KEY=..."
ExecStart=/path/to/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker (будущее)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

## Чеклист перед коммитом

- [ ] Код проходит `python test_setup.py`
- [ ] Удалены print-дебаги
- [ ] Добавлены docstrings для новых функций
- [ ] Обновлен README (если нужно)
- [ ] Проверен .gitignore для новых файлов
- [ ] Нет хардкода секретов

## Полезные ссылки

- [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- [OpenAI API docs](https://platform.openai.com/docs)
- [LangChain docs](https://python.langchain.com/docs)
- [ChromaDB docs](https://docs.trychroma.com/)

---

Happy coding! 🚀
