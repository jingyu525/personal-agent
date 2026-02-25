# Tasks

- [x] Task 1: 创建测试基础设施
  - [x] SubTask 1.1: 创建 tests 目录和测试配置文件
  - [x] SubTask 1.2: 添加 pytest 和相关测试依赖到 requirements.txt
  - [x] SubTask 1.3: 创建 conftest.py 测试夹具配置

- [x] Task 2: 为核心模块添加单元测试
  - [x] SubTask 2.1: 创建 test_search.py 测试知识库搜索功能
  - [x] SubTask 2.2: 创建 test_ingest.py 测试数据导入功能
  - [x] SubTask 2.3: 创建 test_mcp_kb_server.py 测试 MCP 服务器
  - [x] SubTask 2.4: 创建 test_kb_init.py 测试知识库初始化

- [x] Task 3: 优化模型配置和性能
  - [x] SubTask 3.1: 创建 config.py 配置管理模块，支持模型选择
  - [x] SubTask 3.2: 修改 agent.sh 支持模型切换参数（--fast, --quality）
  - [x] SubTask 3.3: 更新 search.py 支持配置化的模型选择
  - [x] SubTask 3.4: 添加模型预热功能减少首次响应延迟

- [x] Task 4: 增强错误处理
  - [x] SubTask 4.1: 为 mcp_kb_server.py 添加异常处理和日志
  - [x] SubTask 4.2: 为 search.py 添加 Ollama 连接检查
  - [x] SubTask 4.3: 为 ingest.py 添加文件处理异常处理

- [x] Task 5: 验证和文档
  - [x] SubTask 5.1: 运行所有测试确保通过
  - [x] SubTask 5.2: 更新 README.md 说明新的模型配置选项

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] 可与 [Task 2] 并行执行
- [Task 4] 可与 [Task 2] 并行执行
- [Task 5] depends on [Task 2, Task 3, Task 4]
