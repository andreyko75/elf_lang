"""
Тестовый скрипт для проверки настройки проекта
"""
import sys
import os


def test_config():
    """Проверка конфигурации"""
    try:
        import config
        print("✅ Config загружен")
        
        if config.TELEGRAM_TOKEN:
            print("✅ Telegram токен найден")
        else:
            print("❌ Telegram токен не найден в .env")
            return False
            
        if config.OPENAI_API_KEY:
            print("✅ OpenAI ключ найден")
        else:
            print("❌ OpenAI ключ не найден в .env")
            return False
            
        if os.path.exists(config.DICTIONARY_PATH):
            print("✅ Словарь найден:", config.DICTIONARY_PATH)
        else:
            print("❌ Словарь не найден:", config.DICTIONARY_PATH)
            return False
            
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки config: {e}")
        return False


def test_imports():
    """Проверка импорта основных модулей"""
    modules = [
        "telegram",
        "openai",
        "langchain",
        "langchain_openai",
        "langchain_community",
        "chromadb",
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} не установлен")
            all_ok = False
    
    return all_ok


def test_project_structure():
    """Проверка структуры проекта"""
    required_files = [
        "bot.py",
        "config.py",
        "requirements.txt",
        "handlers/__init__.py",
        "handlers/start.py",
        "handlers/text.py",
        "handlers/voice.py",
        "handlers/image.py",
        "services/__init__.py",
        "services/router.py",
        "services/mode_manager.py",
        "utils/__init__.py",
        "utils/stt.py",
        "utils/vision.py",
        "rag/__init__.py",
        "rag/loader.py",
        "rag/query.py",
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} отсутствует")
            all_ok = False
    
    return all_ok


def main():
    """Главная функция проверки"""
    print("=" * 50)
    print("Проверка настройки Elenya Bot")
    print("=" * 50)
    
    print("\n1. Проверка конфигурации:")
    config_ok = test_config()
    
    print("\n2. Проверка зависимостей:")
    imports_ok = test_imports()
    
    print("\n3. Проверка структуры проекта:")
    structure_ok = test_project_structure()
    
    print("\n" + "=" * 50)
    if config_ok and imports_ok and structure_ok:
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("\nМожете запускать бота: python bot.py")
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ")
        print("\nИсправьте ошибки выше перед запуском бота")
        sys.exit(1)
    print("=" * 50)


if __name__ == "__main__":
    main()
