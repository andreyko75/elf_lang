"""
Speech-to-Text через OpenAI Whisper API
"""
from openai import OpenAI
import config


class SpeechToText:
    """Класс для распознавания речи из голосовых сообщений"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def transcribe(self, audio_file_path: str, language: str = "ru") -> str:
        """
        Распознает речь из аудиофайла
        
        Args:
            audio_file_path: Путь к аудиофайлу
            language: Язык распознавания (по умолчанию русский)
            
        Returns:
            Распознанный текст
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            return transcript.text
        except Exception as e:
            print(f"❌ Ошибка распознавания речи: {e}")
            return ""
