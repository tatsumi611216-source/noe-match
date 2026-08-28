# -*- coding: utf-8 -*-
import json, re, os

OUT = r"C:/Users/tatsu/noe-match-local/agent/note_html"

LINE_URL = "https://lin.ee/unbDsCR"
LINE_TEXT = "Noe結婚設計室の公式LINE（登録無料）"
SEIKATSUHI = "https://www.noe-match.com/tools/seikatsuhi-simulator/"
SHIKIN = "https://www.noe-match.com/tools/kekkon-shikin-keisanki/"
YARUKOTO = "https://www.noe-match.com/tools/kekkon-yarukoto/"
NYUSEKI = "https://www.noe-match.com/tools/nyuseki-calendar/"

def build(blocks):
    """blocks: list of ('p', text) or ('h2', text). text may contain a single {A}/{B}/{C} placeholder replaced by <a> already embedded as raw html string."""
    parts = []
    for tag, text in blocks:
        parts.append(f"<{tag}>{text}</{tag}>")
    return "".join(parts)

def stats(html):
    # strip tags
    text = re.sub(r"<[^>]+>", "", html)
    text_nospace = re.sub(r"\s+", "", text)
    h2_count = len(re.findall(r"<h2>", html))
    a_count = len(re.findall(r"<a ", html))
    p_count = len(re.findall(r"<p>", html))
    empty_p = len(re.findall(r"<p>\s*</p>", html))
    strong = "<strong" in html or "<ul" in html or "<li" in html
    return {
        "chars": len(text_nospace),
        "h2": h2_count,
        "a": a_count,
        "p": p_count,
        "empty_p": empty_p,
        "forbidden_tags": strong,
    }

def save(slug, title, tags, html):
    path_html = os.path.join(OUT, f"{slug}.html")
    path_json = os.path.join(OUT, f"{slug}.json")
    with open(path_html, "w", encoding="utf-8") as f:
        f.write(html)
    st = stats(html)
    data = {"title": title, "tags": tags, "chars": st["chars"]}
    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return st

if __name__ == "__main__":
    print("gen module loaded")
