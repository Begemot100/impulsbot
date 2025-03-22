import os
import time
import re
from flask import session
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from .utils.utils import init_db, save_conversation, load_training_text
from .utils.amo_crm import create_lead
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate

load_dotenv()

# Инициализация OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Загрузка и обрезка обучающего текста
TRAINING_TEXT = load_training_text()

# Загрузка индекса
embedding_model = OpenAIEmbeddings()
db = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)

def query_with_context(user_question):
    docs = db.similarity_search(user_question, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""
    На основе следующего контекста ответь на вопрос пользователя. 
    Будь дружелюбным ассистентом клиники эстетической медицины IMPULS.

    Контекст:
    {context}

    Вопрос:
    {user_question}

    Ответ:
    """
    return prompt

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
        session.setdefault('lead_sent', False)

    def save(self):
        session.modified = True

    def process_message(self, msg):
        hist = session['conversation_history']
        hist.append({"role": "user", "content": msg})
        messages_for_gpt = [hist[0]] + hist[-10:]

        try:
            prompt = query_with_context(msg)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages_for_gpt,
                max_tokens=200,
                temperature=0.3
            )
            usage = completion.usage
            print(
                f"📊 Токены: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")
            response = completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"GPT Error: {e}")
            response = "⚠️ Ошибка ответа от GPT. Попробуйте позже."

        # Проверка наличия контактов и создания лида в AmoCRM
        if not session.get("lead_sent"):
            email_match = re.search(r'\b[\w.-]+@[\w.-]+\.\w+\b', msg)
            phone_match = re.search(r'\b\d{7,15}\b', msg)
            name_match = re.search(r'\b([\u0410-\u042f\u0430-\u044fA-Z][\u0410-\u042f\u0430-\u044fA-Za-z]+)\b', msg)

            if email_match and phone_match and name_match:
                name = name_match.group()
                email = email_match.group()
                phone = phone_match.group()

                # 1. Собираем переписку
                conversation_log = "\n".join([
                    f"{'👩‍⚕️ Ассистент' if m['role'] == 'assistant' else '🧑 Клиент'}: {m['content']}"
                    for m in hist if m['role'] != 'system'
                ])

                # 2. Извлекаем тему обращения с помощью GPT
                try:
                    topic_prompt = f"""
                    Проанализируй следующий диалог с клиентом и определи КРАТКО, какая услуга или запрос его интересует, максимум 3-5 слов. 
                    Примеры: "удаление тату", "ботокс", "папиллома", "консультация косметолога", "запись на приём".

                    Диалог:
                    {conversation_log}
                    """
                    topic_completion = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system",
                             "content": "Ты — ассистент, который кратко формулирует причину обращения клиента по тексту."},
                            {"role": "user", "content": topic_prompt}
                        ],
                        max_tokens=20,
                        temperature=0.3
                    )
                    topic = topic_completion.choices[0].message.content.strip()
                except OpenAIError as e:
                    print("⚠️ GPT failed to extract topic:", e)
                    topic = "Причина обращения не определена"

                # 3. Полный текст для поля MESSAGE
                message_text = f"Обращение от {name}.\nПричина: {topic}.\n\nПереписка:\n{conversation_log}"

                # 4. Сохраняем файл при необходимости
                file_path = None
                if len(conversation_log.strip()) > 200:
                    os.makedirs("conversations", exist_ok=True)
                    file_name = f"chat_{int(time.time())}.txt"
                    file_path = os.path.join("conversations", file_name)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(conversation_log)

                # 5. Создание сделки в AmoCRM
                status, result = create_lead(
                    name=name,
                    phone=phone,
                    email=email,
                    message=message_text,
                    file_path=file_path
                )
                print(f"📩 AmoCRM: {status}, {result}")
                session['lead_sent'] = True

        # Сохраняем ответ и обновляем историю
        hist.append({"role": "assistant", "content": response})
        session['conversation_history'] = hist
        save_conversation(session['session_id'], msg, response)
        self.save()
        return response