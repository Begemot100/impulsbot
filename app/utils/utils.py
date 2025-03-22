# app/utils.py
import sqlite3

def init_db():
    conn = sqlite3.connect("conversations.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_message TEXT,
            assistant_message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_conversation(session_id, user_message, assistant_message):
    conn = sqlite3.connect("conversations.db")
    c = conn.cursor()
    c.execute("INSERT INTO conversations (session_id, user_message, assistant_message) VALUES (?, ?, ?)",
              (session_id, user_message, assistant_message))
    conn.commit()
    conn.close()

def extract_client_data(message):
    name = None
    email = None
    phone = None

    if "@" in message:
        email = message.split("@")[0] + "@" + message.split("@")[1].split(" ")[0]

    digits = ''.join(filter(str.isdigit, message))
    if len(digits) >= 9:
        phone = digits

    words = message.split()
    if words:
        name = words[0].capitalize()

    return name, email, phone

def load_training_text():
    with open("training_data.txt", "r", encoding="utf-8") as file:
        return file.read()