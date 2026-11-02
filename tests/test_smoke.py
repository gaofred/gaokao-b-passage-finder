#!/usr/bin/env python3
"""Smoke test：文档生成脚本能跑通，SKILL.md 引用的文件都在。

Run from the repo root: python tests/test_smoke.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "create_docx.py"
failures: list[str] = []


def check(condition: bool, message: str) -> None:
    print(f"  {'ok  ' if condition else 'FAIL'} {message}")
    if not condition:
        failures.append(message)


def check_references() -> None:
    """SKILL.md 提到的 references/、scripts/ 路径必须能解析到。

    本仓库找不到时，再去同级 skill 目录找——这一族的 skill 会互相引用
    下游的规范文件（如 gaokao-b-reading-generator 的 adaptation_spec.md）。
    """
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    cited = set(re.findall(r"(?:references|scripts)/[A-Za-z0-9_\-]+\.(?:md|py|json)", text))
    for rel in sorted(cited):
        if (ROOT / rel).exists():
            check(True, f"本地存在：{rel}")
            continue
        elsewhere = sorted(ROOT.parent.glob(f"*/{rel}"))
        if elsewhere:
            print(f"  info 跨 skill 引用：{rel} → {elsewhere[0].parent.parent.name}")
            continue
        check(False, f"引用无法解析：{rel}")


def check_render() -> None:
    try:
        import docx  # noqa: F401
    except ImportError:
        print("  SKIP python-docx 未安装，跳过渲染测试")
        return

    articles = [
        {
            "title": "The Teacher Who Kept a Promise",
            "source": "BBC News",
            "date": "2025-08-23",
            "url": "https://example.com/a",
            "body": ["First paragraph of the story.", "Second paragraph with a quote.", "Third paragraph closing."],
        },
        {
            "title": "A Garden Behind the School",
            "source": "The Guardian",
            "date": "2025-09-01",
            "url": "https://example.com/b",
            "body": ["Opening line.", "Middle line.", "Closing line."],
        },
    ]

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        payload = work / "articles.json"
        payload.write_text(json.dumps(articles, ensure_ascii=False), encoding="utf-8")
        outdir = work / "out"

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--input-json", str(payload), "--output-dir", str(outdir)],
            capture_output=True, text=True,
        )
        check(result.returncode == 0, f"批量生成退出码 0（实际 {result.returncode}）")
        produced = sorted(outdir.glob("*.docx"))
        check(len(produced) == 2, f"生成 2 个 docx（实际 {len(produced)}）")

        if produced:
            from docx import Document

            text = "\n".join(p.text for p in Document(str(produced[0])).paragraphs)
            check(articles[0]["title"] in text, "正文含文章标题")
            check("Second paragraph" in text, "正文含段落内容")
            check(articles[0]["url"] in text, "正文含来源链接")


def main() -> int:
    print("引用完整性：")
    check_references()
    print("渲染：")
    check_render()
    print()
    if failures:
        print(f"FAILED ({len(failures)} 项)")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
