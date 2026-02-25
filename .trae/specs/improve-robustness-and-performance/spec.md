# 项目优化：健壮性与性能提升

## Why
当前项目存在两个主要问题：
1. **缺少单元测试**：核心模块（mcp_kb_server.py, search.py, ingest.py, kb_init.py）没有测试覆盖，导致代码健壮性差，难以重构和维护
2. **Ollama 本地模型响应慢**：使用 qwen2.5:14b 模型进行问答时响应较慢，影响用户体验

## What Changes
- 为所有核心 Python 模块添加单元测试
- 优化模型配置，提供更快的模型选项
- 添加模型切换功能，让用户可以在质量和速度之间权衡
- 添加错误处理和日志记录

## Impact
- Affected specs: 知识库管理、智能问答
- Affected code:
  - `mcp_kb_server.py` - MCP 知识库服务器
  - `search.py` - 知识库搜索
  - `ingest.py` - 数据导入
  - `kb_init.py` - 知识库初始化
  - `agent.sh` - 助手命令入口

## ADDED Requirements

### Requirement: 单元测试覆盖
系统 SHALL 为所有核心 Python 模块提供单元测试覆盖，确保代码健壮性。

#### Scenario: 测试知识库搜索功能
- **WHEN** 用户调用 search.py 进行知识库搜索
- **THEN** 系统应正确返回相关文档并处理异常情况

#### Scenario: 测试数据导入功能
- **WHEN** 用户导入文档到知识库
- **THEN** 系统应正确切分文档并存储到向量数据库

#### Scenario: 测试 MCP 服务器
- **WHEN** MCP 客户端调用知识库服务
- **THEN** 服务器应正确响应 tools/list 和 tools/call 请求

### Requirement: 模型性能优化
系统 SHALL 支持多种模型配置，允许用户在响应速度和回答质量之间权衡。

#### Scenario: 快速模型模式
- **WHEN** 用户选择快速模式
- **THEN** 系统使用更轻量的模型（如 llama3.2:3b）进行问答

#### Scenario: 质量优先模式
- **WHEN** 用户选择质量模式
- **THEN** 系统使用更大的模型（如 qwen2.5:14b）进行问答

### Requirement: 错误处理增强
系统 SHALL 提供完善的错误处理和日志记录。

#### Scenario: Ollama 服务不可用
- **WHEN** Ollama 服务未启动或不可达
- **THEN** 系统应给出清晰的错误提示而非崩溃

#### Scenario: 知识库为空
- **WHEN** 知识库中没有相关文档
- **THEN** 系统应优雅地处理空结果

## MODIFIED Requirements

### Requirement: agent.sh 命令扩展
原有的 agent.sh 命令 SHALL 支持模型选择参数。

```bash
./agent.sh ask <问题>              # 默认使用配置的模型
./agent.sh ask --fast <问题>       # 使用快速模型
./agent.sh ask --quality <问题>    # 使用质量优先模型
```
