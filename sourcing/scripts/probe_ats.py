#!/usr/bin/env python3
"""求人が取れていない企業について、ATS上の採用ページが実在するかを総当たりで確認する。

企業サイトがJS描画だと採用ページのHTMLにATSリンクが現れず、クローラが辿れない。
一方ATSのURLは `hrmos.co/pages/<スラッグ>/jobs` のように規則的なので、企業ドメインから
スラッグ候補を作って実在確認する。「200が返り、かつ JobPosting が取れた」ものだけを
採用URLとして採る（推測をそのまま登録しない）。

usage: python3 probe_ats.py --seeds ../seeds/multi_industry.csv [--out ../seeds/ats_targets.csv]
"""
import argparse
import csv
from pathlib import Path
from urllib.parse import urlparse

from common import DEFAULT_DB, connect, normalize_company_name
from crawl import _Budget, _make_fetch
from extract_jobposting import extract
from http_cache import HttpCache

# スラッグの手前で落とす接頭ラベルと、末尾のトップレベル相当ラベル
_PREFIX = {"www", "about", "corp", "corporate", "info", "global", "holdings",
           "group", "jobs", "careers", "career", "recruit", "hello-world", "en"}
_SUFFIX = {"com", "jp", "co", "net", "org", "info", "io", "ai", "tech", "biz",
           "me", "life", "inc", "plus", "work", "team", "dev", "app"}

# <スラッグ> を埋めると求人一覧になるATSのURL型
PATTERNS = (
    "https://hrmos.co/pages/{slug}/jobs",
    "https://herp.careers/v1/{slug}",
    "https://open.talentio.com/r/1/c/{slug}/homes/1",
    "https://recruit.jobcan.jp/{slug}",
    "https://www.wantedly.com/companies/{slug}/projects",
)


def slug_candidates(*urls: str) -> list[str]:
    """企業サイト・採用ページのホスト名からスラッグ候補を作る。"""
    out = []
    for url in urls:
        host = urlparse(url or "").netloc.lower()
        if not host:
            continue
        labels = [x for x in host.split(".") if x]
        while labels and labels[-1] in _SUFFIX:
            labels.pop()
        while labels and labels[0] in _PREFIX:
            labels.pop(0)
        if not labels:
            continue
        core = labels[-1]
        for cand in (core, core.replace("-", "")):
            if cand and cand not in out:
                out.append(cand)
    return out


def probe(name: str, slugs: list[str], fetch) -> tuple[str, int] | None:
    """候補URLを順に叩き、JobPosting が取れた最初のURLを返す。"""
    for slug in slugs:
        for pattern in PATTERNS:
            url = pattern.format(slug=slug)
            html, state = fetch(url)
            if state != "fetched" or not html:
                continue
            records = extract(html, "ats-probe", name)
            if records:
                return url, len(records)
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", action="append", required=True)
    parser.add_argument("--db", default=str(DEFAULT_DB),
                        help="既に求人が取れている企業を探索対象から外すために参照する")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent.parent
                                             / "seeds" / "ats_targets.csv"))
    args = parser.parse_args()

    # 既に求人が取れている企業は探索しない（無駄打ちと重複取り込みを避ける）
    have_jobs = set()
    if Path(args.db).exists():
        conn = connect(args.db)
        try:
            have_jobs = {r[0] for r in conn.execute(
                """SELECT c.name_normalized FROM companies c
                   JOIN job_postings jp ON jp.company_id=c.id AND jp.is_active=1
                   GROUP BY c.id""")}
        finally:
            conn.close()

    cache = HttpCache()
    rows, found = [], []
    for seed_path in args.seeds:
        with Path(seed_path).open(encoding="utf-8-sig", newline="") as f:
            rows.extend(list(csv.DictReader(f)))

    print(f"シード{len(rows)}社 / 既に求人が取れている{len(have_jobs)}社は除外 "
          f"/ URL型{len(PATTERNS)}種")
    for row in rows:
        name = (row.get("name") or "").strip()
        slugs = slug_candidates(row.get("website", ""), row.get("careers_url", ""))
        if not name or not slugs:
            continue
        if normalize_company_name(name) in have_jobs:
            continue
        budget = _Budget(len(slugs) * len(PATTERNS) + 2)
        hit = probe(name, slugs, _make_fetch(cache, budget, force=False))
        if hit:
            url, n = hit
            found.append({"name": name, "careers_url": url,
                          "website": row.get("website", ""),
                          "is_listed": row.get("is_listed", ""),
                          "industry": row.get("industry", ""),
                          "prefecture": row.get("prefecture", ""),
                          "source_list": "ats-probe"})
            print(f"  [FOUND] {name}: {url} （求人{n}件・候補{slugs}）")
        else:
            print(f"  [ - ]   {name}: 候補{slugs} は全滅")
    cache.save()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name", "careers_url", "website",
                                          "is_listed", "industry", "prefecture",
                                          "source_list"])
        w.writeheader()
        w.writerows(found)
    print(f"\nATS実在確認: {len(found)}社 → {out}")


if __name__ == "__main__":
    main()
