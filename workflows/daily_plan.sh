#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_HOME="${PERSONAL_AGENT_HOME:-$(dirname "$SCRIPT_DIR")}"

echo "🤖 生成今日计划中..."

BACKLOG=$(cat "$AGENT_HOME/todos/backlog.md")
DATE=$(date +%Y-%m-%d)

ollama run qwen2.5:14b << PROMPT
你是一个个人任务规划助手。

## 当前 Backlog：
$BACKLOG

## 任务：
基于以上 Backlog，为今天（$DATE）生成一份专注的日计划。
规则：
1. Must Do 不超过 3 项，选择最重要且当天必须完成的
2. 考虑任务的依赖关系
3. 输出严格按照 today.md 的 Markdown 格式

只输出 Markdown，不要解释。
PROMPT
