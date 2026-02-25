import sys, chromadb
from chromadb.utils import embedding_functions

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="nomic-embed-text",
)
client = chromadb.PersistentClient(path="./vector_db")
collection = client.get_or_create_collection("personal_knowledge", embedding_function=ollama_ef)

query = " ".join(sys.argv[1:])
results = collection.query(query_texts=[query], n_results=5)

for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    print(f"\n[{i+1}] 来源: {meta['source']}")
    print(doc[:300] + "...")
