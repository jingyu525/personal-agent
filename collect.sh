#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INBOX="${PERSONAL_AGENT_HOME:-$SCRIPT_DIR}/knowledge/inbox"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

collect_clipboard() {
    content=$(pbpaste)
    if [ -z "$content" ]; then
        echo "❌ 剪贴板为空"
        exit 1
    fi
    title="${1:-clipboard}"
    echo "$content" > "$INBOX/${TIMESTAMP}_${title}.md"
    echo "✅ 剪贴板已保存: ${TIMESTAMP}_${title}.md"
}

collect_url() {
    url="$1"
    title=$(echo "$url" | sed 's/https\?:\/\///' | tr '/' '_' | cut -c1-40)
    # 网页转 Markdown
    monolith "$url" -o /tmp/page.html 2>/dev/null
    pandoc /tmp/page.html -t markdown -o "$INBOX/${TIMESTAMP}_${title}.md" 2>/dev/null
    echo "✅ 网页已保存: ${TIMESTAMP}_${title}.md"
}

collect_pdf() {
    filepath="$1"
    filename=$(basename "$filepath" .pdf)
    python3 - << PYEOF
import warnings
import logging
import pdfplumber

logging.getLogger('pdfminer').setLevel(logging.ERROR)
warnings.filterwarnings('ignore')

filepath = "$filepath"
filename = "$filename"
inbox = "$INBOX"
timestamp = "$TIMESTAMP"

with pdfplumber.open(filepath) as pdf:
    text = "\n\n".join(p.extract_text() or "" for p in pdf.pages)
with open(f"{inbox}/{timestamp}_{filename}.md", "w") as f:
    f.write(f"# {filename}\n\n> 来源: {filepath}\n\n")
    f.write(text)
print(f"✅ PDF 已提取: {timestamp}_{filename}.md")
PYEOF
}

collect_docx() {
    filepath="$1"
    filename=$(basename "$filepath" .docx)
    python3 - << PYEOF
from docx import Document
doc = Document("$filepath")
text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
with open("$INBOX/${TIMESTAMP}_${filename}.md", "w") as f:
    f.write(f"# {filename}\n\n> 来源: $filepath\n\n")
    f.write(text)
print("✅ Word 已提取: ${TIMESTAMP}_${filename}.md")
PYEOF
}

collect_audio() {
    filepath="$1"
    filename=$(basename "$filepath")
    echo "🎙 转录中（本地 Whisper）..."
    python3 - << PYEOF
import whisper
model = whisper.load_model("base")  # 或 small/medium
result = model.transcribe("$filepath", language="zh")
with open("$INBOX/${TIMESTAMP}_${filename}.md", "w") as f:
    f.write(f"# 语音转录: {filename}\n\n")
    f.write(result["text"])
print("✅ 音频已转录")
PYEOF
}

collect_screenshot() {
    # 截图 + Ollama Vision OCR
    filepath="${1:-/tmp/screenshot.png}"
    screencapture -i "$filepath"   # 交互式截图
    result=$(ollama run llava:13b "请提取这张图片中的所有文字内容，保持原始格式" < "$filepath")
    echo "$result" > "$INBOX/${TIMESTAMP}_screenshot.md"
    echo "✅ 截图已 OCR"
}

# 路由分发
case "$1" in
    clip|c)     collect_clipboard "$2" ;;
    url|u)      collect_url "$2" ;;
    pdf|p)      collect_pdf "$2" ;;
    word|w)     collect_docx "$2" ;;
    audio|a)    collect_audio "$2" ;;
    shot|s)     collect_screenshot "$2" ;;
    *)
        echo "用法:"
        echo "  collect clip [标题]        # 剪贴板"
        echo "  collect url  <网址>        # 网页"
        echo "  collect pdf  <文件路径>    # PDF"
        echo "  collect word <文件路径>    # Word"
        echo "  collect audio <文件路径>   # 录音转录"
        echo "  collect shot               # 截图 OCR"
        ;;
esac
