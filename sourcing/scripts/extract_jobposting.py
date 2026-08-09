#!/usr/bin/env python3
"""HTMLから schema.org JobPosting（JSON-LD）を抽出して正規化レコードにする。

企業が自社採用ページに埋め込む機械可読な求人データを対象とする。
Google しごと検索向けに広く普及しており、規約クリーンかつ構造が安定している。

usage(単体): python3 extract_jobposting.py page.html --source mysite --company "㈱ABC"
"""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path

_LD_JSON_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)


def _iter_jsonld_objects(page_html: str):
    """ページ内の JSON-LD ブロックを全て走査し、辞書を1つずつ yield する。"""
    for block in _LD_JSON_RE.findall(page_html):
        text = html.unescape(block.strip())
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                if "@graph" in node:
                    stack.extend(node["@graph"] if isinstance(node["@graph"], list) else [node["@graph"]])
                yield node


def _types(node: dict) -> set[str]:
    t = node.get("@type", "")
    if isinstance(t, list):
        return {str(x) for x in t}
    return {str(t)}


def _text(v):
    if isinstance(v, dict):
        return v.get("name") or v.get("value") or ""
    if isinstance(v, list):
        return ", ".join(_text(x) for x in v if _text(x))
    return str(v) if v is not None else ""


def _salary(node: dict):
    """baseSalary から月給換算の下限/上限（円）を素朴に取り出す。取れなければ (None, None)。"""
    bs = node.get("baseSalary")
    if not isinstance(bs, dict):
        return None, None
    val = bs.get("value")
    if not isinstance(val, dict):
        return None, None

    def to_int(x):
        try:
            return int(float(x))
        except (TypeError, ValueError):
            return None

    lo = to_int(val.get("minValue"))
    hi = to_int(val.get("maxValue"))
    single = to_int(val.get("value"))
    if lo is None and hi is None and single is not None:
        lo = hi = single
    return lo, hi


def _location(node: dict) -> str:
    loc = node.get("jobLocation")
    if isinstance(loc, list):
        loc = loc[0] if loc else None
    if isinstance(loc, dict):
        addr = loc.get("address")
        if isinstance(addr, dict):
            parts = [addr.get("addressRegion"), addr.get("addressLocality"), addr.get("streetAddress")]
            return "".join(p for p in parts if p)
        return _text(addr)
    return ""


def extract(page_html: str, source_site: str, default_company: str = "") -> list[dict]:
    """ページから JobPosting レコードのリストを返す。"""
    records = []
    for node in _iter_jsonld_objects(page_html):
        if "JobPosting" not in _types(node):
            continue
        title = _text(node.get("title"))
        if not title:
            continue
        org = _text(node.get("hiringOrganization")) or default_company
        url = node.get("url") or node.get("@id") or ""
        job_id = str(node.get("identifier") or "") or hashlib.sha1(
            (org + "|" + title + "|" + url).encode("utf-8")
        ).hexdigest()[:16]
        lo, hi = _salary(node)
        records.append({
            "source_site": source_site,
            "source_job_id": job_id,
            "company_name": org.strip(),
            "title": title.strip(),
            "employment_type": _text(node.get("employmentType")),
            "location": _location(node),
            "salary_min": lo,
            "salary_max": hi,
            "url": url,
            "posted_at": (node.get("datePosted") or "")[:10] or None,
        })
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_file")
    parser.add_argument("--source", required=True)
    parser.add_argument("--company", default="")
    args = parser.parse_args()
    recs = extract(Path(args.html_file).read_text(encoding="utf-8"), args.source, args.company)
    print(json.dumps(recs, ensure_ascii=False, indent=2))
