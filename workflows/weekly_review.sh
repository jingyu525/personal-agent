#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_HOME="${PERSONAL_AGENT_HOME:-$(dirname "$SCRIPT_DIR")}"

WEEK=$(date +%Y-W%V)
DONE_DIR="$AGENT_HOME/todos/done"

completed=$(find "$DONE_DIR" -name "*.md" -newer "$DONE_DIR/.last_review" -exec cat {} \; 2>/dev/null)

ollama run qwen2.5:14b << PROMPT > "$AGENT_HOME/knowledge/daily/weekly-review-$WEEK.md"
生成本周工作回顾报告（Markdown格式）：

## 已完成事项：
$completed

包含以下章节：
1. 本周亮点（3条）
2. 未完成事项分析
3. 下周重点方向
4. 个人成长观察

风格：简洁、客观、有洞见。
PROMPT

echo "✅ 周报已生成: weekly-review-$WEEK.md"
osascript -e 'display notification "本周回顾已生成" with title "Personal Agent"'
