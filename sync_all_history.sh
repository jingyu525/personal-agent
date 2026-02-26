#!/bin/bash
# 快速同步所有 OpenClaw 历史对话

OPENCLAW_MEMORY="/Users/zyb/.openclaw/workspace/memory"
AGENT_HOME="/Users/zyb/personal-agent"

echo "🔄 开始同步所有 OpenClaw 历史对话..."
echo ""

count=0
for f in "$OPENCLAW_MEMORY"/*.md; do
    if [ -f "$f" ]; then
        filename=$(basename "$f")
        echo "📝 同步: $filename"
        cd "$AGENT_HOME" && ./collect.sh openclaw "$f"
        count=$((count + 1))
    fi
done

echo ""
echo "✅ 完成！共同步 $count 个对话文件"
echo "💡 现在可以使用 ./agent.sh ask '问题' 来检索历史对话了"
