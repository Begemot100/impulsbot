import requests
import json
import os

TOKEN_PATH = 'amo_tokens.json'

def load_tokens():
    with open(TOKEN_PATH, 'r') as f:
        return json.load(f)

def get_lead_custom_fields():
    tokens = load_tokens()
    access_token = tokens['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    url = 'https://tech241224.amocrm.ru/api/v4/leads/custom_fields'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        fields = response.json()['_embedded']['custom_fields']
        print("📋 Кастомные поля сделок:")
        for field in fields:
            print(f"- {field['name']} (field_id: {field['id']}, type: {field['type']})")
    else:
        print(f"❌ Ошибка: {response.status_code} - {response.text}")

# Вызов
get_lead_custom_fields()