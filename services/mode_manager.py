"""
Управление режимами работы бота (словарь / свободный режим)
"""
from typing import Dict


class ModeManager:
    """Менеджер режимов работы для каждого пользователя"""
    
    # Режимы работы
    DICTIONARY_MODE = "dictionary"
    FREE_MODE = "free"
    
    def __init__(self):
        # Хранилище режимов для каждого chat_id
        self.user_modes: Dict[int, str] = {}
    
    def set_mode(self, chat_id: int, mode: str):
        """Устанавливает режим для пользователя"""
        if mode not in [self.DICTIONARY_MODE, self.FREE_MODE]:
            raise ValueError(f"Неизвестный режим: {mode}")
        
        self.user_modes[chat_id] = mode
        print(f"📋 Пользователь {chat_id}: режим установлен на {mode}")
    
    def get_mode(self, chat_id: int) -> str:
        """Получает текущий режим пользователя"""
        # По умолчанию - режим словаря
        return self.user_modes.get(chat_id, self.DICTIONARY_MODE)
    
    def is_dictionary_mode(self, chat_id: int) -> bool:
        """Проверяет, использует ли пользователь режим словаря"""
        return self.get_mode(chat_id) == self.DICTIONARY_MODE
    
    def toggle_mode(self, chat_id: int) -> str:
        """Переключает режим и возвращает новый"""
        current_mode = self.get_mode(chat_id)
        new_mode = self.FREE_MODE if current_mode == self.DICTIONARY_MODE else self.DICTIONARY_MODE
        self.set_mode(chat_id, new_mode)
        return new_mode
    
    def get_mode_name(self, mode: str) -> str:
        """Возвращает человекочитаемое название режима"""
        if mode == self.DICTIONARY_MODE:
            return "Словарь Elenya"
        elif mode == self.FREE_MODE:
            return "Свободный режим"
        return "Неизвестный режим"
