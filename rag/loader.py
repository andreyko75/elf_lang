"""
Загрузка словаря Elenya в RAG систему
"""
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import config


class DictionaryLoader:
    """Загрузчик словаря в векторную базу данных"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config.OPENAI_API_KEY
        )
        self.vectorstore = None
        
    def load_dictionary(self):
        """Загружает словарь из PDF и создает векторное хранилище"""
        # Загружаем PDF
        loader = PyPDFLoader(config.DICTIONARY_PATH)
        documents = loader.load()
        
        # Разбиваем на чанки
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        splits = text_splitter.split_documents(documents)
        
        # Создаем векторное хранилище
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            collection_name="elenya_dictionary"
        )
        
        print(f"✅ Словарь загружен: {len(splits)} фрагментов")
        return self.vectorstore
    
    def get_vectorstore(self):
        """Возвращает векторное хранилище"""
        if self.vectorstore is None:
            self.load_dictionary()
        return self.vectorstore
