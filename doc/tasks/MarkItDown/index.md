# MarkItDown

[MarkItDown](https://github.com/microsoft/markitdown) 是用于将文件和办公文档转换为 Markdown 的 Python 工具。

MarkItDown 是用于将各种文件转换为 Markdown 的工具（例如，用于索引、文本分析等）。它支持：

- PDF
- PowerPoint
- Word
- Excel
- 图像（EXIF 元数据和 OCR）
- 音频（EXIF 元数据和语音转录）
- HTML
- 基于文本的格式（CSV、JSON、XML）
- ZIP 文件（遍历内容）

要安装 MarkItDown，请使用 pip：`pip install markitdown`。或者，您可以从源代码安装：`pip install -e .`

## 使用方法
命令行
```bash
markitdown path-to-file.pdf > document.md
```
你也可以通过管道传递内容：
```bash
cat path-to-file.pdf | markitdown
```
Python API，在 Python 中的基本用法：
```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("test.xlsx")
print(result.text_content)
```
要使用大型语言模型进行图像描述，请提供 `llm_client` 和 `llm_model`：
```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o")
result = md.convert("example.jpg")
print(result.text_content)
```

Docker
```bash
docker build -t markitdown:latest .
docker run --rm -i markitdown:latest < ~/your-file.pdf > output.md
```
