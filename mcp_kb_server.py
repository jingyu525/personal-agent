# ~/personal-agent/mcp_kb_server.py
import sys, json, chromadb, os
from pathlib import Path
from chromadb.utils import embedding_functions

BASE_DIR = Path(__file__).parent.resolve()
VECTOR_DB_PATH = os.environ.get("PERSONAL_AGENT_HOME", str(BASE_DIR))

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="nomic-embed-text",
)
client = chromadb.PersistentClient(path=f"{VECTOR_DB_PATH}/vector_db")
collection = client.get_or_create_collection("personal_knowledge", embedding_function=ollama_ef)

def handle_request(req):
    method = req.get("method")

    if method == "tools/list":
        return {
            "tools": [{
                "name": "search_knowledge",
                "description": "在个人知识库中搜索相关内容",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"}
                    },
                    "required": ["query"]
                }
            }]
        }

    if method == "tools/call":
        query = req["params"]["arguments"]["query"]
        results = collection.query(query_texts=[query], n_results=5)
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        output = "\n\n---\n\n".join(
            f"[来源: {m['source']}]\n{d}" for d, m in zip(docs, metas)
        )
        return {"content": [{"type": "text", "text": output}]}

# MCP 标准 stdio 通信
for line in sys.stdin:
    try:
        req = json.loads(line)
        res = handle_request(req)
        print(json.dumps({"id": req.get("id"), "result": res}))
        sys.stdout.flush()
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.stdout.flush()
