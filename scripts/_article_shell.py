# -*- coding: utf-8 -*-
"""データ記事の共通シェル（2026-08-27 新設）

データ記事の型は「複数の公表値を横断で1枚の表にする＋出典＋確認日」。
実測ではこの型の流入はAI（chatgpt/copilot）とBingがほぼ全部で、
Google/Yahooは2セッションしかない。Google順位ではなくAIの引用を取りに行くので、
数値・出典・確認日・単位を1か所にまとめ、引用しやすい形にする。

factory_audit が求める条件（冒頭の広告表記・他記事への内部リンク3本以上・
FAQ5問以上・canonical・目次アンカーの実在）を満たす形で組み立てる。
"""
import io
import json
import os

OISIX = "https://px.a8.net/svt/ejp?a8mat=45C0YR+2VBK6Q+3250+5YZ77"


def css():
    shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
    return shell[shell.find("<style>"):shell.find("</style>") + 8]


HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VLQBH0S1SL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-VLQBH0S1SL');document.addEventListener('click',function(e){{var a=e.target.closest&&e.target.closest('a[href*="px.a8.net"],a[href*="t.afi-b.com"]');if(a){{try{{gtag('event','aff_click',{{link_domain:(a.href.indexOf('a8.net')>-1?'a8':'afb'),page_slug:location.pathname}});}}catch(x){{}}}}}},true);</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{ogd}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{ogd}">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@500;600;700;900&display=swap" rel="stylesheet">
{css}
<style>table.cmp td{{vertical-align:top;font-size:.86rem;line-height:1.85}}
table.cmp td.n{{text-align:right;font-weight:700;color:#7c2e42;white-space:nowrap}}
.srcline{{font-size:.78rem;color:#6b7178;line-height:1.9;margin:8px 0 0}}</style>
<script type="application/ld+json">{faqld}</script>
<script type="application/ld+json">{artld}</script>
<script type="application/ld+json">{bcld}</script>
</head>
<body>
<header><div class="header-inner">
<a href="/" class="logo">Noe結婚設計室<span class="logo-badge">2026</span></a>
<nav><a href="/#tools">ツール</a><a href="/articles/">記事一覧</a><a href="/#faq">FAQ</a><a href="/#about">運営者</a></nav>
</div></header>
<div class="wrap">
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/articles/">記事一覧</a> ＞ {h1}</div>
<article>
<h1>{h1}</h1>
<p style="font-size:.78rem;color:#8a8f95;margin:6px 0 20px">公開 {today}／出典は公的統計。{checked}に各原典で確認</p>
<p class="pr-notice">本ページはプロモーションを含みます。記事内に広告主から成果報酬を受け取るリンクが含まれます。掲載内容は編集部の基準で作成しており、報酬の有無で評価を変えていません。</p>
{body}
<div style="border:1px solid #e3ddd3;border-radius:6px;padding:22px 24px;margin:32px 0;background:#faf8f5">
<p style="font-size:.7rem;color:#999;margin:0 0 6px">PR</p>
<p style="font-weight:900;margin:0 0 6px;color:#1d242b">{pr_head}</p>
<p style="font-size:.86rem;color:#5a6068;margin:0 0 16px;line-height:1.9">{pr_body}</p>
<a href="{oisix}" rel="sponsored noopener" target="_blank" style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;padding:13px 32px;text-decoration:none">Oisixのおためしセットを見る</a>
<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">食材宅配サービス。本記事の統計とは関係ありません</p>
</div>
</article>
<!-- LINE-CTA -->
<section id="line-cta" style="max-width:680px;margin:56px auto 64px;padding:36px 28px;background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;">
  <p style="margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif;">NOE OFFICIAL LINE</p>
  <p style="margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5;">公表値が更新されたらお知らせします</p>
  <p style="margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;">国勢調査・人口動態統計・白書など、この記事で使っている統計の更新を月1回まとめて配信します。<br>調べてほしい数字があれば、追加後そのままトークでどうぞ。</p>
  <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{{gtag('event','line_add_click',{{article:'{slug}'}});}}catch(e){{}}"
     style="display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;font-size:15px;font-weight:600;text-decoration:none;">友だち追加する</a>
  <p style="margin:14px 0 0;font-size:11px;color:#8a8f95;">登録は無料・配信は月1回だけ。いつでも解除できます。</p>
</section>
</div>
<footer><div class="footer-inner">
<div><a href="/">ホーム</a><a href="/articles/">記事一覧</a><a href="/about.html">運営者情報</a><a href="/privacy-policy.html">プライバシー</a><a href="/disclaimer.html">免責事項</a></div>
<p class="footer-disc">※本記事は公的統計の公表値にもとづく整理です（{checked}確認）。統計は改定・更新されるため、引用の際は原典と公表年をご確認ください。<strong style="color:#cda">【PR】</strong>本サイトはアフィリエイト広告を含みます。<br>&copy; 2026 Noe結婚設計室</p>
</div></footer>
<button id="top" onclick="scrollTo({{top:0,behavior:'smooth'}})">↑</button>
</body>
</html>"""


def faq_html(faq):
    return "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a)
                     for i, (q, a) in enumerate(faq))


def source_list(sources):
    """[(url, label), ...] を出典リストにする"""
    items = "\n".join(
        '<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % (u, l)
        for u, l in sources)
    return ('<h2 id="src">出典</h2>\n<p>本記事の数値はすべて次の公的統計の公表値です。'
            '統計ごとに調査の対象・周期・母集団が違うため、異なる統計の数値を掛け合わせないでください。</p>\n'
            '<ul style="font-size:.86rem;line-height:2">\n%s\n</ul>' % items)


def table(headers, rows, aligns=None):
    aligns = aligns or [""] * len(headers)
    th = "".join("<th>%s</th>" % h for h in headers)
    trs = "".join(
        "<tr>" + "".join('<td%s>%s</td>' % (' class="n"' if aligns[i] == "n" else "", c)
                         for i, c in enumerate(r)) + "</tr>"
        for r in rows)
    return ('<div class="table-scroll"><table class="cmp"><thead><tr>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>' % (th, trs))


def write(slug, title, h1, desc, ogd, faq, body, today, checked,
          pr_head, pr_body):
    url = "https://www.noe-match.com/articles/%s/" % slug
    faqld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in faq]}, ensure_ascii=False)
    artld = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": title,
        "description": desc, "inLanguage": "ja",
        "datePublished": today, "dateModified": today,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "author": {"@type": "Organization", "name": "Noe編集部",
                   "url": "https://www.noe-match.com/about.html"},
        "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                      "url": "https://www.noe-match.com/"}}, ensure_ascii=False)
    bcld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                       "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
        {"@type": "ListItem", "position": 2, "name": "記事一覧", "item": "https://www.noe-match.com/articles/"},
        {"@type": "ListItem", "position": 3, "name": h1}]}, ensure_ascii=False)
    html = HEAD.format(title=title, desc=desc, ogd=ogd, url=url, css=css(),
                       faqld=faqld, artld=artld, bcld=bcld, h1=h1,
                       today=today, checked=checked, body=body, slug=slug,
                       oisix=OISIX, pr_head=pr_head, pr_body=pr_body)
    os.makedirs("articles/%s" % slug, exist_ok=True)
    io.open("articles/%s/index.html" % slug, "w", encoding="utf-8").write(html)
    print("written: articles/%s/index.html  %d chars" % (slug, len(html)))
