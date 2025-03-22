import requests
import json
import os

# Путь к токенам AmoCRM
TOKEN_PATH = 'amo_tokens.json'  # если файл в корне проекта

PIPELINE_ID = 9239766  # ваша ID воронки

def load_tokens():
    with open(TOKEN_PATH, 'r') as f:
        return json.load(f)

def get_pipeline_statuses():
    tokens = load_tokens()
    access_token = tokens['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    url = 'https://tech241224.amocrm.ru/api/v4/leads/pipelines'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        pipelines = response.json()['_embedded']['pipelines']
        for pipeline in pipelines:
            if pipeline['id'] == PIPELINE_ID:
                statuses = pipeline['_embedded']['statuses']
                print("📋 Статусы в воронке:")
                for status in statuses:
                    print(f"- {status['name']}: {status['id']}")
                return
        print("❌ Воронка не найдена")
    else:
        print(f"❌ Ошибка: {response.status_code} - {response.text}")

# Вызов
if __name__ == '__main__':
    get_pipeline_statuses()