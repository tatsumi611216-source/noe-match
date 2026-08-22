# -*- coding: utf-8 -*-
"""既存記事のシェル（CSS・ヘッダ・フッタ・構造化データの型）を使い回して1記事を組む。

なぜ必要か（2026-08-14）:

記事ページは1本37KBあり、その大半はインラインCSSとヘッダ/フッタの定型部分。
手で複製すると、CSS変数の取りこぼし・パンくずの書き換え漏れ・JSON-LDの
壊れ（8/13にガルガル診断で実際に発生し、GSCの「解析不能な構造化データ」を招いた）
が起きる。**定型部分は触らせず、記事ごとに違う部分だけを差し込む**のがこの器の役割。

生成後は必ず json.loads() でJSON-LDを検証してから書き出す（同じ事故を繰り返さない）。

使い方:
    from build_page import build
    build(slug=..., title=..., desc=..., toc=[...], body=..., faq=[...],
          related=[...], cta={...})
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "articles", "garugaru-ki-itsumade", "index.html")
SITE = "https://www.noe-match.com"


def _shell():
    """テンプレートから、記事に依存しない部分だけを取り出す。

    注意（2026-08-15に実際に踏んだ罠）:
    テンプレートの <head> は「フォント→CSS→JSON-LD→</head>」の順に並ぶ。
    </head> までを丸ごと切り出すと **テンプレート元記事のJSON-LDまで持ってきてしまい**、
    生成した記事が別記事のURL・見出しを名乗るArticle/FAQ/パンくずを抱える。
    JSON-LDとしては構文が正しいためパース検証では検出できない。
    そのため、CSSの切り出しは最初の ld+json の手前で必ず止める。
    """
    h = open(TEMPLATE, encoding="utf-8").read()
    gtag = h[h.find("<!DOCTYPE"):h.find('<meta charset')]
    start = h.find('<link href="https://fonts.googleapis.com')
    ld_at = h.find('<script type="application/ld+json">', start)
    end = ld_at if ld_at > 0 else h.find("</head>")
    style = h[start:end]
    footer = h[h.rfind("<footer"):]
    return gtag, style, footer


def build(slug, title, desc, lead, toc, body, faq, related, cta,
          date="2026年8月15日", iso="2026-08-15", og="/images/garugaru-og.png"):
    gtag, style, footer = _shell()
    url = "%s/articles/%s/" % (SITE, slug)

    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q,
         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    ld_art = {"@context": "https://schema.org", "@type": "Article",
              "headline": title, "description": desc, "image": SITE + og, "url": url,
              "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "inLanguage": "ja",
              "author": {"@type": "Organization", "name": "Noe編集部",
                         "url": SITE + "/about.html"},
              "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": SITE + "/"},
              "datePublished": iso, "dateModified": iso}
    ld_bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "記事一覧", "item": SITE + "/#articles"},
        {"@type": "ListItem", "position": 3, "name": title}]}

    lds = ""
    for d in (ld_faq, ld_art, ld_bc):
        s = json.dumps(d, ensure_ascii=False)
        json.loads(s)  # 書き出す前に必ず検証する
        lds += '<script type="application/ld+json">%s</script>\n' % s

    toc_html = "".join('<li><a href="#%s">%s</a></li>' % (i, t) for i, t in toc)
    faq_html = "".join("<h3>Q%d. %s</h3>\n<p>%s</p>\n" % (n + 1, q, a)
                       for n, (q, a) in enumerate(faq))
    rel_html = "".join('<li><a href="%s">%s</a></li>' % (u, t) for u, t in related)

    html = """%(gtag)s<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(url)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="article">
<meta property="og:url" content="%(url)s">
<meta property="og:image" content="%(site)s%(og)s">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta property="article:published_time" content="%(iso)s">
<meta property="article:modified_time" content="%(iso)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(title)s">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="%(site)s%(og)s">
%(style)s%(lds)s</head>
<body>
<header><div class="header-inner">
<a href="/" class="logo">Noe結婚設計室<span class="logo-badge">2026</span></a>
<nav><a href="/#tools">ツール</a><a href="/articles/">記事一覧</a><a href="/#tools">無料ツール</a><a href="/#faq">FAQ</a><a href="/#about">運営者</a></nav>
</div></header>
<div class="wrap">
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/#articles">記事一覧</a> ＞ %(title)s</div>

<article>
<h1>%(title)s</h1>
<div class="byline"><span class="av">N</span><div>Noe編集部｜結婚まわりのお金と段取りを、公式データで整理するガイドです。<div class="up">公開：%(date)s（最終更新：%(date)s）</div></div></div>
<p class="pr-notice">本記事はアフィリエイト広告を含みます。広告の有無にかかわらず、編集部が有益と判断した情報のみ掲載しています。</p>

%(lead)s

<div class="toc"><div class="toc-h">この記事でわかること</div><ol>%(toc)s</ol></div>

%(body)s

<h2 id="faq">よくある質問</h2>
%(faq)s</article>

<div class="related">
<h2>関連記事・ツール</h2>
<ul>%(rel)s</ul>
</div>
<div class="cta-foot">
<h2>%(cta_h)s</h2>
<p>%(cta_p)s</p>
<a href="%(cta_u)s">%(cta_a)s</a>
</div>
</div>
%(footer)s""" % dict(gtag=gtag, style=style, lds=lds, title=title, desc=desc, url=url,
                     site=SITE, og=og, iso=iso, date=date, lead=lead, toc=toc_html,
                     body=body, faq=faq_html, rel=rel_html, footer=footer,
                     cta_h=cta["h"], cta_p=cta["p"], cta_u=cta["url"], cta_a=cta["a"])

    d = os.path.join(ROOT, "articles", slug)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "index.html")
    open(p, "w", encoding="utf-8").write(html)

    # 書き出したものを読み直して再検証（テンプレ由来の混入も含めて確認する）
    out = open(p, encoding="utf-8").read()
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', out, re.S)
    types = []
    for s in blocks:
        d = json.loads(s)  # ① 構文が壊れていないか
        types.append(d.get("@type"))
        # ② 他記事のURLを名乗っていないか（テンプレのJSON-LDを持ってきた場合に出る）
        u = d.get("url") or d.get("mainEntityOfPage", {}).get("@id", "")
        if u and u != url:
            raise AssertionError("他記事のJSON-LDが混入: %s（期待: %s）" % (u, url))
    # ③ 同じ型が2つ以上ないか（重複はテンプレ混入の典型症状）
    if len(types) != len(set(types)):
        raise AssertionError("JSON-LDの型が重複: %s" % types)
    return p, len(out)
