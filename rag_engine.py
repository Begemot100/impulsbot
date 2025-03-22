# rag_engine.py
import os
import openai
import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Используем локальную модель для эмбеддингов (или OpenAI ниже)
model = SentenceTransformer('all-MiniLM-L6-v2')  # можно заменить на OpenAI embeddings

# 1. Подготовка текстовых чанков
def split_text(text: str, max_words=300) -> List[str]:
    words = text.split()
    chunks = [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
    return chunks

# 2. Индексация в FAISS
def build_faiss_index(chunks: List[str]):
    embeddings = model.encode(chunks, show_progress_bar=True)
    dimension = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index, chunks, embeddings

# 3. Поиск по индексу
def search(query: str, index, chunks, k=3):
    query_vector = model.encode([query])
    D, I = index.search(np.array(query_vector), k)
    return [chunks[i] for i in I[0]]

# 4. Запрос к OpenAI с релевантным контекстом
def ask_gpt(query: str, context_chunks: List[str]) -> str:
    context = "\n\n".join(context_chunks)
    prompt = f"На основе следующего контекста ответь на вопрос:\n\n{context}\n\nВопрос: {query}\n\nОтвет:"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты ассистент клиники IMPULS."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

# Пример использования
if __name__ == "__main__":
    with open("combined_text.txt", "r") as f:
        raw_text = f.read()

    chunks = split_text(raw_text, max_words=300)
    index, chunk_store, _ = build_faiss_index(chunks)

    while True:
        user_q = input("Вопрос: ")
        relevant_chunks = search(user_q, index, chunk_store)
        answer = ask_gpt(user_q, relevant_chunks)
        print("\nОтвет:", answer)
        print("\n" + "=" * 50 + "\n")
