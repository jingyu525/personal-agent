#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_HOME="${PERSONAL_AGENT_HOME:-$SCRIPT_DIR}"

case "$1" in
  ask)
    shift
    query="$*"
    context=$(python3 "$AGENT_HOME/search.py" "$query" 2>/dev/null | head -50)
    ollama run qwen2.5:14b << PROMPT
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
  
  *)
    echo "Usage: agent [ask|add-note|todo|plan|review|sync] [args]"
    ;;
esac
