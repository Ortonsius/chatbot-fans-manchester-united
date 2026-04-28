from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from ollama import Client

client = QdrantClient("http://localhost:6333")
ollama_client = Client(host='http://localhost:11434')

COLLECTION_NAME = "knowledge"
EMBED_MODEL = "nomic-embed-text-v2-moe"
VECTOR_SIZE = 768
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks

with open("information.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

chunks = chunk_text(raw_text, CHUNK_SIZE, CHUNK_OVERLAP)
print(f"Created {len(chunks)} chunks")

points = []
for idx, chunk in enumerate(chunks):
    if not chunk:
        continue
    response = ollama_client.embeddings(model=EMBED_MODEL, prompt=chunk)
    embedding = response["embedding"]
    points.append(PointStruct(id=idx, vector=embedding, payload={"text": chunk}))

client.upsert(collection_name=COLLECTION_NAME, points=points)
print("Ingestion complete.")