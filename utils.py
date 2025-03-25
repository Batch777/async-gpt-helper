import re
from pathlib import Path
import os
import pymupdf
import tempfile
import html2text
import requests
from urllib.parse import urlparse


def process_image(filename):
    return f"[IMG处理] {filename}"


def process_pdf(filePath):
    text = ""
    with pymupdf.open(filePath) as doc:  # open a document
        for page in doc:  # iterate the document pages
            text += page.get_text()  # get plain text encoded as UTF-8
    return text


def process_text(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def process_file(filename):
    path = Path(filename)
    if not path.exists():
        return f"[文件不存在] {filename}"
    ext = path.suffix.lower()
    if ext in [".jpg", ".jpeg", ".png", ".gif"]:
        return process_image(filename)
    elif ext == ".pdf":
        return process_pdf(filename)
    elif ext in [".txt", ".md", ".py", ".c", ".h", ".hpp", ".cpp", ".cu"]:
        return process_text(filename)
    else:
        return f"[不支持类型] {ext}"


def replace_file_tag(match):
    processed = process_file(match.group(1))
    return f'"{processed}"'


def process_arxiv(url_arxiv):
    url = url_arxiv.replace("/abs/", "/html/")
    response = requests.get(url)
    html_content = response.text

    # 将 HTML 转换为 Markdown
    markdown_text = html2text.html2text(html_content)
    return markdown_text
    # PDF deprecated
    # pdf_url = url_arxiv.replace("/abs/", "/pdf/")
    # if not pdf_url.endswith(".pdf"):
    #     pdf_url += ".pdf"
    #     return process_url(pdf_url)


def process_url(url):
    try:
        response = requests.get(url)
    except Exception as e:
        return f"[请求错误] {e}"

    content_type = response.headers.get("Content-Type", "")
    if "text/html" in content_type:
        # 如果返回内容为普通网页，则直接返回其文本内容
        return response.text
    else:
        # 提取 URL 中的扩展名（如果有的话）
        parsed_url = urlparse(url)
        _, ext = os.path.splitext(parsed_url.path)
        # 创建带有扩展名的临时文件
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(response.content)
            tmp_filename = tmp.name
        try:
            result = process_file(tmp_filename)
        finally:
            os.remove(tmp_filename)
        return result


handler_map = {
    "file": lambda content: f'"{process_file(content)}"',
    "url": lambda content: f'"{process_url(content)}"',
    "arx": lambda content: f'"{process_arxiv(content)}"',
    # 以后若需要新增其他类型处理，只需添加新的映射
}


def replace_tag(match):
    tag = match.group(1)
    content = match.group(2)
    if tag in handler_map:
        return handler_map[tag](content)
    else:
        # 如果不支持该 tag，原样返回匹配字符串
        return match.group(0)


def handle_input(input_str):
    # 匹配模式：@tag(content)
    pattern = re.compile(r"@(\w+)\(([^)]+)\)")
    return re.sub(pattern, replace_tag, input_str)
