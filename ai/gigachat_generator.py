import requests
import os
import json
import uuid
from typing import List

class GigaChatGenerator:
    def __init__(self):
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self.credentials = os.getenv('GIGACHAT_CREDENTIALS')
        
        if not self.credentials:
            print("GigaChat: Не найден GIGACHAT_CREDENTIALS в .env файле")
        else:
            print(f"GigaChat: Ключ длиной {len(self.credentials)} символов")
        
    def _get_access_token(self):
        try:
            rquid = str(uuid.uuid4())
            print(f"RqUID: {rquid}")
            
            headers = {
                'Authorization': f'Basic {self.credentials}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': rquid
            }
            data = {'scope': 'GIGACHAT_API_PERS'}
            
            print("GigaChat: Получение токена...")
            response = requests.post(
                self.auth_url, 
                headers=headers, 
                data=data, 
                verify=False,
                timeout=30
            )
            
            print(f"GigaChat: Ответ сервера - {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data['access_token']
                expires_in = token_data.get('expires_in', 'N/A')
                print(f"GigaChat: Токен получен! Действует {expires_in} секунд")
                return token
            else:
                print(f"GigaChat Auth Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"GigaChat Auth Exception: {e}")
            return None
    
    def generate_script(self, category: str, count: int, total_errors: int, examples: List[str]) -> str:
        if not self.credentials:
            return self._get_fallback_solution(category, count, total_errors, examples)
        
        token = self._get_access_token()
        if not token:
            return self._get_fallback_solution(category, count, total_errors, examples)
        
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            prompt = self._build_prompt(category, count, total_errors, examples)
            
            data = {
                "model": "GigaChat",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Ты аналитик в телеком-компании. Анализируй ошибки робота в колл-центре. "
                            "Давай практические рекомендации как уменьшить количество ошибок. "
                            "Говори просто и понятно. Строго следуй формату ответа."
                        )
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            print(f"GigaChat: Генерация решения для '{category}'...")
            
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=data, 
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                print(f"GigaChat: Решение сгенерировано!")
                return ai_response
            else:
                error_msg = f"GigaChat API Error: {response.status_code}"
                print(error_msg)
                return self._get_fallback_solution(category, count, total_errors, examples)
                
        except Exception as e:
            error_msg = f"GigaChat Exception: {e}"
            print(error_msg)
            return self._get_fallback_solution(category, count, total_errors, examples)

    def _build_prompt(self, category: str, count: int, total_errors: int, examples: List[str]) -> str:
        examples_text = "\n".join([f"ДИАЛОГ {i+1}:\n{ex}\n" for i, ex in enumerate(examples)])
        
        return f"""
АНАЛИЗИРУЙ категорию ошибок и дай рекомендации.

КАТЕГОРИЯ ОШИБКИ: {category}
КОЛИЧЕСТВО СЛУЧАЕВ: {count} (из {total_errors} всего ошибок)

ДИАЛОГИ ДЛЯ АНАЛИЗА:
{examples_text}

ОТВЕТЬ СТРОГО В ЭТОМ ФОРМАТЕ:

КАТЕГОРИЯ: {category}
КОЛИЧЕСТВО ОШИБОК: {count}

ОСНОВНЫЕ ПРИЧИНЫ ОШИБКИ
[опиши 2-3 основные причины почему робот ошибается в этой категории]

РЕШЕНИЯ ДЛЯ ИСПРАВЛЕНИЯ  
[2-3 конкретных технических решения для исправления ошибок]

ОБЩИЕ РЕКОМЕНДАЦИИ
[2-3 общие рекомендации по улучшению работы робота для этой категории]

Отвечай кратко, по делу, без лишних слов. Фокус на практические решения.
"""

    def _get_fallback_solution(self, category: str, count: int, total_errors: int, examples: List[str]) -> str:
        return f"""
КАТЕГОРИЯ: {category}
КОЛИЧЕСТВО ОШИБОК: {count}

ОСНОВНЫЕ ПРИЧИНЫ ОШИБКИ
GigaChat временно недоступен для анализа конкретных причин.

РЕШЕНИЯ ДЛЯ ИСПРАВЛЕНИЯ
1. Провести ручной анализ {len(examples)} примеров диалогов
2. Разработать специфичные правила для категории "{category}"
3. Протестировать изменения на исторических данных

ОБЩИЕ РЕКОМЕНДАЦИИ
1. Увеличить порог уверенности для этой категории ошибок
2. Добавить дополнительные проверки в логику классификации
3. Регулярно мониторить эффективность исправлений
"""