"""
Обработка изображений через OpenAI Vision API
"""
from openai import OpenAI
import base64
import config


class VisionProcessor:
    """Класс для анализа изображений и определения объектов"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def analyze_image(self, image_path: str) -> str:
        """
        Анализирует изображение и определяет, что на нем изображено
        
        Args:
            image_path: Путь к файлу изображения
            
        Returns:
            Описание объекта на изображении (одним словом или короткой фразой)
        """
        try:
            # Читаем и кодируем изображение
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Отправляем запрос к Vision API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Определи, что изображено на картинке. Ответь одним словом или короткой фразой (максимум 2-3 слова). Это должен быть конкретный объект, предмет, природное явление или существо."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=50
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Ошибка анализа изображения: {e}")
            return ""
