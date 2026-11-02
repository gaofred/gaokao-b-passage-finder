#!/usr/bin/env python3
"""
生成高考 B 篇语篇 Word 文档。

用法：
  单篇：
    python3 create_docx.py --title "Article Title" \
      --source "BBC News" --date "2025-08-23" --url "https://..." \
      --output "/path/to/output.docx"

  批量（JSON输入）：
    python3 create_docx.py --input-json articles.json --output-dir "/path/to/dir/"

JSON 格式：
[
  {
    "title": "Article Title",
    "source": "BBC News",
    "date": "2025-08-23",
    "url": "https://...",
    "body": ["Paragraph 1", "Paragraph 2", ...]
  }
]
"""

import argparse
import json
import os
import re
import sys

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH


# ── 默认样式常量 ──────────────────────────────────────────────
FONT_NAME = "Georgia"
FONT_SIZE = Pt(11)
TITLE_SIZE = Pt(16)
SUBTITLE_SIZE = Pt(10)
HEADING_SIZE = Pt(13)
LINE_SPACING = Pt(16)
PARA_SPACING = Pt(6)

TITLE_COLOR = RGBColor(0x1A, 0x1A, 0x2E)   # 深蓝
SUBTITLE_COLOR = RGBColor(0x55, 0x55, 0x55)
HEADING_COLOR = RGBColor(0x2C, 0x3E, 0x50)
SEPARATOR = "─" * 60


def _set_run_font(run, font_name=FONT_NAME, font_size=FONT_SIZE,
                  color=None, italic=False, bold=False):
    run.font.name = font_name
    run.font.size = font_size
    if color:
        run.font.color.rgb = color
    run.font.italic = italic
    run.font.bold = bold


def create_article_docx(title, source_info, body_paragraphs, output_path):
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = FONT_NAME
    style.font.size = FONT_SIZE

    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)

    p = doc.add_heading(title, level=0)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in p.runs:
        _set_run_font(run, font_size=TITLE_SIZE, color=TITLE_COLOR)

    info_lines = [
        f"Source: {source_info.get('source', 'N/A')}",
        f"Date: {source_info.get('date', 'N/A')}",
    ]
    if source_info.get("url"):
        info_lines.append(f"URL: {source_info['url']}")

    for line in info_lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(line)
        _set_run_font(run, font_size=SUBTITLE_SIZE, color=SUBTITLE_COLOR,
                      italic=True)

    doc.add_paragraph(SEPARATOR)

    for para_text in body_paragraphs:
        stripped = para_text.strip()
        if not stripped:
            continue
        if stripped.isupper() and len(stripped) > 5 and not stripped.endswith("."):
            p = doc.add_heading(stripped.title(), level=1)
            for run in p.runs:
                _set_run_font(run, font_size=HEADING_SIZE, color=HEADING_COLOR)
            continue
        if stripped.startswith("## ") or stripped.startswith("### "):
            level = 1 if stripped.startswith("## ") else 2
            heading_text = stripped.lstrip("#").strip()
            p = doc.add_heading(heading_text, level=level)
            for run in p.runs:
                _set_run_font(run, font_size=HEADING_SIZE, color=HEADING_COLOR)
            continue
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(para_text)
        _set_run_font(run)
        p.paragraph_format.space_after = PARA_SPACING
        p.paragraph_format.line_spacing = LINE_SPACING

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    doc.save(output_path)
    print(f"✓ Saved: {output_path}")
    return output_path


def sanitize_filename(name, max_len=60):
    safe = re.sub(r'[<>:"/\\|?*]', "", name)
    safe = re.sub(r"\s+", "_", safe.strip())
    if len(safe) > max_len:
        safe = safe[:max_len]
    return safe


def batch_create_from_json(json_path, output_dir, filename_prefix=""):
    with open(json_path, "r", encoding="utf-8") as f:
        articles = json.load(f)
    os.makedirs(output_dir, exist_ok=True)
    results = []
    for i, article in enumerate(articles, 1):
        title = article.get("title", f"Article_{i}")
        source_info = {
            "source": article.get("source", "N/A"),
            "date": article.get("date", "N/A"),
            "url": article.get("url", ""),
        }
        body = article.get("body", [])
        source_short = sanitize_filename(article.get("source", "Unknown"), 20)
        keywords = sanitize_filename(title, 40).split("_")[:4]
        keyword_str = "_".join(keywords)
        filename = f"{filename_prefix}{i:02d}_{source_short}_{keyword_str}.docx"
        output_path = os.path.join(output_dir, filename)
        create_article_docx(title, source_info, body, output_path)
        results.append(output_path)
    print(f"\n✅ {len(results)} documents created in {output_dir}")
    return results


def main():
    parser = argparse.ArgumentParser(description="生成高考 B 篇语篇 Word 文档")
    parser.add_argument("--input-json", help="批量模式的 JSON 输入文件")
    parser.add_argument("--output-dir", help="批量模式的输出目录")
    parser.add_argument("--title", help="单篇模式的文章标题")
    parser.add_argument("--source", help="单篇模式的来源")
    parser.add_argument("--date", help="单篇模式的日期")
    parser.add_argument("--url", help="单篇模式的URL")
    parser.add_argument("--output", help="单篇模式的输出文件路径")
    parser.add_argument("--prefix", default="", help="文件名前缀")
    args = parser.parse_args()

    if args.input_json:
        if not args.output_dir:
            print("❌ 批量模式需要 --output-dir")
            sys.exit(1)
        batch_create_from_json(args.input_json, args.output_dir, args.prefix)
    elif args.title:
        if not args.output:
            print("❌ 单篇模式需要 --output")
            sys.exit(1)
        source_info = {
            "source": args.source or "N/A",
            "date": args.date or "N/A",
            "url": args.url or "",
        }
        create_article_docx(args.title, source_info, [], args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
