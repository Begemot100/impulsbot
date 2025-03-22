import json
import requests
import os
from datetime import datetime

# Путь к токенам AmoCRM
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '../../amo_tokens.json')

# ID воронки и стадии
PIPELINE_ID = 9239766  # Ваша воронка

DEFAULT_STATUS_ID = 74180478  # ID стадии "Первичный контакт"
def load_tokens():
    with open(TOKEN_PATH, 'r') as f:
        return json.load(f)

def get_field_id_by_name(field_name):
    tokens = load_tokens()
    access_token = tokens['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    url = 'https://tech241224.amocrm.ru/api/v4/leads/custom_fields'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        fields = response.json()['_embedded']['custom_fields']
        for field in fields:
            if field['name'].lower() == field_name.lower():
                return field['id']
        print(f"❌ Поле '{field_name}' не найдено.")
    else:
        print(f"❌ Ошибка получения полей: {response.status_code} - {response.text}")
    return None
print("🧪 Проверка контактов:")
print(f"Имя: {name}")
print(f"Email: {email}")
print(f"Телефон: {phone}")
print(f"Тема: {topic}")
print(f"Файл: {file_path}")

def create_lead(name, phone, email, message, file_path=None):
    tokens = load_tokens()
    access_token = tokens['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Получаем ID кастомного поля MESSAGE
    message_field_id = get_field_id_by_name("MESSAGE")
    if not message_field_id:
        print("❌ Поле MESSAGE не найдено.")
        return False, "MESSAGE field not found"

    # Подготовка данных сделки
    lead_data = {
        "name": f"Заявка от {name}",
        "pipeline_id": PIPELINE_ID,
        "status_id": DEFAULT_STATUS_ID,
        "created_at": int(datetime.now().timestamp()),
        "custom_fields_values": [
            {
                "field_id": message_field_id,
                "values": [{"value": message}]
            }
        ],
        "_embedded": {
            "contacts": [
                {
                    "name": name,
                    "custom_fields_values": [
                        {"field_code": "PHONE", "values": [{"value": phone}]},
                        {"field_code": "EMAIL", "values": [{"value": email}]}
                    ]
                }
            ]
        }
    }

    try:
        # 🔄 Создание сделки
        res = requests.post(
            'https://tech241224.amocrm.ru/api/v4/leads/complex',
            headers=headers,
            json=[lead_data]
        )

        if res.status_code == 200:
            lead = res.json()['_embedded']['leads'][0]  # ✅ берём первый лид
            lead_id = lead['id']
            print(f"✅ Сделка создана: ID {lead_id}")

            # 📎 Прикрепление файла, если есть
            if file_path and os.path.exists(file_path):
                files_url = f"https://tech241224.amocrm.ru/api/v4/leads/{lead_id}/files"
                file_name = os.path.basename(file_path)
                with open(file_path, 'rb') as f:
                    file_upload = {
                        "file": (file_name, f, "text/plain")
                    }
                    file_resp = requests.post(
                        files_url,
                        headers={'Authorization': f'Bearer {access_token}'},
                        files=file_upload
                    )
                    if file_resp.status_code == 200:
                        print("📎 Файл прикреплён к сделке")
                    else:
                        print(f"⚠️ Ошибка при прикреплении файла: {file_resp.status_code} - {file_resp.text}")

            return True, lead_id
        else:
            print(f"❌ Ошибка при создании сделки: {res.status_code} - {res.text}")
            return False, res.text

    except Exception as e:
        print(f"🚨 Исключение при создании сделки: {e}")
        return False, str(e)
