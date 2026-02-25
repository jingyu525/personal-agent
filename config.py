import os
import argparse

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

MODEL_FAST = "llama3.2:3b"
MODEL_QUALITY = "qwen2.5:7b"
MODEL_HIGH = "qwen2.5:14b"
MODEL_DEFAULT = MODEL_QUALITY

EMBEDDING_MODEL = "nomic-embed-text"

def get_model(mode=None):
    if mode == "fast":
        return MODEL_FAST
    elif mode == "quality":
        return MODEL_QUALITY
    elif mode == "high":
        return MODEL_HIGH
    
    env_model = os.getenv("AGENT_MODEL", "")
    if env_model in ("fast", "quality", "high"):
        return {"fast": MODEL_FAST, "quality": MODEL_QUALITY, "high": MODEL_HIGH}[env_model]
    elif env_model:
        return env_model
    
    return MODEL_DEFAULT

def get_ollama_url():
    return OLLAMA_BASE_URL

def get_embedding_model():
    return EMBEDDING_MODEL

def parse_model_args(args):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-f", "--fast", action="store_true", help="使用快速模型")
    parser.add_argument("-q", "--quality", action="store_true", help="使用质量模型")
    parser.add_argument("-h", "--high", action="store_true", help="使用高质量模型")
    
    known, unknown = parser.parse_known_args(args)
    
    if known.fast:
        mode = "fast"
    elif known.high:
        mode = "high"
    elif known.quality:
        mode = "quality"
    else:
        mode = None
    
    return mode, unknown

if __name__ == "__main__":
    print(f"当前配置:")
    print(f"  Ollama URL: {get_ollama_url()}")
    print(f"  默认模型: {get_model()}")
    print(f"  快速模型 (-f): {MODEL_FAST}")
    print(f"  质量模型 (-q): {MODEL_QUALITY}")
    print(f"  高质量模型 (-h): {MODEL_HIGH}")
    print(f"  嵌入模型: {get_embedding_model()}")
