# Checklist

## 测试覆盖
- [x] tests 目录已创建，包含 __init__.py
- [x] pytest 已添加到 requirements.txt
- [x] conftest.py 包含测试夹具配置
- [x] test_search.py 测试覆盖正常搜索和异常情况
- [x] test_ingest.py 测试覆盖文件导入和切分逻辑
- [x] test_mcp_kb_server.py 测试覆盖 MCP 协议处理
- [x] test_kb_init.py 测试覆盖知识库初始化
- [x] 所有测试通过（pytest 命令执行成功）

## 模型性能优化
- [x] config.py 配置模块已创建，支持模型选择
- [x] agent.sh 支持 --fast 和 --quality 参数
- [x] 默认模型配置合理（建议快速模型作为默认）
- [x] 模型预热功能已实现

## 错误处理
- [x] mcp_kb_server.py 包含完善的异常处理
- [x] search.py 检查 Ollama 服务可用性
- [x] ingest.py 处理文件不存在和编码错误
- [x] 错误信息清晰友好

## 文档
- [x] README.md 已更新，说明新的模型配置选项
- [x] 配置说明清晰易懂
