#!/bin/bash
# OpenClaw 对话自动同步脚本

OPENCLAW_MEMORY="/Users/zyb/.openclaw/workspace/memory"
AGENT_HOME="/Users/zyb/personal-agent"
TODAY=$(date +%Y-%m-%d)

echo "🔄 开始每日同步任务..."
echo ""

# 1. 同步 OpenClaw 对话记录
if [ -f "$OPENCLAW_MEMORY/$TODAY.md" ]; then
    cd "$AGENT_HOME" && ./collect.sh openclaw "$OPENCLAW_MEMORY/$TODAY.md"
    echo "✅ 已同步今天的 OpenClaw 对话"
else
    echo "⚠️  今天还没有 OpenClaw 对话记录"
fi

# 2. 检查是否需要同步昨天的（如果昨天有对话但还没同步）
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d 2>/dev/null)
if [ -f "$OPENCLAW_MEMORY/$YESTERDAY.md" ]; then
    # 检查是否已经同步过
    if ! ls "$AGENT_HOME/knowledge/inbox/"*"openclaw_$YESTERDAY.md" 1> /dev/null 2>&1; then
        cd "$AGENT_HOME" && ./collect.sh openclaw "$OPENCLAW_MEMORY/$YESTERDAY.md"
        echo "✅ 补同步昨天 ($YESTERDAY) 的对话记录"
    fi
fi

echo ""

# 3. 归档今日完成的待办
cd "$AGENT_HOME" && ./agent.sh archive-todos
echo ""

echo "🎉 每日同步完成！"
