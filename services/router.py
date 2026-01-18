"""
Роутер для маршрутизации запросов к OpenAI LLM
"""
from openai import OpenAI
from typing import Optional
import config
from rag.query import DictionaryQuery


class OpenAIRouter:
    """Роутер для обработки запросов через OpenAI"""
    
    def __init__(self, dictionary_query: Optional[DictionaryQuery] = None):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.dictionary_query = dictionary_query
    
    def translate(
        self, 
        text: str, 
        use_dictionary: bool = True,
        context: Optional[str] = None
    ) -> tuple[str, bool]:
        """
        Переводит текст с/на Elenya
        
        Args:
            text: Текст для перевода
            use_dictionary: Использовать ли словарь
            context: Дополнительный контекст (например, "это дерево" для изображения)
            
        Returns:
            Tuple: (ответ бота, найдено ли в словаре)
        """
        found_in_dictionary = False
        system_prompt = self._build_system_prompt(use_dictionary)
        
        # Если используем словарь, ищем в RAG
        rag_context = ""
        if use_dictionary and self.dictionary_query:
            search_results, found = self.dictionary_query.search(text, k=3)
            found_in_dictionary = found
            
            if found:
                rag_context = self.dictionary_query.format_context(search_results)
        
        # Формируем промпт для пользователя
        user_prompt = self._build_user_prompt(text, rag_context, context)
        
        # Запрос к OpenAI
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            return answer, found_in_dictionary
            
        except Exception as e:
            print(f"❌ Ошибка запроса к OpenAI: {e}")
            return "Произошла ошибка при обработке запроса.", False
    
    def _build_system_prompt(self, use_dictionary: bool) -> str:
        """Строит системный промпт"""
        base_prompt = """Ты — обучающий ассистент по эльфийскому языку Elenya.
Твоя задача — помогать изучать эльфийский язык.

ВАЖНО: Пользователи учат эльфийский язык!
- Если пользователь пишет на русском → дай перевод на Elenya
- Если пользователь пишет на Elenya → дай перевод на русский

Формат ответа:

Elenya: <слово на эльфийском>
Перевод: <перевод на русский>
Пояснение: <краткое пояснение о значении и использовании>

Будь лаконичен, но полезен. Используй поэтичный стиль, отражающий природу эльфийского языка."""
        
        if use_dictionary:
            base_prompt += """

ВАЖНО: Ты ДОЛЖЕН использовать информацию из словаря Elenya, если она предоставлена в контексте.
Если слово найдено в словаре — используй только эту информацию.
Если слово НЕ найдено в словаре — можешь использовать общие знания, но это будет указано отдельно."""
        
        return base_prompt
    
    def _build_user_prompt(
        self, 
        text: str, 
        rag_context: str, 
        additional_context: Optional[str]
    ) -> str:
        """Строит промпт пользователя"""
        prompt = ""
        
        if rag_context:
            prompt += f"{rag_context}\n\n"
        
        if additional_context:
            prompt += f"Контекст: {additional_context}\n\n"
        
        # Определяем язык и формируем запрос
        # Простая проверка: если есть кириллица — это русский, иначе Elenya
        is_russian = any('\u0400' <= char <= '\u04FF' for char in text)
        
        if is_russian:
            prompt += f"Пользователь написал на русском: \"{text}\"\nДай перевод на эльфийский язык Elenya."
        else:
            prompt += f"Пользователь написал на Elenya: \"{text}\"\nДай перевод на русский язык."
        
        return prompt
