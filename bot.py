import asyncio
import logging
from collections import defaultdict
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from qdrant_client import QdrantClient
from ollama import Client

TELEGRAM_TOKEN = "<ISI SENDIRI>"
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "knowledge"
EMBED_MODEL = "nomic-embed-text-v2-moe"
LLM_MODEL = "qwen3.5:9b-q8_0"

SYSTEM_PROMPT = """Kamu adalah penggemar Manchester united garis keras.
Sifatmu adalah santai namun keras kepala.
Jawab user dengan tegas, tidak terlalu panjang, tidak basa-basi, bahasa yang tidak formal, santai dan gaul dalam bahasa Indonesia.
Tugasmu adalah menjawab semua respon user terkait dunia sepak bola.
Dilarang memberi jawaban diluar topic seputar sepak bola.
Jika user terindikasi menhina atau merendahkan Manchester united, kamu boleh menyerang, menghina dan menggunakan kata-kata kasa kepada user. Jangan biarkan user merendahkan Manchester united, gunakan segala cara untuk menyerang balik user yang merendahkan Manchester united. Gunakan amarahmu untuk membalas pesan user.
Jika user tidak terindikasi menhina atau merendahkan Manchester united, respon user dengan santai dan gaul.
Kamu diperbolehkan menggunakan kata-kata kasar untuk menjawab user.
"""

ollama_client = Client(host='http://localhost:11434')
qdrant = QdrantClient(url=QDRANT_URL)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

conversation_history = defaultdict(list)
MAX_HISTORY_LENGTH = 10

def rag_pipeline(user_id: int, question: str, top_k: int = 3) -> str:
    embed_resp = ollama_client.embeddings(model=EMBED_MODEL, prompt=question)
    query_vector = embed_resp["embedding"]
    search_result = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
    ).points
    retrieved_texts = [hit.payload["text"] for hit in search_result]
    context = "\n".join(retrieved_texts)

    # Start with system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    messages.append({
        "role": "system",
        "content": f"Konteks relevan (gunakan ini untuk menjawab):\n{context}"
    })

    history = conversation_history[user_id]
    messages.extend(history)

    messages.append({"role": "user", "content": question})

    response = ollama_client.chat(model=LLM_MODEL, messages=messages, think=False)
    answer = response["message"]["content"].strip()

    conversation_history[user_id].append({"role": "user", "content": question})
    conversation_history[user_id].append({"role": "assistant", "content": answer})

    if len(conversation_history[user_id]) > MAX_HISTORY_LENGTH:
        conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY_LENGTH:]

    return answer

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("P")
    await message.answer("knp?")

@dp.message(F.text)
async def handle_question(message: Message):
    user_id = message.from_user.id
    question = message.text.strip()

    try:
        answer = await asyncio.to_thread(rag_pipeline, user_id, question)
        if len(answer) > 4096:
            answer = answer[:4096] + "..."
        await message.answer(answer)
    except Exception as e:
        logging.exception("Error processing message")
        await message.answer("Sorry, something went wrong. Please try again later.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())