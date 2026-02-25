import os, sys, chromadb, hashlib, logging
from pathlib import Path
from chromadb.utils import embedding_functions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="nomic-embed-text",
    )
    client = chromadb.PersistentClient(path="./vector_db")
    collection = client.get_or_create_collection("personal_knowledge", embedding_function=ollama_ef)
except Exception as e:
    logger.error(f"初始化向量数据库失败: {e}")
    sys.exit(1)

def ingest_file(filepath):
    try:
        if not os.path.exists(filepath):
            logger.warning(f"文件不存在: {filepath}")
            return False
        
        if os.path.getsize(filepath) == 0:
            logger.warning(f"文件为空: {filepath}")
            return False
        
        try:
            content = Path(filepath).read_text(encoding='utf-8')
        except UnicodeDecodeError:
            logger.warning(f"文件编码错误，尝试其他编码: {filepath}")
            try:
                content = Path(filepath).read_text(encoding='gbk')
            except UnicodeDecodeError:
                logger.error(f"无法解码文件 (不支持 utf-8 或 gbk 编码): {filepath}")
                return False
        
        content = content.strip()
        if not content:
            logger.warning(f"文件内容为空: {filepath}")
            return False
        
        doc_id = hashlib.md5(filepath.encode()).hexdigest()
        chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 50]
        
        if not chunks:
            logger.warning(f"文件没有足够长的段落可切分: {filepath}")
            return False
        
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metas = [{"source": filepath, "chunk": i} for i in range(len(chunks))]
        collection.upsert(documents=chunks, ids=ids, metadatas=metas)
        logger.info(f"✅ 已入库: {filepath} ({len(chunks)} chunks)")
        return True
        
    except PermissionError:
        logger.error(f"无权限读取文件: {filepath}")
        return False
    except Exception as e:
        logger.error(f"处理文件时发生错误 {filepath}: {e}")
        return False

knowledge_dir = "./knowledge"
if not os.path.exists(knowledge_dir):
    logger.error(f"知识库目录不存在: {knowledge_dir}")
    sys.exit(1)

success_count = 0
fail_count = 0

for root, _, files in os.walk(knowledge_dir):
    for f in files:
        if f.endswith(('.md', '.txt')):
            filepath = os.path.join(root, f)
            if ingest_file(filepath):
                success_count += 1
            else:
                fail_count += 1

logger.info(f"入库完成: 成功 {success_count} 个文件, 失败 {fail_count} 个文件")
