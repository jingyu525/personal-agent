# ~/personal-agent/mcp_kb_server.py
import sys, json, chromadb, os, logging, requests
from pathlib import Path
from chromadb.utils import embedding_functions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.resolve()
VECTOR_DB_PATH = os.environ.get("PERSONAL_AGENT_HOME", str(BASE_DIR))

OLLAMA_URL = "http://localhost:11434/api/embeddings"

def check_ollama_service():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

if not check_ollama_service():
    logger.error("Ollama 服务不可用，请确保 Ollama 正在运行 (http://localhost:11434)")
    print(json.dumps({"error": "Ollama 服务不可用，请启动 Ollama 服务"}))
    sys.stdout.flush()
    sys.exit(1)

try:
    ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        url=OLLAMA_URL,
        model_name="nomic-embed-text",
    )
    client = chromadb.PersistentClient(path=f"{VECTOR_DB_PATH}/vector_db")
    collection = client.get_or_create_collection("personal_knowledge", embedding_function=ollama_ef)
    logger.info("成功连接到向量数据库和 Ollama 服务")
except Exception as e:
    logger.error(f"初始化失败: {e}")
    print(json.dumps({"error": f"初始化失败: {e}"}))
    sys.stdout.flush()
    sys.exit(1)

def handle_request(req):
    method = req.get("method")
    logger.info(f"处理请求: {method}")

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
        try:
            query = req["params"]["arguments"]["query"]
            logger.info(f"搜索查询: {query}")
            results = collection.query(query_texts=[query], n_results=5)
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            output = "\n\n---\n\n".join(
                f"[来源: {m['source']}]\n{d}" for d, m in zip(docs, metas)
            )
            logger.info(f"搜索完成，返回 {len(docs)} 条结果")
            return {"content": [{"type": "text", "text": output}]}
        except KeyError as e:
            logger.error(f"请求参数缺失: {e}")
            return {"content": [{"type": "text", "text": f"错误: 缺少必要参数 {e}"}]}
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return {"content": [{"type": "text", "text": f"搜索失败: {e}"}]}

    return {"error": f"未知方法: {method}"}

for line in sys.stdin:
    try:
        req = json.loads(line)
        logger.debug(f"收到请求: {req}")
        res = handle_request(req)
        print(json.dumps({"id": req.get("id"), "result": res}))
        sys.stdout.flush()
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析错误: {e}, 原始输入: {line[:100]}")
        print(json.dumps({"error": f"JSON 解析错误: {e}"}))
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"处理请求时发生错误: {e}")
        print(json.dumps({"error": str(e)}))
        sys.stdout.flush()
