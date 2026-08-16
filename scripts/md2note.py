# -*- coding: utf-8 -*-
"""note入稿用に、下書きmdをnoteエディタへ貼れるHTMLへ変換する。

noteのエディタは paste イベント一発で流し込むのが安全（execCommandのループは
クラッシュする・2026-07の実測）。またプレーンテキストで貼ると見出しやリンクが
失われるため、text/html で渡す。

空行を段落の区切りにするが、**空段落は作らない**
（「スペースが多くて読みにくい」というFBの原因が空段落だったため）。

使い方:
    python scripts/md2note.py agent/note_drafts/01_gijikka.md
"""
import html
import re
import sys


def conv(md):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    out, lines, i = [], md.splitlines(), 0
    title = None
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("# ") and title is None:
            title = ln[2:].strip()
            i += 1
            continue
        if ln.startswith("## "):
            out.append("<h2>%s</h2>" % inline(ln[3:].strip()))
            i += 1
            continue
        if ln.strip() == "---":
            i += 1
            continue
        if ln.startswith(("- ", "* ")):
            items = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                items.append("<li>%s</li>" % inline(lines[i].strip()[2:]))
                i += 1
            out.append("<ul>%s</ul>" % "".join(items))
            continue
        # 通常段落（連続行は1段落にまとめる）
        buf = [ln]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "-", "*")) \
                and lines[i].strip() != "---":
            buf.append(lines[i].rstrip())
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(buf)))
    return title, "".join(out)


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = s.replace("▶ ", "")
    return s


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    t, h = conv(open(sys.argv[1], encoding="utf-8").read())
    print("TITLE:", t)
    print("CHARS:", len(re.sub(r"<[^>]+>", "", h)))
    print("HTML:")
    print(h)
