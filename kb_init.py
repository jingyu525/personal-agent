import chromadb
from chromadb.utils import embedding_functions

# 使用 Ollama 本地 Embedding
ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="nomic-embed-text",
)

client = chromadb.PersistentClient(path="./vector_db")
collection = client.get_or_create_collection(
    name="personal_knowledge",
    embedding_function=ollama_ef,
    metadata={"hnsw:space": "cosine"}
)

print("✅ 知识库初始化完成")
