import os, sys, chromadb, hashlib
from pathlib import Path
from chromadb.utils import embedding_functions

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="nomic-embed-text",
)
client = chromadb.PersistentClient(path="./vector_db")
collection = client.get_or_create_collection("personal_knowledge", embedding_function=ollama_ef)

def ingest_file(filepath):
    content = Path(filepath).read_text(encoding='utf-8')
    doc_id = hashlib.md5(filepath.encode()).hexdigest()
    # 按段落切分（简易）
    chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 50]
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metas = [{"source": filepath, "chunk": i} for i in range(len(chunks))]
    collection.upsert(documents=chunks, ids=ids, metadatas=metas)
    print(f"✅ 已入库: {filepath} ({len(chunks)} chunks)")

# 批量入库
for root, _, files in os.walk("./knowledge"):
    for f in files:
        if f.endswith(('.md', '.txt')):
            ingest_file(os.path.join(root, f))
