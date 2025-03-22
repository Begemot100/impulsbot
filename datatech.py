import os
import docx2txt
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv

# 1. Загрузка переменных окружения
load_dotenv()

# 2. Путь к папке с документами
DATA_DIR = "/Users/germany/PycharmProjects/PythonProject/PythonProject7/data"

# 3. Загрузка и объединение текста из всех .docx файлов
all_text = ""
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".docx"):
        filepath = os.path.join(DATA_DIR, filename)
        print(f"\n📄 Чтение: {filename}")
        all_text += docx2txt.process(filepath) + "\n"

# 4. Разбиение текста на чанки
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_text(all_text)
print(f"\n📚 Получено чанков: {len(chunks)}")

# 5. Создание эмбеддингов и индексация в FAISS
embedding_model = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(chunks, embedding_model)

# 6. Сохранение индекса локально
vectorstore.save_local("faiss_index")
print("✅ Индекс сохранён в папку ./faiss_index")
