#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_HOME="${PERSONAL_AGENT_HOME:-$(dirname "$SCRIPT_DIR")}"

INBOX_DIR="$AGENT_HOME/knowledge/inbox"
NOTES_DIR="$AGENT_HOME/knowledge/notes"

for file in "$INBOX_DIR"/*.md; do
    [ -f "$file" ] || continue
    filename=$(basename "$file")
    content=$(cat "$file")
    
    echo "📄 处理: $filename"
    
    result=$(ollama run qwen2.5:14b << PROMPT
分析以下笔记，返回 JSON：
{"category": "tech|life|work|reference", "tags": ["tag1","tag2"], "summary": "50字摘要", "title": "建议标题"}

笔记内容：
$content

只返回 JSON，不要其他内容。
PROMPT
)
    
    category=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['category'])")
    
    target_dir="$NOTES_DIR/$category"
    mkdir -p "$target_dir"
    mv "$file" "$target_dir/$filename"
    
    echo "✅ 已归档到: $category/$filename"
done

cd "$AGENT_HOME" && python3 ingest.py
