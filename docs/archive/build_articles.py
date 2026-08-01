# -*- coding: utf-8 -*-
"""48本のmarkdownソースから、サイト統一デザインのHTML記事を生成する。"""
import re, json, html, shutil, sys
from pathlib import Path

SRC = Path(r"C:/Users/tatsu/matching-app/article-system/output")
DEPLOY = Path(r"C:/Users/tatsu/Desktop/noe-match-deploy")
ART_OUT = DEPLOY / "articles"
IMG_OUT = DEPLOY / "images"
DOMAIN = "https://www.noe-match.com"

# 連番 -> content-matched スラッグ
SLUGS = {
 1:"matching-app-ranking", 2:"price-comparison", 3:"safety-guide",
 4:"pairs-guide", 5:"pairs-women", 6:"pairs-men",
 7:"with-guide", 8:"with-women", 9:"omiai-guide",
 10:"tapple-vs-pairs", 11:"tapple-guide", 12:"with-vs-pairs",
 13:"omiai-vs-pairs", 14:"free-vs-paid", 15:"fraud-statistics",
 16:"20s-guide", 17:"student-guide", 18:"30s-konkatsu",
 19:"late-20s-strategy", 20:"35s-strategy", 21:"40s-guide",
 22:"40s-men", 23:"women-strategy", 24:"konkatsu-roadmap",
 25:"message-strategy", 26:"profile-photo", 27:"profile-text",
 28:"first-date-spot", 29:"success-stories", 30:"tokyo-guide",
 31:"agency-vs-app", 32:"photo-tips", 33:"time-management",
 34:"fraud-detection", 35:"first-date-guide", 36:"line-exchange",
 37:"anti-fraud", 38:"privacy-protection", 39:"success-rate-data",
 40:"age-data", 41:"members-data", 42:"compare-popular",
 43:"compare-20s", 44:"compare-konkatsu", 45:"compare-price",
 46:"faq-troubleshooting", 47:"renkatsu-vs-konkatsu", 48:"app-plus-agency",
}

def src_files():
    out={}
    for p in SRC.glob("[0-4][0-9]_*.md"):
        n=int(p.name[:2])
        if 1<=n<=48: out[n]=p
    return dict(sorted(out.items()))

FILES = src_files()
FNAME2SLUG = {FILES[n].name: SLUGS[n] for n in FILES}

def esc(s): return html.escape(s, quote=True)

def inline(t):
    """インライン記法（リンク・強調・コード）をHTMLへ。"""
    t = esc(t)
    # 画像はブロックで処理済みのため、ここはリンクのみ
    def link(m):
        text, href = m.group(1), m.group(2)
        href = href.strip()
        # 内部mdリンク -> スラッグURL
        base = href.split('/')[-1]
        if base in FNAME2SLUG:
            href = f"/articles/{FNAME2SLUG[base]}/"
        return f'<a href="{href}">{text}</a>'
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t

def md_to_html(md, faq_acc):
    """対象mdサブセットをHTMLへ変換。FAQはfaq_accに(question,answer)蓄積。"""
    lines = md.split('\n')
    out=[]; i=0; n=len(lines)
    cur_q=None; cur_a=[]
    def flush_faq():
        nonlocal cur_q,cur_a
        if cur_q is not None:
            faq_acc.append((cur_q, ' '.join(cur_a).strip()))
            cur_q=None; cur_a=[]
    in_faq=False
    while i<n:
        ln=lines[i]
        # 水平線
        if re.match(r'^\s*---\s*$', ln):
            i+=1; continue
        # HTMLコメント（<!-- ... -->）は出力しない
        if re.match(r'^\s*<!--', ln):
            while i<n and '-->' not in lines[i]:
                i+=1
            i+=1; continue
        # md内に生の <script>（JSON-LD等）が埋め込まれている場合:
        # そのまま出すとエスケープされて本文に露出するため、FAQPageならfaq_accへ回収し、他は破棄
        if re.match(r'^\s*<script', ln, re.I):
            buf=[ln]
            while i<n and '</script>' not in lines[i].lower():
                i+=1
                if i<n: buf.append(lines[i])
            i+=1
            raw='\n'.join(buf)
            mjson=re.search(r'>\s*(\{.*\})\s*</script>', raw, re.S|re.I)
            if mjson:
                try:
                    data=json.loads(mjson.group(1))
                    if isinstance(data,dict) and data.get('@type')=='FAQPage':
                        for it in data.get('mainEntity',[]):
                            q=(it.get('name') or '').strip()
                            a=((it.get('acceptedAnswer') or {}).get('text') or '').strip()
                            if q and a and q not in [x[0] for x in faq_acc]:
                                faq_acc.append((q,a))
                except Exception:
                    pass
            continue
        # 画像（単独行）
        mimg=re.match(r'^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$', ln)
        if mimg:
            alt,src=esc(mimg.group(1)), mimg.group(2).strip()
            base=src.split('/')[-1]
            out.append(f'<img src="/images/{base}" alt="{alt}" loading="lazy" class="art-img">')
            i+=1; continue
        # 見出し
        mh=re.match(r'^(#{1,4})\s+(.+?)\s*#*$', ln)
        if mh:
            lvl=len(mh.group(1)); txt=mh.group(2).strip()
            # FAQ判定
            if lvl==2:
                flush_faq()
                in_faq = ('よくある質問' in txt or 'FAQ' in txt)
            if in_faq and lvl==3 and re.match(r'^Q\d*[\.\．]?', txt):
                flush_faq()
                cur_q=re.sub(r'^Q\d*[\.\．]?\s*','',txt)
                i+=1; continue
            # H1はテンプレ側のタイトルのみ。本文のレベル1見出しはh2へ降格（H1重複回避）
            tag = 'h2' if lvl==1 else f'h{min(lvl,4)}'
            out.append(f'<{tag}>{inline(txt)}</{tag}>')
            i+=1; continue
        # テーブル
        if '|' in ln and i+1<n and re.match(r'^\s*\|?[\s:|-]+\|[\s:|-]*$', lines[i+1]):
            header=[c.strip() for c in ln.strip().strip('|').split('|')]
            i+=2; rows=[]
            while i<n and '|' in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i+=1
            th=''.join(f'<th>{inline(h)}</th>' for h in header)
            trs=''
            for r in rows:
                tds=''.join(f'<td>{inline(c)}</td>' for c in r)
                trs+=f'<tr>{tds}</tr>'
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
            continue
        # 引用
        if re.match(r'^\s*>\s?', ln):
            buf=[]
            while i<n and re.match(r'^\s*>\s?', lines[i]):
                buf.append(re.sub(r'^\s*>\s?','',lines[i])); i+=1
            inner='<br>'.join(inline(b) for b in buf if b.strip())
            out.append(f'<blockquote>{inner}</blockquote>')
            continue
        # リスト
        if re.match(r'^\s*[-*]\s+', ln):
            items=[]
            while i<n and re.match(r'^\s*[-*]\s+', lines[i]):
                items.append(inline(re.sub(r'^\s*[-*]\s+','',lines[i]))); i+=1
            out.append('<ul>'+''.join(f'<li>{it}</li>' for it in items)+'</ul>')
            continue
        # 番号リスト
        if re.match(r'^\s*\d+\.\s+', ln):
            items=[]
            while i<n and re.match(r'^\s*\d+\.\s+', lines[i]):
                items.append(inline(re.sub(r'^\s*\d+\.\s+','',lines[i]))); i+=1
            out.append('<ol>'+''.join(f'<li>{it}</li>' for it in items)+'</ol>')
            continue
        # 空行
        if not ln.strip():
            i+=1; continue
        # 段落（連続行をまとめる）
        buf=[ln]; i+=1
        while i<n and lines[i].strip() and not re.match(r'^(#{1,4}\s|\s*[-*]\s|\s*\d+\.\s|\s*>|\s*!\[|\s*---\s*$)', lines[i]) and '|' not in lines[i]:
            buf.append(lines[i]); i+=1
        para=' '.join(buf)
        if in_faq and cur_q is not None:
            cur_a.append(re.sub(r'<[^>]+>','',inline(para)))
        out.append(f'<p>{inline(para)}</p>')
    flush_faq()
    return '\n'.join(out)

def parse(md):
    """frontmatter(title,author,date) と本文・バイラインを抽出。"""
    meta={}
    m=re.match(r'^---\n(.*?)\n---\n', md, re.S)
    body=md
    if m:
        for line in m.group(1).split('\n'):
            if ':' in line:
                k,v=line.split(':',1); meta[k.strip()]=v.strip()
        body=md[m.end():]
    # バイライン抽出（**著者:** ...）
    author=meta.get('author','Noe編集部')
    mby=re.search(r'\*\*著者[:：]\*\*\s*(.+)', body)
    byline=mby.group(1).strip() if mby else ''
    updated=meta.get('last_updated','2026年5月')
    mup=re.search(r'\*\*最終更新[:：]\*\*\s*(.+)', body)
    if mup: updated=mup.group(1).strip()
    # 先頭のメタ行（最終更新/著者）を本文から除去
    body=re.sub(r'\*\*最終更新[:：]\*\*.*?\n','',body)
    body=re.sub(r'\*\*著者[:：]\*\*.*?\n','',body)
    return meta, author, byline, updated, body

CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--pink:#ff4d7e;--pink-dark:#d63660;--pink-deep:#b02a4e;--pink-light:#fff0f4;--purple:#7c5cbf;--navy:#1c2b33;--text:#2c3e50;--ink-soft:#3d454d;--sub:#607d8b;--bg:#faf8f9;--white:#fff;--border:#efe8ea;--line-strong:#e0d5d9;--shadow:0 1px 3px rgba(30,35,40,.06),0 4px 14px rgba(30,35,40,.06);--shadow-hover:0 4px 10px rgba(214,54,96,.10),0 8px 24px rgba(30,35,40,.08);--radius:12px}
html{scroll-behavior:smooth}
body{font-family:'Noto Sans JP',-apple-system,"Hiragino Kaku Gothic ProN",sans-serif;color:var(--text);background:var(--bg);line-height:1.9;font-size:15.5px;-webkit-font-smoothing:antialiased;font-feature-settings:"palt";letter-spacing:.01em}
header{background:rgba(255,255,255,.94);backdrop-filter:blur(8px);border-bottom:3px solid var(--pink);position:sticky;top:0;z-index:100;box-shadow:0 2px 12px rgba(0,0,0,.05)}
.header-inner{max-width:860px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.logo{font-size:1.1rem;font-weight:900;color:var(--pink-dark);text-decoration:none;letter-spacing:.01em}
.logo-badge{background:var(--pink);color:#fff;font-size:.62rem;padding:2px 8px;border-radius:20px;margin-left:6px}
nav a{color:var(--sub);text-decoration:none;font-size:.8rem;padding:6px 9px;border-radius:6px;font-weight:500;transition:background .15s,color .15s}
nav a:hover{background:var(--pink-light);color:var(--pink-dark)}
@media(max-width:680px){nav{display:none}}
.wrap{max-width:860px;margin:0 auto;padding:0 20px}
.breadcrumb{font-size:.76rem;color:var(--sub);padding:14px 0}
.breadcrumb a{color:var(--sub);text-decoration:none}
.breadcrumb a:hover{color:var(--pink-dark)}
article{background:#fff;border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow);padding:38px 34px;margin-bottom:30px}
@media(max-width:600px){article{padding:26px 18px}}
article h1{font-size:clamp(1.5rem,4.5vw,2rem);font-weight:900;line-height:1.45;letter-spacing:.01em;margin-bottom:16px;color:var(--navy)}
.byline{display:flex;gap:12px;align-items:flex-start;background:var(--pink-light);border:1px solid #ffdfe8;border-radius:10px;padding:14px 16px;margin-bottom:8px;font-size:.8rem;color:var(--text);line-height:1.7}
.byline .av{font-size:1.6rem;line-height:1}
.byline .up{color:var(--sub);font-size:.72rem;margin-top:3px}
article h2{font-size:clamp(1.2rem,3.4vw,1.45rem);font-weight:900;line-height:1.5;margin:44px 0 16px;padding:.45em 0 .45em 14px;border-left:5px solid var(--pink);background:linear-gradient(90deg,var(--pink-light),transparent 70%);border-radius:0 8px 8px 0;color:var(--navy)}
article h3{font-size:1.08rem;font-weight:700;margin:30px 0 10px;color:var(--pink-deep);padding-bottom:4px;border-bottom:2px solid var(--pink-light)}
article h4{font-size:.98rem;font-weight:700;margin:22px 0 8px;color:var(--ink-soft)}
article p{margin:13px 0}
article ul,article ol{margin:13px 0 13px 1.45em}
article li{margin:7px 0}
article a{color:var(--pink-dark);font-weight:500;text-decoration-color:#f2b3c4;text-underline-offset:3px;transition:color .15s}
article a:hover{color:var(--pink)}
.art-img{max-width:100%;height:auto;border-radius:10px;margin:20px 0;display:block;box-shadow:var(--shadow)}
blockquote{background:#fff8e1;border-left:4px solid #f4c542;border-radius:0 10px 10px 0;padding:14px 18px;margin:20px 0;font-size:.93rem;color:var(--ink-soft)}
blockquote strong{color:var(--pink-dark)}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:10px;box-shadow:var(--shadow);margin:20px 0;border:1px solid var(--border)}
table{width:100%;border-collapse:collapse;background:#fff;font-size:.85rem;min-width:520px}
thead th{background:linear-gradient(180deg,#243642,var(--navy));color:#fff;padding:12px 10px;text-align:center;font-weight:700;letter-spacing:.02em;white-space:nowrap}
tbody td{padding:11px 10px;border-bottom:1px solid var(--border);text-align:center}
tbody tr:nth-child(even){background:#fbf7f8}
tbody tr:hover{background:var(--pink-light)}
tbody td:first-child{font-weight:700;color:var(--navy)}
code{background:#f3f0ff;color:#6a1b9a;padding:1px 6px;border-radius:4px;font-size:.86em}
.related{background:#fff;border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow);padding:24px 26px;margin-bottom:30px}
.related h2{font-size:1.05rem;font-weight:900;margin-bottom:14px;color:var(--navy);padding-left:10px;border-left:4px solid var(--pink)}
.related ul{list-style:none;display:grid;gap:10px}
.related a{display:block;background:#fff;border:1px solid var(--border);border-radius:10px;padding:12px 15px;font-size:.83rem;font-weight:500;text-decoration:none;color:var(--text);transition:border-color .15s,box-shadow .15s,transform .12s}
.related a:hover{border-color:var(--pink);box-shadow:var(--shadow-hover);transform:translateY(-1px);color:var(--pink-dark)}
.cta-foot{background:linear-gradient(135deg,var(--pink-deep) 0%,var(--pink-dark) 45%,var(--pink) 100%);color:#fff;text-align:center;border-radius:16px;padding:38px 26px;margin-bottom:30px;box-shadow:0 6px 22px rgba(214,54,96,.28)}
.cta-foot h2{font-size:1.28rem;font-weight:900;margin-bottom:10px;border:none;background:none;padding:0;color:#fff}
.cta-foot p{opacity:.92;font-size:.92rem}
.cta-foot a{display:inline-block;background:linear-gradient(180deg,#fff,#ffeef3);color:var(--pink-deep);font-weight:800;padding:14px 34px;border-radius:32px;text-decoration:none;margin-top:14px;font-size:1.02rem;box-shadow:0 3px 10px rgba(0,0,0,.18);transition:transform .12s,box-shadow .12s}
.cta-foot a:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,.24)}
footer{background:var(--navy);color:#9aa;padding:34px 20px;font-size:.76rem;line-height:1.8}
.footer-inner{max-width:860px;margin:0 auto;text-align:center}
.footer-inner a{color:#b9c2c8;text-decoration:none;margin:0 8px}
.footer-inner a:hover{color:#fff}
.footer-disc{color:#78868f;font-size:.68rem;margin-top:12px;line-height:1.7}
#top{position:fixed;bottom:20px;right:20px;width:44px;height:44px;background:var(--pink);color:#fff;border:none;border-radius:50%;font-size:1.1rem;cursor:pointer;box-shadow:0 4px 14px rgba(255,77,126,.4);opacity:0;transition:.3s}
#top.show{opacity:1}
#top:hover{background:var(--pink-dark)}
@media(max-width:600px){body{font-size:14.5px}article h2{margin:34px 0 12px}.cta-foot a{display:block;padding:14px 18px}}"""

def build(n):
    p=FILES[n]; slug=SLUGS[n]
    meta,author,byline,updated,body=parse(p.read_text(encoding='utf-8'))
    title=meta.get('title') or ''
    # frontmatterのtitleが欠損/プレースホルダなら本文H1を採用
    if (not title) or title.strip().lower() in ('article','記事',f'記事{n}'):
        mh1=re.search(r'^#\s+(.+?)\s*$', body, re.M)
        title=mh1.group(1).strip() if mh1 else f"記事{n}"
    # 本文先頭のタイトルH1を除去（テンプレH1と重複するため）
    body=re.sub(r'^#\s+.+?\s*$', '', body, count=1, flags=re.M)
    faq=[]
    content=md_to_html(body, faq)
    # description: 本文最初の<p>から
    mdesc=re.search(r'<p>(.*?)</p>', content, re.S)
    desc=re.sub(r'<[^>]+>','',mdesc.group(1))[:110] if mdesc else title
    # 更新日をISO8601へ（例: 2026年6月1日 -> 2026-06-01）
    iso=''
    md_=re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', updated)
    if md_: iso=f"{int(md_.group(1)):04d}-{int(md_.group(2)):02d}-{int(md_.group(3)):02d}"
    # 先頭画像（スキーマ用）
    mimg=re.search(r'<img src="(/images/[^"]+)"', content)
    img_url=f"{DOMAIN}{mimg.group(1)}" if mimg else f"{DOMAIN}/images/"
    canon=f"{DOMAIN}/articles/{slug}/"
    # FAQ schema
    schemas=[]
    if faq:
        items=[{"@type":"Question","name":q,
                "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq if a]
        if items:
            schemas.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":items})
    # Article(BlogPosting) schema
    art={"@context":"https://schema.org","@type":"Article","headline":title[:110],
         "description":desc,"image":img_url,"url":canon,
         "mainEntityOfPage":{"@type":"WebPage","@id":canon},
         "inLanguage":"ja",
         "author":{"@type":"Organization","name":author or "NOE結婚設計室 編集部",
                   "url":DOMAIN+"/about.html"},
         "publisher":{"@type":"Organization","name":"NOE結婚設計室",
                      "url":DOMAIN+"/"}}
    if iso: art["datePublished"]=iso; art["dateModified"]=iso
    schemas.append(art)
    # BreadcrumbList schema
    schemas.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"ホーム","item":DOMAIN+"/"},
        {"@type":"ListItem","position":2,"name":"記事一覧","item":DOMAIN+"/#articles"},
        {"@type":"ListItem","position":3,"name":title}]})
    faq_ld='\n'.join('<script type="application/ld+json">'+json.dumps(s,ensure_ascii=False)+'</script>' for s in schemas)
    # 著者名（バイラインがあれば著者の肩書/実績、無ければ編集部）
    aname=esc(author or "Noe編集部")
    bdesc=esc(byline) if (byline and byline.strip()!=author.strip()) else "マッチングアプリを実際に使用した経験を持つ編集部。Pairs・with・Omiai・Tapple・ユーブライドを検証。"
    byline_html=f'''<div class="byline"><div class="av">✍️</div><div><strong><a href="/about.html" style="color:inherit;text-decoration:none">{aname}</a></strong><br>{bdesc}<div class="up">最終更新：{esc(updated)}</div></div></div>'''
    page=f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{DOMAIN}/articles/{slug}/">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{DOMAIN}/articles/{slug}/">
<meta property="og:image" content="{esc(img_url)}">
<meta property="og:site_name" content="NOE結婚設計室">
<meta property="og:locale" content="ja_JP">
{f'<meta property="article:published_time" content="{iso}">' if iso else ''}
{f'<meta property="article:modified_time" content="{iso}">' if iso else ''}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(img_url)}">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>{CSS}</style>
{faq_ld}
</head>
<body>
<header><div class="header-inner">
<a href="/" class="logo">💑 マッチングアプリガイド<span class="logo-badge">2026</span></a>
<nav><a href="/#ranking">ランキング</a><a href="/#articles">記事一覧</a><a href="/#faq">FAQ</a><a href="/#about">運営者</a></nav>
</div></header>
<div class="wrap">
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/#articles">記事一覧</a> ＞ {esc(title)}</div>
<article>
<h1>{esc(title)}</h1>
{byline_html}
{content}
</article>
{{related}}
<div class="cta-foot">
<h2>あなたに合うアプリを見つけよう</h2>
<p>編集部が実際に使って検証した2026年版ランキングはこちら。</p>
<a href="/#ranking">🏆 おすすめランキングを見る</a>
</div>
</div>
<footer><div class="footer-inner">
<div><a href="/">ホーム</a><a href="/#articles">記事一覧</a><a href="/about.html">運営者情報</a><a href="/privacy-policy.html">プライバシー</a><a href="/disclaimer.html">免責事項</a></div>
<p class="footer-disc">※本記事の情報は{esc(updated)}時点のものです。料金・サービス内容は変更される場合があります。<strong style="color:#cda">【PR】</strong>本サイトはアフィリエイト広告を含みます。<br>&copy; 2026 NOE結婚設計室</p>
</div></footer>
<button id="top" onclick="scrollTo({{top:0,behavior:'smooth'}})">↑</button>
<script>onscroll=()=>top.classList.toggle('show',scrollY>300)</script>
</body>
</html>'''
    return slug, title, desc, page, content

# --- 関連記事ブロックを本文内リンクから生成（なければ前後の記事）---
def related_block(content, n):
    links=re.findall(r'<a href="(/articles/[^"/]+/)">([^<]+)</a>', content)
    seen=[]; uniq=[]
    for href,txt in links:
        if href not in seen and f"/articles/{SLUGS[n]}/"!=href:
            seen.append(href); uniq.append((href,txt))
    if len(uniq)<3:
        for m in [n-1,n+1,1,2,3]:
            if m in SLUGS and m!=n:
                h=f"/articles/{SLUGS[m]}/"
                if h not in seen: seen.append(h); uniq.append((h,SLUGS[m]))
            if len(uniq)>=4: break
    uniq=uniq[:6]
    lis=''.join(f'<li><a href="{h}">{esc(t)}</a></li>' for h,t in uniq)
    return f'<div class="related"><h2>📚 関連記事</h2><ul>{lis}</ul></div>'

def write_sitemap(lastmod):
    """トップ＋48記事＋法的ページを含む sitemap.xml を生成。"""
    entries=[(f"{DOMAIN}/","weekly","1.0")]
    for n in sorted(SLUGS):
        entries.append((f"{DOMAIN}/articles/{SLUGS[n]}/","monthly","0.8"))
    for pg in ("about.html","privacy-policy.html","disclaimer.html"):
        entries.append((f"{DOMAIN}/{pg}","yearly","0.3"))
    parts=['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc,freq,pri in entries:
        parts.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>")
    parts.append('</urlset>\n')
    (DEPLOY/"sitemap.xml").write_text('\n'.join(parts),encoding='utf-8')
    return len(entries)

if __name__=='__main__':
    targets=[int(x) for x in sys.argv[1:]] if len(sys.argv)>1 else list(SLUGS)
    IMG_OUT.mkdir(exist_ok=True)
    # 画像コピー
    copied=0
    for img in SRC.glob('images/*'):
        dst=IMG_OUT/img.name
        if not dst.exists():
            shutil.copy2(img,dst); copied+=1
    meta_out=[]
    for n in targets:
        slug,title,desc,page,content=build(n)
        page=page.replace('{related}', related_block(content,n))
        # GitHub Pages 静的対応: articles/{slug}/index.html
        d=ART_OUT/slug; d.mkdir(parents=True, exist_ok=True)
        (d/"index.html").write_text(page,encoding='utf-8')
        meta_out.append((n,slug,title))
        print(f"  [{n:>2}] {slug:<22} {title[:42]}")
    from datetime import date
    n_urls=write_sitemap(date.today().isoformat())
    print(f"\n生成 {len(targets)}記事 / 画像コピー {copied}枚 / sitemap {n_urls} URL")
