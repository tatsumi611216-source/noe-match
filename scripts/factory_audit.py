#!/usr/bin/env python3
"""記事工場の出荷検品スクリプト（2026-07-30制定）

AGENT.md の品質基準のうち、機械的に判定できるものを全記事に対して検査する。
週次実行の Phase 1 の最後（コミット前）に必ず実行し、FAIL が出たら
その記事を出荷せず修正する。

既知の未達分（agent/quality_backlog.md に登録済みのもの）は「既知バックログ」として
分けて表示し、終了コードには算入しない。ゲートが常時赤だと検品として機能しないため。
**バックログに載っていない新規の違反が出た時だけ赤くなる。**

使い方:
    python3 scripts/factory_audit.py            # 検査してサマリを表示
    python3 scripts/factory_audit.py --list     # 違反記事を全件列挙（既知分も含む）
    python3 scripts/factory_audit.py --strict   # 既知バックログも違反として扱う
    python3 scripts/factory_audit.py --json PATH  # 結果をJSONで保存

終了コード: 新規違反または構造エラーが1件でもあれば 1、なければ 0
"""
import argparse
import json
import os
import re
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# AGENT.md の品質基準
MIN_CHARS = 6000          # 本文文字数の下限
HARD_MIN_CHARS = 4000     # これを下回るものは最優先で是正
MIN_INTERNAL_LINKS = 3    # 内部リンク本数
MIN_FAQ = 5               # FAQ設問数
MAX_AFFILIATE = 4         # 1記事あたりアフィリエイトリンク上限
MAX_AFFILIATE_YMYL = 3    # YMYL寄りクラスタの上限
MAX_PER_ADVERTISER = 2    # 同一広告主の上限

# YMYL寄りクラスタ（AGENT.md「CTA密度のガードレール」）
YMYL_PATTERNS = (
    'tantei', 'uwaki', 'rikon', 'sokou', 'hoken', 'loan', 'ninkatsu',
    'myseed', 'mitocore', 'mitas',
)

AFFILIATE_RE = re.compile(r'https?://(?:t\.afi-b\.com|px\.a8\.net)[^"\']*')
ADVERTISER_RE = re.compile(r'a8mat=([A-Za-z0-9+]+)|visit\.php\?a=([^&"\']+)')


def body_text(html):
    """script/style を除いた本文の実文字数を数える（空白は除外）"""
    stripped = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S)
    return re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', stripped))


def advertiser_key(url):
    m = ADVERTISER_RE.search(url)
    if not m:
        return url
    return m.group(1) or m.group(2)


def is_ymyl(slug):
    return any(p in slug for p in YMYL_PATTERNS)


def known_backlog():
    """agent/quality_backlog.md に是正待ちとして登録済みのスラッグ集合"""
    path = os.path.join(ROOT, 'agent', 'quality_backlog.md')
    if not os.path.exists(path):
        return set()
    with open(path, encoding='utf-8') as f:
        text = f.read()
    slugs = set(re.findall(r'^\|\s*([a-z0-9][a-z0-9-]+)\s*\|', text, re.M))
    slugs |= set(re.findall(r'([a-z0-9][a-z0-9-]+)（\d+字）', text))
    return slugs


def live_slugs():
    """sitemap.xml に載っている＝出荷済みの記事スラッグ"""
    with open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8') as f:
        return sorted(set(re.findall(r'/articles/([^/]+)/</loc>', f.read())))


def audit_article(slug):
    path = os.path.join(ROOT, 'articles', slug, 'index.html')
    if not os.path.exists(path):
        return {'slug': slug, 'errors': ['index.html が存在しない'], 'warnings': []}

    with open(path, encoding='utf-8', errors='replace') as f:
        html = f.read()

    text = body_text(html)
    aff_urls = AFFILIATE_RE.findall(html)
    advertisers = {}
    for url in aff_urls:
        advertisers[advertiser_key(url)] = advertisers.get(advertiser_key(url), 0) + 1
    internal = set(re.findall(r'href="/articles/([^/"]+)/', html))
    internal.discard(slug)
    faq_count = len(re.findall(r'"@type"\s*:\s*"Question"', html))
    cap = MAX_AFFILIATE_YMYL if is_ymyl(slug) else MAX_AFFILIATE

    errors, warnings = [], []

    if len(text) < HARD_MIN_CHARS:
        errors.append(f'本文 {len(text)}字（下限{MIN_CHARS}字・最優先是正ライン{HARD_MIN_CHARS}字を下回る）')
    elif len(text) < MIN_CHARS:
        warnings.append(f'本文 {len(text)}字（下限{MIN_CHARS}字に未達）')

    if len(internal) < MIN_INTERNAL_LINKS:
        errors.append(f'内部リンク {len(internal)}本（最低{MIN_INTERNAL_LINKS}本）')
    if faq_count < MIN_FAQ:
        errors.append(f'FAQ {faq_count}問（最低{MIN_FAQ}問）')
    if len(aff_urls) > cap:
        errors.append(f'アフィリエイトリンク {len(aff_urls)}箇所（上限{cap}箇所）')
    for adv, n in advertisers.items():
        if n > MAX_PER_ADVERTISER:
            errors.append(f'同一広告主 {adv} が {n}箇所（上限{MAX_PER_ADVERTISER}箇所）')

    for label, needle in (
        ('canonical', 'rel="canonical"'),
        ('og:title', 'og:title'),
        ('BreadcrumbList', 'BreadcrumbList'),
        ('FAQPage', 'FAQPage'),
    ):
        if needle not in html:
            errors.append(f'{label} が無い')

    if 'BlogPosting' not in html:
        warnings.append('JSON-LD が BlogPosting でない（テンプレ分岐）')

    return {
        'slug': slug,
        'chars': len(text),
        'affiliate': len(aff_urls),
        'internal_links': len(internal),
        'faq': faq_count,
        'blogposting': 'BlogPosting' in html,
        'ymyl': is_ymyl(slug),
        'errors': errors,
        'warnings': warnings,
    }


def audit_structure():
    """記事ディレクトリ / sitemap / index.html / redirects.json の整合を検査"""
    errors = []
    with open(os.path.join(ROOT, 'redirects.json'), encoding='utf-8') as f:
        redirects = json.load(f)
    with open(os.path.join(ROOT, 'index.html'), encoding='utf-8') as f:
        indexed = set(re.findall(r'href="/articles/([^/"]+)/?"', f.read()))

    sitemap = set(live_slugs())
    dirs = {d for d in os.listdir(os.path.join(ROOT, 'articles'))
            if os.path.isdir(os.path.join(ROOT, 'articles', d))}
    live_dirs = dirs - set(redirects)

    for slug in sorted(live_dirs - sitemap):
        errors.append(f'記事ディレクトリが sitemap.xml に無い: {slug}')
    for slug in sorted(sitemap - dirs):
        errors.append(f'sitemap.xml のURLに実体が無い: {slug}')
    for slug in sorted(sitemap - indexed):
        errors.append(f'sitemap.xml にあるが index.html から未リンク: {slug}')
    # 稼働記事がリダイレクト元として登録されていると server.py が301で飛ばしてしまう
    for slug in sorted(sitemap & set(redirects)):
        errors.append(f'稼働記事が redirects.json のリダイレクト元になっている: {slug}')

    # sitemap-all.xml は sitemap.xml と同一URL集合であることが前提
    all_path = os.path.join(ROOT, 'sitemap-all.xml')
    if os.path.exists(all_path):
        with open(all_path, encoding='utf-8') as f:
            sm_all = set(re.findall(r'/articles/([^/]+)/</loc>', f.read()))
        if sm_all != sitemap:
            errors.append(
                f'sitemap-all.xml と sitemap.xml のURL集合が不一致'
                f'（差分 {len(sm_all ^ sitemap)}件）'
            )
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true', help='違反記事を全件列挙する')
    parser.add_argument('--strict', action='store_true',
                        help='既知バックログも違反として扱う')
    parser.add_argument('--json', metavar='PATH', help='結果をJSONで保存する')
    args = parser.parse_args()

    results = [audit_article(s) for s in live_slugs()]
    structure = audit_structure()
    backlog = set() if args.strict else known_backlog()

    all_failed = [r for r in results if r['errors']]
    failed = [r for r in all_failed if r['slug'] not in backlog]
    known = [r for r in all_failed if r['slug'] in backlog]
    warned = [r for r in results if r['warnings'] and not r['errors']]
    chars = [r['chars'] for r in results if 'chars' in r]

    print(f'稼働記事: {len(results)}本')
    print(f'本文文字数: 中央値 {statistics.median(chars):.0f}字 / '
          f'{MIN_CHARS}字未満 {sum(c < MIN_CHARS for c in chars)}本 / '
          f'{HARD_MIN_CHARS}字未満 {sum(c < HARD_MIN_CHARS for c in chars)}本')
    print(f'アフィリエイト設置: {sum(r.get("affiliate", 0) > 0 for r in results)}本 / '
          f'総設置 {sum(r.get("affiliate", 0) for r in results)}箇所')
    print(f'JSON-LD が BlogPosting: {sum(r.get("blogposting", False) for r in results)}本')
    print()
    print(f'構造エラー: {len(structure)}件')
    for e in structure:
        print(f'  [STRUCT] {e}')
    print(f'新規エラー(FAIL): {len(failed)}本 / '
          f'既知バックログ: {len(known)}本 / 警告(WARN): {len(warned)}本')

    for r in failed:
        print(f'  [FAIL] {r["slug"]}: ' + ' / '.join(r['errors']))
    if args.list:
        for r in known:
            print(f'  [BACKLOG] {r["slug"]}: ' + ' / '.join(r['errors']))
        for r in warned:
            print(f'  [WARN] {r["slug"]}: ' + ' / '.join(r['warnings']))

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump({'structure': structure, 'articles': results,
                       'backlog': sorted(backlog)}, f, ensure_ascii=False, indent=1)
        print(f'\n結果を {args.json} に保存した')

    if failed or structure:
        return 1
    if known:
        print('\n新規違反なし。既知バックログは agent/quality_backlog.md で消化する。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
