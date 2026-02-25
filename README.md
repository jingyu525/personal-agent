# Personal Agent - 个人智能助手

基于本地 AI 的个人知识管理和智能助手系统，完全本地化运行，保护隐私。

## 功能特性

- 🧠 **知识库管理**：基于 ChromaDB 的本地向量数据库，支持知识检索和问答
- 📝 **数据采集**：支持多种数据源采集（剪贴板、网页、PDF、Word、音频、截图）
- ✅ **待办管理**：MCP 服务器驱动的待办事项管理
- 🤖 **智能问答**：基于本地 Ollama 模型的知识库增强问答
- 🔒 **完全本地化**：所有数据和处理都在本地完成，保护隐私

## 系统要求

- Python 3.11+
- Ollama（本地 LLM 服务）
- macOS（当前版本）

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/jingyu525/personal-agent.git
cd personal-agent
```

### 2. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装 Ollama

访问 [Ollama 官网](https://ollama.ai) 下载并安装。

### 5. 下载模型

```bash
ollama pull qwen2.5:14b
ollama pull nomic-embed-text
```

### 6. 初始化知识库

```bash
python3 kb_init.py
```

## 使用方法

### 数据采集

```bash
./collect.sh clip [标题]        # 剪贴板内容
./collect.sh url  <网址>        # 网页内容
./collect.sh pdf  <文件路径>    # PDF 文档
./collect.sh word <文件路径>    # Word 文档
./collect.sh audio <文件路径>   # 音频转录
./collect.sh shot               # 截图 OCR
```

### 智能助手

```bash
./agent.sh ask <问题>           # 知识库增强问答（默认模型 qwen2.5:7b）
./agent.sh ask -f <问题>        # 使用快速模型（响应更快）
./agent.sh ask -q <问题>        # 使用质量模型
./agent.sh ask -h <问题>        # 使用高质量模型（回答更准确）
./agent.sh add-note <标题>      # 快速添加笔记
./agent.sh todo <待办事项>      # 添加待办
./agent.sh plan                 # 生成今日计划
./agent.sh review               # 生成周报
./agent.sh sync                 # 重建知识库索引
./agent.sh warmup               # 预热模型（减少首次响应延迟）
./agent.sh config               # 查看当前配置
```

### 模型配置

项目支持三种模型模式，可在速度和质量之间权衡：

| 选项 | 短选项 | 模型 | 特点 |
|------|--------|------|------|
| `--fast` | `-f` | llama3.2:3b | 响应快速，适合简单问题 |
| `--quality` | `-q` | qwen2.5:7b | 平衡速度与质量 [默认] |
| `--high` | `-h` | qwen2.5:14b | 回答准确，适合复杂问题 |

首次使用前需要下载模型：

```bash
ollama pull llama3.2:3b      # 快速模型
ollama pull qwen2.5:7b       # 质量模型（默认）
ollama pull qwen2.5:14b      # 高质量模型
ollama pull nomic-embed-text # 嵌入模型
```

通过环境变量设置默认模型：

```bash
export AGENT_MODEL=fast     # 默认使用快速模型
export AGENT_MODEL=quality  # 默认使用质量模型
export AGENT_MODEL=high     # 默认使用高质量模型
```

### MCP 服务器配置

将 `mcp_config.json` 添加到你的 MCP 客户端配置中：

```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "python3",
      "args": ["~/personal-agent/mcp_kb_server.py"],
      "description": "本地知识库检索"
    }
  }
}
```

## 项目结构

```
personal-agent/
├── config.py             # 配置管理（模型选择）
├── mcp_kb_server.py      # MCP 知识库服务器
├── search.py             # 知识库搜索
├── ingest.py             # 数据导入和索引
├── kb_init.py            # 知识库初始化
├── warmup.py             # 模型预热
├── collect.sh            # 数据采集脚本
├── agent.sh              # 助手命令入口
├── tests/                # 单元测试
│   ├── conftest.py       # 测试夹具
│   ├── test_search.py    # 搜索测试
│   ├── test_ingest.py    # 导入测试
│   ├── test_mcp_kb_server.py  # MCP 服务器测试
│   └── test_kb_init.py   # 初始化测试
├── workflows/            # 工作流脚本
│   ├── daily_plan.sh
│   ├── process_inbox.sh
│   └── weekly_review.sh
├── skills/               # 技能定义
│   ├── coding.skill.md
│   ├── knowledge.skill.md
│   └── writing.skill.md
├── knowledge/            # 知识库数据（不纳入版本控制）
│   └── inbox/
├── todos/                # 待办事项（不纳入版本控制）
├── vector_db/            # 向量数据库（不纳入版本控制）
└── requirements.txt      # Python 依赖
```

## 配置说明

### 环境变量

项目使用相对路径，建议设置以下环境变量：

```bash
export PERSONAL_AGENT_HOME=~/personal-agent
```

### 快捷命令别名

为了提高使用效率，可以在 `~/.zshrc` 或 `~/.bashrc` 中添加以下别名：

```bash
# AI 模型快捷命令
alias ai-local="ollama run qwen2.5:14b"     # 隐私任务
alias ai-fast="ollama run llama3.2:3b"       # 快速响应
alias ai-code="claude"                        # 代码任务（Claude Code）

# 个人助手快捷命令
alias kb="cd ~/personal-agent && python3 search.py"
alias today="cat ~/personal-agent/todos/today.md"
alias inbox="open ~/personal-agent/knowledge/inbox/"
```

添加后运行 `source ~/.zshrc` 或 `source ~/.bashrc` 生效。

### 依赖工具

部分功能需要额外安装：

- `monolith`：网页保存
- `pandoc`：格式转换
- `ffmpeg`：音频处理（Whisper 依赖）

```bash
brew install monolith pandoc ffmpeg
```

## 技术栈

- **LLM**: Ollama (qwen2.5:14b)
- **向量数据库**: ChromaDB
- **嵌入模型**: nomic-embed-text
- **MCP 协议**: Model Context Protocol
- **文档处理**: pdfplumber, python-docx
- **音频转录**: OpenAI Whisper

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 注意事项

- 所有个人数据（知识库、待办事项、向量数据库）默认不纳入版本控制
- 请确保 `.gitignore` 正确配置，避免泄露个人隐私
- 建议定期备份 `knowledge/` 和 `vector_db/` 目录
