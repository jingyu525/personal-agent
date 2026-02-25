import sys, chromadb, requests
from chromadb.utils import embedding_functions

def check_ollama_service():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.Timeout:
        return False
    except Exception:
        return False

def print_error(message):
    print(f"\n❌ 错误: {message}")
    sys.exit(1)

if not check_ollama_service():
    print_error("Ollama 服务不可用\n\n请确保 Ollama 正在运行:\n  1. 运行 'ollama serve' 启动服务\n  2. 或访问 https://ollama.ai 安装 Ollama")

try:
    ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="nomic-embed-text",
    )
    client = chromadb.PersistentClient(path="./vector_db")
    collection = client.get_or_create_collection("personal_knowledge", embedding_function=ollama_ef)
except Exception as e:
    print_error(f"初始化向量数据库失败: {e}")

if len(sys.argv) < 2:
    print_error("请提供搜索关键词\n\n用法: python search.py <搜索关键词>")

query = " ".join(sys.argv[1:])
print(f"\n🔍 搜索: {query}\n")

try:
    results = collection.query(query_texts=[query], n_results=5)
    
    if not results['documents'][0]:
        print("未找到相关结果")
        sys.exit(0)
    
    for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"[{i+1}] 来源: {meta['source']}")
        print(doc[:300] + "...")
except Exception as e:
    print_error(f"搜索失败: {e}")
