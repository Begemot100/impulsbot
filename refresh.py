import requests
import json
import os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
load_dotenv()

# 🔐 Данные интеграции
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
AUTH_CODE = os.getenv('AUTH_CODE')
TOKEN_PATH = os.getenv('TOKEN_PATH', 'amo_tokens.json')

# 💾 Сохраняем токены в файл
def save_tokens(data):
    with open(TOKEN_PATH, 'w') as f:
        json.dump(data, f)

# 📦 Загружаем токены из файла
def load_tokens():
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as f:
            return json.load(f)
    return None

# 🆕 Получение нового токена по коду авторизации
def get_new_token():
    url = 'https://tech241224.amocrm.ru/oauth2/access_token'
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': AUTH_CODE,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        tokens = response.json()
        save_tokens(tokens)
        print(f"✅ Получен новый access_token в {datetime.now()}")
    else:
        print(f"❌ Ошибка при получении токена: {response.status_code} - {response.text}")

# 🔁 Обновление токена по refresh_token
def refresh_token():
    tokens = load_tokens()
    if not tokens:
        print("⚠️ Токенов нет — получаем новый")
        get_new_token()
        return

    url = 'https://tech241224.amocrm.ru/oauth2/access_token'
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': tokens['refresh_token'],
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        new_tokens = response.json()
        save_tokens(new_tokens)
        print(f"🔁 Токен успешно обновлён в {datetime.now()}")
    else:
        print(f"❌ Ошибка обновления токена: {response.status_code} - {response.text}")

# ⏰ Планировщик для запуска обновления каждый час
if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(refresh_token, 'interval', hours=1)  # обновлять раз в час
    print("🕒 Запущен автообновлятор токена AmoCRM")
    refresh_token()  # запуск сразу при старте
    scheduler.start()