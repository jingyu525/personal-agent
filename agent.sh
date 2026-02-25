#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_HOME="${PERSONAL_AGENT_HOME:-$SCRIPT_DIR}"

get_model() {
  local mode="$1"
  python3 - << PYEOF
import sys
sys.path.insert(0, "$AGENT_HOME")
from config import get_model
print(get_model("$mode"))
PYEOF
}

case "$1" in
  ask)
    shift
    model_mode=""
    query_args=()
    
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --fast)
          model_mode="fast"
          shift
          ;;
        --quality)
          model_mode="quality"
          shift
          ;;
        *)
          query_args+=("$1")
          shift
          ;;
      esac
    done
    
    query="${query_args[*]}"
    model=$(get_model "$model_mode")
    
    context=$(python3 "$AGENT_HOME/search.py" "$query" 2>/dev/null | head -50)
    ollama run "$model" << PROMPT
基于以下个人知识库内容回答问题。

## 知识库检索结果：
$context

## 问题：$query

请给出准确、简洁的回答，引用知识库内容时注明来源。
PROMPT
    ;;
  
  add-note)
    echo "# $2" > "$AGENT_HOME/knowledge/inbox/$(date +%Y%m%d_%H%M)_$2.md"
    echo "内容 (Ctrl+D 结束):"
    cat >> "$AGENT_HOME/knowledge/inbox/$(date +%Y%m%d_%H%M)_$2.md"
    echo "✅ 已添加到 inbox"
    ;;
  
  todo)
    echo "- [ ] $2 @$(date +%Y-%m-%d)" >> "$AGENT_HOME/todos/backlog.md"
    echo "✅ 已添加待办: $2"
    ;;
  
  plan)
    bash "$AGENT_HOME/workflows/daily_plan.sh"
    ;;
  
  review)
    bash "$AGENT_HOME/workflows/weekly_review.sh"
    ;;
  
  sync)
    cd "$AGENT_HOME" && python3 ingest.py
    ;;
  
  warmup)
    python3 "$AGENT_HOME/warmup.py"
    ;;
  
  config)
    python3 "$AGENT_HOME/config.py"
    ;;
  
  *)
    echo "Usage: agent [ask|add-note|todo|plan|review|sync|warmup|config] [args]"
    echo ""
    echo "ask 命令选项:"
    echo "  --fast      使用快速模型 (llama3.2:3b)"
    echo "  --quality   使用质量优先模型 (qwen2.5:14b)"
    echo ""
    echo "环境变量:"
    echo "  AGENT_MODEL   设置默认模型 (fast/quality 或模型名称)"
    echo "  OLLAMA_BASE_URL 设置 Ollama 服务地址"
    ;;
esac
