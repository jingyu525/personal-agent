# 隐私保护说明

本项目是个人知识库和效率工具，包含以下**本地化隐私数据**：

## 🔒 不会被提交到 GitHub 的目录

| 目录 | 内容 | 说明 |
|------|------|------|
| `knowledge/` | 个人知识库 | 包含笔记、项目文档、OpenClaw 对话历史 |
| `todos/` | 待办事项 | 今日任务、待办池、已完成归档 |
| `vector_db/` | 向量数据库 | Chroma 向量索引（用于语义搜索） |
| `.claude/` | Claude Desktop 配置 | 可能包含 API Key 或个人路径 |

这些目录已在 `.gitignore` 中配置，Git 会**自动忽略**。

---

## 🛡️ 隐私保护机制

### 1. .gitignore 自动过滤

```gitignore
# 个人数据（不共享）
knowledge/
todos/
vector_db/

# 配置文件（包含用户特定路径）
.claude/

# 日志和临时文件
*.log
/tmp/
```

### 2. Git 历史检查

所有隐私数据**从未被提交**到 Git 历史中。

可以随时验证：
```bash
git log --all --name-only | grep -E "knowledge|todos|vector_db"
# 应该输出为空
```

---

## 📦 克隆后如何使用

如果你克隆了这个项目：

1. **克隆后不会包含隐私数据**  
   你会看到空的 `knowledge/`、`todos/` 目录（或完全不存在）

2. **首次运行自动初始化**  
   运行 `./agent.sh` 会自动创建必要的目录结构

3. **你的数据完全本地化**  
   所有知识库和待办事项只存储在你的本地，不会同步到任何地方

---

## ⚠️ 重要提醒

### ✅ 安全操作

```bash
# 正常提交代码（自动跳过隐私文件）
git add .
git commit -m "update scripts"
git push
```

### ❌ 危险操作（避免）

```bash
# ❌ 不要强制添加被忽略的文件
git add -f knowledge/

# ❌ 不要修改 .gitignore 中的隐私规则
```

---

## 🔍 如何验证隐私保护

随时运行以下命令自检：

```bash
# 检查隐私目录是否被 Git 忽略
git check-ignore -v knowledge/ todos/ vector_db/

# 应该输出：
# .gitignore:42:knowledge/    knowledge/
# .gitignore:43:todos/        todos/
# .gitignore:44:vector_db/    vector_db/
```

如果输出包含 `.gitignore` 规则，说明保护有效 ✅

---

## 📞 问题反馈

如果发现任何隐私泄露风险，请立即：
1. 停止 `git push`
2. 检查 `git status` 和 `git diff --cached`
3. 使用 `git reset HEAD <file>` 取消暂存

---

**最后更新**：2026-02-27  
**项目作者**：jingyu525  
**GitHub**：https://github.com/jingyu525/personal-agent
