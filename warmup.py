import requests
import time
from config import get_ollama_url, MODEL_FAST, MODEL_QUALITY, get_embedding_model

def warmup_model(model_name, ollama_url):
    print(f"预热模型: {model_name}...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model_name,
                "prompt": "Hi",
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            elapsed = time.time() - start_time
            print(f"  ✅ {model_name} 预热完成 ({elapsed:.1f}s)")
            return True
        else:
            print(f"  ❌ {model_name} 预热失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ {model_name} 预热出错: {e}")
        return False

def warmup_embedding_model(model_name, ollama_url):
    print(f"预热嵌入模型: {model_name}...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{ollama_url}/api/embeddings",
            json={
                "model": model_name,
                "prompt": "test"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            elapsed = time.time() - start_time
            print(f"  ✅ {model_name} 预热完成 ({elapsed:.1f}s)")
            return True
        else:
            print(f"  ❌ {model_name} 预热失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ {model_name} 预热出错: {e}")
        return False

def main():
    ollama_url = get_ollama_url()
    embedding_model = get_embedding_model()
    
    print("=" * 50)
    print("模型预热工具")
    print("=" * 50)
    print(f"Ollama URL: {ollama_url}")
    print()
    
    print("开始预热模型...")
    print()
    
    results = []
    
    results.append(warmup_embedding_model(embedding_model, ollama_url))
    results.append(warmup_model(MODEL_FAST, ollama_url))
    results.append(warmup_model(MODEL_QUALITY, ollama_url))
    
    print()
    print("=" * 50)
    success_count = sum(results)
    total_count = len(results)
    print(f"预热完成: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("✅ 所有模型已就绪，首次响应延迟已优化")
    else:
        print("⚠️ 部分模型预热失败，请检查 Ollama 服务")

if __name__ == "__main__":
    main()
