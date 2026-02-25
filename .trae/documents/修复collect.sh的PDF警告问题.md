# 修复 collect.sh PDF 提取警告问题

## 问题分析

运行 `collect pdf` 命令时出现大量警告：
```
Could not get FontBBox from font descriptor because None cannot be parsed as 4 floats
```

**原因**：pdfplumber 在解析某些 PDF 文件时，遇到不完整或不规范的字体描述符信息，产生大量警告。这些警告不影响文本提取，但严重影响用户体验。

## 解决方案

在 Python 脚本中添加警告抑制配置，过滤掉 pdfplumber/pdfminer 的警告信息。

### 修改位置
文件：`/Users/zyb/personal-agent/collect.sh`
函数：`collect_pdf()` (第 27-39 行)

### 具体修改

在 Python heredoc 中添加警告抑制代码：

```python
import warnings
import logging

# 抑制 pdfminer 的警告日志
logging.getLogger('pdfminer').setLevel(logging.ERROR)
# 抑制所有警告
warnings.filterwarnings('ignore')
```

### 修改后的代码

```bash
collect_pdf() {
    filepath="$1"
    filename=$(basename "$filepath" .pdf)
    python3 - << PYEOF
import warnings
import logging
import pdfplumber

# 抑制 pdfminer/pdfplumber 的警告
logging.getLogger('pdfminer').setLevel(logging.ERROR)
warnings.filterwarnings('ignore')

with pdfplumber.open("$filepath") as pdf:
    text = "\n\n".join(p.extract_text() or "" for p in pdf.pages)
with open("$INBOX/${TIMESTAMP}_${filename}.md", "w") as f:
    f.write(f"# {filename}\n\n> 来源: $filepath\n\n")
    f.write(text)
print("✅ PDF 已提取: ${TIMESTAMP}_${filename}.md")
PYEOF
}
```

## 预期结果

- PDF 提取功能正常工作
- 不再显示大量 FontBBox 警告
- 输出简洁清晰
