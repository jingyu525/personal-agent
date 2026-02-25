# Tasks

- [x] Task 1: 验证模型上下文窗口配置
  - [x] SubTask 1.1: 使用 ollama run 测试各模型的默认上下文限制
  - [x] SubTask 1.2: 测试通过 num_ctx 参数调整上下文窗口
  - [x] SubTask 1.3: 验证各模型在不同上下文大小下的性能表现

- [ ] Task 2: 实现上下文窗口配置优化
  - [ ] SubTask 2.1: 在 personal-agent 中添加模型配置文件
  - [ ] SubTask 2.2: 实现场景化的上下文窗口自动选择
  - [ ] SubTask 2.3: 添加配置验证和错误处理

- [ ] Task 3: 实现对话历史管理
  - [ ] SubTask 3.1: 设计对话历史存储结构
  - [ ] SubTask 3.2: 实现对话摘要和压缩机制
  - [ ] SubTask 3.3: 实现滑动窗口策略

- [ ] Task 4: 编写使用文档和最佳实践
  - [ ] SubTask 4.1: 记录各模型的推荐配置
  - [ ] SubTask 4.2: 提供场景化使用示例
  - [ ] SubTask 4.3: 编写性能调优指南

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] depends on [Task 1, Task 2, Task 3]
