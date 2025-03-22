import os
import time
from flask import session
from openai import OpenAI
from dotenv import load_dotenv
from .utils import init_db, save_conversation, load_training_text

load_dotenv()

# Инициализация OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Загрузка и обрезка обучающего текста
TRAINING_TEXT = load_training_text()

# Безопасный системный промпт (до 3000 токенов!)
SYSTEM_PROMPT = f"""
Ты — ассистент клиники эстетической медицины IMPULS. Общайся дружелюбно, профессионально и естественно, как человек, используя стиль из текста ниже. Отвечай на вопросы, консультируй и собирай имя, email и телефон клиента. Используй смайлики 😊, избегай шаблонов и повторов.

---

{TRAINING_TEXT[:10000]}  # ограничим текст до безопасной длины

---

Если пользователь:
- Хочет узнать об услугах — объясни доступно, дружелюбно, предложи записаться
- Указывает проблему — предложи решение и консультацию
- Пишет грубости — ответь вежливо, но с уважением к себе
- Упоминает беременность — поздравь и предложи вернуться после родов
"""

class ImpulsAssistant:
    def __init__(self):
        session.setdefault('conversation_history', [{"role": "system", "content": SYSTEM_PROMPT}])
        session.setdefault('language', None)
        session.setdefault('session_id', str(time.time()))

    def save(self):
        session.modified = True

    def process_message(self, msg):
        hist = session['conversation_history']
        hist.append({"role": "user", "content": msg})

        # Используем только system + последние 19 сообщений
        messages_for_gpt = [hist[0]] + hist[-19:]

        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages_for_gpt,
                max_tokens=500,
                temperature=0.7
            )
            response = completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"GPT Error: {e}")
            response = "⚠️ Ошибка ответа от GPT. Попробуйте позже."

        # Сохраняем ответ и обновляем историю
        hist.append({"role": "assistant", "content": response})
        session['conversation_history'] = hist
        save_conversation(session['session_id'], msg, response)
        self.save()
        return response