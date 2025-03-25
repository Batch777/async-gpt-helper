import requests
import html2text

url = "https://arxiv.org/html/2403.17888v3"
response = requests.get(url)
html_content = response.text

# 将 HTML 转换为 Markdown
markdown_text = html2text.html2text(html_content)
segments = [
    segment.strip() for segment in markdown_text.split("\n\n") if segment.strip()
]
for segment in segments:
    print(segment)
