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
    """script/style/目次を除いた本文の実文字数を数える（空白は除外）

    目次は本文の見出しを再掲したナビゲーションであり、内容量ではない。
    含めると加筆していないのに文字数が増え、品質バックログが自動的に痩せてしまう。
    """
    stripped = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S)
    stripped = re.sub(r'<nav class="toc".*?</nav>', '', stripped, flags=re.S)
    # 冒頭の広告表記も全記事共通の定型文なので内容量には数えない
    stripped = re.sub(r'<p class="pr-notice">.*?</p>', '', stripped, flags=re.S)
    # 中盤CTAも定型の訴求文であり内容量ではない（既存の記事末CTAは従来どおり数え、
    # 過去の計測値と比較できるようにしておく）
    stripped = re.sub(r'<div class="cta-mid">.*?</div>', '', stripped, flags=re.S)
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


_REVENUE_CACHE = set()


def revenue_slugs():
    """アフィリエイトリンクを持つ記事＝収益記事のスラッグ集合（1度だけ走査）"""
    global _REVENUE_CACHE
    if _REVENUE_CACHE:
        return _REVENUE_CACHE
    found = set()
    for slug in live_slugs():
        path = os.path.join(ROOT, 'articles', slug, 'index.html')
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8', errors='replace') as f:
            if AFFILIATE_RE.search(f.read()):
                found.add(slug)
    _REVENUE_CACHE = found
    return found


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

    # 景表法のステマ規制対応：アフィリエイトリンクを持つ記事は、広告である旨を
    # 記事の冒頭（h1直後）に明示する。フッターの【PR】だけでは「明瞭に表示」といえない。
    if aff_urls and 'class="pr-notice"' not in html:
        errors.append('アフィリエイトリンクがあるのに冒頭の広告表記（.pr-notice）が無い')

    # 6,000〜10,000字の記事で目次が無いと、読者が必要な節に到達できない
    if 'class="toc"' not in html:
        warnings.append('目次（.toc）が無い')

    # タイトルは日本語SERPで30〜32字前後で切れる。長さそのものより語順が問題で、
    # 【20XX年版】を途中に置くと、その後ろの差別化フレーズが丸ごと見えなくなる。
    tm = re.search(r'<title>(.*?)</title>', html, re.S)
    if tm:
        title = re.sub(r'\s+', ' ', tm.group(1)).strip()
        ym = re.search(r'【20\d\d年(?:版|最新)?】', title)
        if ym and ym.end() < len(title) - 1:
            errors.append('タイトルの【年号】が末尾でない（後続の語がSERPで切れる）')
        # 主キーワード＝最初の区切りまでの節。ここが32字を超えると検索語が見えない
        head = re.split(r'[｜|？?]', title)[0]
        if len(head) > 32:
            errors.append(f'タイトルの主キーワード部が{len(head)}字（32字以内に収める）')

    # TOCのアンカーが実在するh2のidを指しているか
    nav = re.search(r'<nav class="toc".*?</nav>', html, re.S)
    if nav:
        targets = set(re.findall(r'href="#([^"]+)"', nav.group(0)))
        ids = set(re.findall(r'<h2[^>]*id="([^"]+)"', html))
        if targets - ids:
            errors.append(f'目次のアンカーが実在しない: {sorted(targets - ids)[:3]}')

    # 収益記事へ1クリックで到達できない記事は、集客しても収益に繋がらない
    if not aff_urls and internal and not (internal & revenue_slugs()):
        warnings.append('収益記事へ1クリックで到達できない（内部リンクが全て非収益記事）')

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


def audit_index_groups():
    """index.html の記事一覧グループを検査する（2026-08-09追加）。

    なぜ必要か：index.html には生成スクリプトが無く、エージェントが手で編集している。
    **グループを2つに分割したとき、arc-no の通し番号を振り直さず、
    件数表記も分割前の合計のまま残る**という事故が起きていた。
    2026-08-09時点で7グループが壊れていた（例：プロフィール10本に「19記事」と表記され、
    続くデート・交際9本の番号が 11〜19 から始まっていた。10+9=19 が前半に付いていた）。

    見た目の破損なので記事の中身では気づけない。機械で止める。
    """
    errors = []
    # 2026-08-18 以降、記事一覧グループは articles/index.html（記事ハブ）にあり、
    # 見出しは h2。トップの index.html は「全N記事」の数字だけ持つ。
    hub = os.path.join(ROOT, 'articles', 'index.html')
    if not os.path.exists(hub):
        hub = os.path.join(ROOT, 'index.html')
    with open(hub, encoding='utf-8') as f:
        html = f.read()

    parts = re.split(r'(<h[23] [^>]*>.*?</h[23]>)', html, flags=re.S)
    cur = None
    total = 0
    for seg in parts:
        m = re.match(r'<h[23] [^>]*>(.*?)<span[^>]*>（(\d+)記事）</span></h[23]>', seg, re.S)
        if m:
            cur = (re.sub(r'<[^>]+>', '', m.group(1)).strip(), int(m.group(2)))
            continue
        if cur is None:
            continue
        name, declared = cur
        cur = None
        nos = [int(x) for x in re.findall(
            r'class="arc-link"><span class="arc-no">(\d+)</span>', seg)]
        total += len(nos)
        if declared != len(nos):
            errors.append(
                f'index.html「{name}」の件数表記が{declared}記事だが実数は{len(nos)}本')
        if nos and nos != list(range(1, len(nos) + 1)):
            errors.append(
                f'index.html「{name}」の通し番号が連番でない（{nos[0]}〜{nos[-1]}／{len(nos)}本）'
                'グループを分割したら番号を1から振り直すこと')

    # 「全N記事」はトップとハブの両方に現れうる。グループ合計（無ければ稼働記事数）と照合
    if total == 0:
        total = len(live_slugs())
    for name in ('index.html', os.path.join('articles', 'index.html')):
        hp = os.path.join(ROOT, name)
        if not os.path.exists(hp):
            continue
        with open(hp, encoding='utf-8') as f:
            for m in re.finditer(r'全(\d+)記事', f.read()):
                if int(m.group(1)) != total:
                    errors.append(f'{name} の「全{m.group(1)}記事」が実数{total}本と不一致')
                    break
    return errors


def audit_structure():
    """記事ディレクトリ / sitemap / index.html / redirects.json の整合を検査"""
    errors = []
    with open(os.path.join(ROOT, 'redirects.json'), encoding='utf-8') as f:
        redirects = json.load(f)
    # 2026-08-18 にトップをツール中心へ再設計し、記事の全件一覧は
    # articles/index.html（記事ハブ）へ移った。どちらかから辿れればよい。
    indexed = set()
    for hub in ('index.html', os.path.join('articles', 'index.html')):
        hp = os.path.join(ROOT, hub)
        if os.path.exists(hp):
            with open(hp, encoding='utf-8') as f:
                indexed |= set(re.findall(r'href="/articles/([^/"]+)/?"', f.read()))

    sitemap = set(live_slugs())
    dirs = {d for d in os.listdir(os.path.join(ROOT, 'articles'))
            if os.path.isdir(os.path.join(ROOT, 'articles', d))}
    live_dirs = dirs - set(redirects)

    for slug in sorted(live_dirs - sitemap):
        errors.append(f'記事ディレクトリが sitemap.xml に無い: {slug}')
    for slug in sorted(sitemap - dirs):
        errors.append(f'sitemap.xml のURLに実体が無い: {slug}')
    for slug in sorted(sitemap - indexed):
        errors.append(f'sitemap.xml にあるが index.html / articles/index.html のどちらからも未リンク: {slug}')
    # 稼働記事がリダイレクト元として登録されていると server.py が301で飛ばしてしまう
    for slug in sorted(sitemap & set(redirects)):
        errors.append(f'稼働記事が redirects.json のリダイレクト元になっている: {slug}')

    errors.extend(audit_index_groups())

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

    # lastmod は記事の JSON-LD dateModified と一致していなければならない。
    # build_articles.py が全URLに実行日を一律で書く作りだったため、
    # 2026-08-01時点で60本がズレていた（50本は実際より新しい＝虚偽の鮮度、
    # 10本は寄せ直し済みなのに更新が伝わっていない）。放置すると lastmod 自体が
    # 信用されなくなるので、ズレたままコミットできないようにする。
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    try:
        import sitemap_sync
    except ImportError:
        sitemap_sync = None
    if sitemap_sync:
        for name in sitemap_sync.SITEMAPS:
            stale = sitemap_sync.diffs(name)
            if stale:
                sample = ', '.join(
                    f'{u.rsplit("/articles/", 1)[-1].rstrip("/")}({cur}→{want})'
                    for u, cur, want in stale[:3])
                errors.append(
                    f'{name} の lastmod が dateModified と不一致: {len(stale)}件'
                    f'（{sample} ...）→ python3 scripts/sitemap_sync.py で同期する')
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
