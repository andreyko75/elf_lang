"""
Поиск в словаре Elenya через RAG
"""
from typing import Optional, List


class DictionaryQuery:
    """Поиск слов и фраз в словаре"""
    
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        
    def search(self, query: str, k: int = 3) -> tuple[List[str], bool]:
        """
        Ищет информацию по запросу в словаре
        
        Args:
            query: Поисковый запрос (слово или фраза)
            k: Количество результатов
            
        Returns:
            Tuple: (список найденных фрагментов, флаг "найдено в словаре")
        """
        # Поиск по векторной базе
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        # Проверяем, есть ли релевантные результаты
        # Если score слишком большой (> 1.5), считаем что результат не релевантен
        relevant_results = []
        found_in_dictionary = False
        
        for doc, score in results:
            if score < 1.5:  # порог релевантности
                relevant_results.append(doc.page_content)
                found_in_dictionary = True
        
        return relevant_results, found_in_dictionary
    
    def format_context(self, results: List[str]) -> str:
        """Форматирует найденные результаты в контекст для LLM"""
        if not results:
            return ""
        
        context = "Информация из словаря Elenya:\n\n"
        for i, result in enumerate(results, 1):
            context += f"{result}\n\n"
        
        return context
