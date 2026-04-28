# Chatbot fans MU 😂
## Requirement
Sebelum menjalankan botnya, install library python dengan cara berikut:
```
pip install -r requirements.txt
```
Kemudian perlu install software external yaitu Ollama dan qdrant.
Secara default model AI yang digunakan adalah nomic-embed-text-v2-moe dan qwen3.5 9b.
Download model nomic menggunakan ollama:
```
ollama pull nomic-embed-text-v2-moe
```
Download model qwen menggunakan ollama:
```
ollama pull qwen3.5:9b-q8_0
```

## Cara pakai
### 1. Cari informasi tentang MU
Informasi tentang MU sudah disediakan secara default di file information.txt, tapi kalau melakukan perubahan ada penambahan silahkan file information.txt-nya diupdate.
### 2. Jalankan ingest.py
Jalankan script ini untuk memasukan data di information.txt ke dalam vector database.
```
python ingest.py
```
### 3. Telegram bot token
Perlu buat bot telegram dulu, dan masukan token botnya di file bot.py pada variable TELEGRAM_TOKEN.
### 4. Jalankan bot
Jalankan script botnya.
```
python bot.py
```
