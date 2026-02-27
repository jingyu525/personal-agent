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
        -f|--fast)
          model_mode="fast"
          shift
          ;;
        -q|--quality)
          model_mode="quality"
          shift
          ;;
        -h|--high)
          model_mode="high"
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
    shift
    task="$*"
    timestamp=$(date +%Y%m%d_%H%M%S)
    date_str=$(date +%Y-%m-%d)
    
    # 1. 添加到 backlog.md
    echo "- [ ] $task @$date_str" >> "$AGENT_HOME/todos/backlog.md"
    
    # 2. 同步到知识库 inbox
    cat > "$AGENT_HOME/knowledge/inbox/${timestamp}_todo_${task//[^a-zA-Z0-9]/_}.md" << EOF
---
source: todo
type: task
status: backlog
date: $date_str
created: $timestamp
---

# 待办：$task

**创建时间**: $date_str  
**状态**: 待完成

## 描述
$task

## 标签
#todo #backlog
EOF
    
    echo "✅ 已添加待办: $task"
    echo "📝 已同步到知识库"
    
    # 3. 自动重建索引（后台执行，不阻塞）
    (cd "$AGENT_HOME" && python3 ingest.py >/dev/null 2>&1 &)
    ;;
  
  done)
    shift
    task_pattern="$*"
    
    # 从 today.md 或 backlog.md 中找到任务
    if grep -q "- \[ \] .*$task_pattern" "$AGENT_HOME/todos/today.md" 2>/dev/null; then
        file="$AGENT_HOME/todos/today.md"
    elif grep -q "- \[ \] .*$task_pattern" "$AGENT_HOME/todos/backlog.md" 2>/dev/null; then
        file="$AGENT_HOME/todos/backlog.md"
    else
        echo "❌ 未找到任务: $task_pattern"
        exit 1
    fi
    
    # 标记为完成
    sed -i.bak "s/- \[ \] \(.*$task_pattern.*\)/- [x] \1 @done:$(date +%Y-%m-%d)/" "$file"
    rm -f "${file}.bak"
    
    # 归档到知识库
    timestamp=$(date +%Y%m%d_%H%M%S)
    cat > "$AGENT_HOME/knowledge/inbox/${timestamp}_todo_done_${task_pattern//[^a-zA-Z0-9]/_}.md" << EOF
---
source: todo
type: task
status: done
completed: $(date +%Y-%m-%d)
---

# ✅ 已完成：$task_pattern

**完成时间**: $(date +%Y-%m-%d)

## 任务描述
$task_pattern

## 标签
#todo #done
EOF
    
    echo "✅ 任务已完成: $task_pattern"
    echo "📝 已归档到知识库"
    
    # 重建索引
    (cd "$AGENT_HOME" && python3 ingest.py >/dev/null 2>&1 &)
    ;;
  
  archive-todos)
    today=$(date +%Y-%m-%d)
    archive_dir="$AGENT_HOME/todos/done"
    archive_file="$archive_dir/${today}_archive.md"
    
    # 确保归档目录存在
    mkdir -p "$archive_dir"
    
    # 从 today.md 提取已完成任务
    completed=$(grep "- \[x\]" "$AGENT_HOME/todos/today.md" 2>/dev/null || echo "")
    
    if [ -z "$completed" ]; then
        echo "📭 今天没有完成的任务"
        exit 0
    fi
    
    # 创建归档文件
    cat > "$archive_file" << EOF
---
date: $today
type: daily_archive
---

# $today 完成的任务

$completed

---
归档时间: $(date +%Y-%m-%d\ %H:%M:%S)
EOF
    
    # 同步到知识库
    cp "$archive_file" "$AGENT_HOME/knowledge/inbox/$(date +%Y%m%d_%H%M%S)_daily_todos_$today.md"
    
    # 从 today.md 移除已完成任务
    grep -v "- \[x\]" "$AGENT_HOME/todos/today.md" > "$AGENT_HOME/todos/today.md.tmp" 2>/dev/null
    mv "$AGENT_HOME/todos/today.md.tmp" "$AGENT_HOME/todos/today.md"
    
    echo "✅ 已归档今日完成任务 ($archive_file)"
    echo "📝 已同步到知识库"
    
    # 重建索引
    cd "$AGENT_HOME" && python3 ingest.py
    ;;
  
  stats)
    echo "📊 待办统计"
    echo ""
    backlog_count=$(grep -c "- \[ \]" "$AGENT_HOME/todos/backlog.md" 2>/dev/null || echo 0)
    today_count=$(grep -c "- \[ \]" "$AGENT_HOME/todos/today.md" 2>/dev/null || echo 0)
    today_done=$(grep -c "- \[x\]" "$AGENT_HOME/todos/today.md" 2>/dev/null || echo 0)
    
    echo "📋 待办池: $backlog_count"
    echo "📅 今日待办: $today_count"
    echo "✅ 今日已完成: $today_done"
    echo ""
    
    # 从知识库统计（可选，需要时间）
    # echo "🔍 知识库统计（检索中...）"
    # python3 - << PYEOF 2>/dev/null
# from search import search_knowledge
# results = search_knowledge("#todo", top_k=50)
# docs = results.get('documents', [[]])[0]
# backlog = sum(1 for d in docs if '#backlog' in d)
# done = sum(1 for d in docs if '#done' in d)
# print(f"  待办池: {backlog}")
# print(f"  已完成: {done}")
# PYEOF
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
    echo "Personal Agent - 个人智能助手"
    echo ""
    echo "用法:"
    echo "  agent ask [选项] <问题>    # 知识库增强问答"
    echo "    -f, --fast              # 使用快速模型 (llama3.2:3b)"
    echo "    -q, --quality           # 使用质量模型 (qwen2.5:7b) [默认]"
    echo "    -h, --high              # 使用高质量模型 (qwen2.5:14b)"
    echo ""
    echo "  agent todo <任务描述>       # 添加待办（自动入库）"
    echo "  agent done <任务描述>       # 标记完成（自动归档）"
    echo "  agent archive-todos        # 归档今日完成任务"
    echo "  agent stats                # 待办统计"
    echo "  agent plan                 # 生成今日计划"
    echo "  agent review               # 生成周报"
    echo ""
    echo "  agent add-note <标题>      # 快速添加笔记"
    echo "  agent sync                 # 重建知识库索引"
    echo "  agent warmup               # 预热模型"
    echo "  agent config               # 查看当前配置"
    echo ""
    echo "环境变量:"
    echo "  AGENT_MODEL     设置默认模型 (fast/quality/high 或模型名称)"
    echo "  OLLAMA_BASE_URL 设置 Ollama 服务地址"
    ;;
esac
