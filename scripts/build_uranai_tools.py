# -*- coding: utf-8 -*-
"""C-003 占い診断3本を生成する（mon-uranai-shindan・2026-10-26）

  python scripts/build_uranai_tools.py

- tools/seiza-renai-uranai/ / tools/suhi-kekkon-uranai/ / tools/aisho-uranai/ の index.html
- images/<slug>-og.png（1200x630）
見た目は tools/konkatsu-type-shindan/ の CSS をそのまま流用する。
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from uranai_content import SIGNS, ELEM_DESC, NUMBERS, COMPAT  # noqa: E402

SITE = 'https://www.noe-match.com'
COCONALA = 'https://px.a8.net/svt/ejp?a8mat=4B8BWW+FJNJQI+2PEO+C28PU'
UPDATED = '2026-10-26'

NOTE_C = [
    'この診断は娯楽のための占いです。入力された生年月日をもとに、あらかじめ用意した文章をプログラムが自動で選んで表示しています。占い師や霊能者が鑑定したものではなく、AI による自動生成の文章を含みます。結果は将来を予言・保証するものではありません。恋愛・結婚・お金・健康などの大切な判断は、結果だけで決めないでください。',
    '入力した内容はお使いのブラウザの中だけで計算し、当サイトのサーバーや第三者には送りません（保存もしません）。',
    '下に紹介する電話占いは有料のサービス（1分ごとに料金がかかります）です。18歳未満の方がココナラを利用するには、保護者（法定代理人）の同意が必要です（ココナラの利用規約による）。',
]
NOTE_U18 = '電話占いは有料のサービス（1分ごとに料金がかかります）です。18歳未満の方がココナラを利用するには、保護者（法定代理人）の同意が必要です（ココナラの利用規約による）。'
PR_HEAD = '【PR】相談サービスの紹介（広告）'
PR_LEAD = '【PR】以下は電話占いサービスの広告です。'

TOOLS = {
    'seiza-renai-uranai': {'short': '星座でみる恋愛傾向占い', 'desc': '生年月日から12星座を出し、恋愛の傾向と婚活で生かせるヒントを読む'},
    'suhi-kekkon-uranai': {'short': '数秘術でみる結婚観占い', 'desc': '生年月日からライフパスナンバーを出し、結婚観と話し合うと良いことを読む'},
    'aisho-uranai': {'short': '生年月日でみる二人の相性占い', 'desc': '二人の生年月日から、関係の傾向とすれ違いやすい点、話し方のヒントを読む'},
}
ARTICLE_URL = '/articles/denwa-uranai-konkatsu/'
ARTICLE_TITLE = '婚活・恋愛の迷いを電話占いで話す前に'


def esc(s):
    return html.escape(s, quote=True)


def base_css():
    with open(os.path.join(ROOT, 'tools', 'konkatsu-type-shindan', 'index.html'), encoding='utf-8') as f:
        src = f.read()
    m = re.search(r'<style>(.*?)</style>', src, re.S)
    return m.group(1)


EXTRA_CSS = """
.pr-top{font-size:.78rem;color:var(--sub);margin:0 0 14px}
.calc select{width:100%;padding:11px 8px;font-size:16px;border:1px solid var(--line-strong);border-radius:4px;background:#fff;color:var(--text);font-family:inherit}
.date-row{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:8px}
.person-ttl{font-weight:700;font-size:.92rem;color:var(--ink);margin:4px 0 8px}
.err{color:#a24e2a;font-size:.85rem;font-weight:700;margin-top:10px;display:none}
.note-c p{margin:0 0 8px}
.note-c p:last-child{margin:0}
.result{padding:0;overflow:hidden}
.result-head{background:linear-gradient(rgba(250,249,247,.9),rgba(250,249,247,.86)),url('../../images/lp/__BG__') center/cover;padding:28px 20px 20px;text-align:center;border-bottom:1px solid var(--hair)}
.result-head .lbl{font-size:.8rem;color:var(--sub);font-weight:700;letter-spacing:.06em}
.result-head .num{font-family:var(--serif);font-size:clamp(1.6rem,6vw,2.2rem);font-weight:700;color:var(--acc);line-height:1.4;margin:4px 0}
.result-head .sub{font-size:.86rem;color:var(--ink-soft)}
.result-head .type{font-weight:700;color:var(--ink);margin-top:8px;font-size:.98rem}
.result-head .wm{font-size:.66rem;color:var(--gray);margin-top:10px;letter-spacing:.04em}
.result-body{padding:6px 20px 22px}
.r-block{margin:20px 0 0}
.r-block h3{font-size:.98rem;margin:0 0 6px;font-weight:700;color:var(--ink);border:none;padding:0}
.r-block p{margin:0;font-size:.93rem}
.edge-note{background:var(--alt);border:1px dashed var(--line-strong);border-radius:6px;padding:12px 14px;font-size:.85rem;margin:16px 0 0}
.edge-note button{background:none;border:none;color:var(--acc);font-weight:700;cursor:pointer;text-decoration:underline;font-family:inherit;font-size:.85rem;padding:0}
.r-disclaimer{font-size:.76rem;color:var(--sub);margin-top:18px}
.share-block{text-align:center;margin-top:22px;padding-top:18px;border-top:1px solid var(--hair)}
.share-title{font-size:.82rem;font-weight:700;color:var(--sub);margin-bottom:12px}
.share-btns{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}
.share-btn{display:inline-flex;align-items:center;gap:7px;border-radius:4px;padding:10px 22px;font-size:.86rem;font-weight:700;text-decoration:none;cursor:pointer;border:none;font-family:inherit}
.share-btn.x{background:#0f1419;color:#fff}
.share-btn.copy{background:#fff;color:var(--text);border:1px solid var(--line-strong)}
.prbox{background:var(--alt);border:1px solid var(--hair);padding:20px 20px;margin:24px 0 0;text-align:center}
.prbox .pr-h{font-weight:700;margin:0 0 8px;text-align:left;font-size:.95rem;color:var(--ink)}
.prbox .pr-p{font-size:.86rem;color:var(--ink-soft);margin:0 0 10px;text-align:left}
.prbox .pr-u18{font-size:.8rem;color:var(--ink-soft);margin:0 0 12px;text-align:left;background:#fff;border-left:3px solid var(--line-strong);padding:8px 12px}
.prbox .pr-lead{font-size:.8rem;color:var(--sub);margin:0 0 8px;text-align:left}
.prbox a.pr-btn{display:inline-block;background:#7c2e42;color:#fff;font-weight:700;padding:13px 30px;text-decoration:none;max-width:100%}
.prbox a.pr-btn:hover{background:#5c2131}
.prbox .pr-n{font-size:.74rem;color:#888;margin:10px 0 0}
.next-links{margin:22px 0 0}
.next-links h3{font-size:.95rem;margin:0 0 8px;border:none;padding:0}
.next-links ul{margin:0 0 0 1.2em}
.next-links li{font-size:.9rem;margin:5px 0}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0 0}
.pair .cell{background:var(--alt);border-radius:4px;padding:10px;text-align:center;font-size:.86rem}
.pair .cell b{display:block;color:var(--ink);font-size:.98rem}
@media(max-width:420px){.pair{grid-template-columns:1fr}}
"""

HEADER = """<header><div class="header-inner">
<a href="/" class="logo">Noe結婚設計室<span class="logo-badge">2026</span></a>
<nav><a href="/#tools">ツール</a><a href="/articles/">記事一覧</a><a href="/#faq">FAQ</a><a href="/#about">運営者</a></nav>
</div></header>"""

FOOTER = """<footer><div class="footer-inner">
<div><a href="/">ホーム</a><a href="/articles/">記事一覧</a><a href="/about.html">運営者情報</a><a href="/privacy-policy.html">プライバシー</a><a href="/disclaimer.html">免責事項</a></div>
<p class="footer-disc">※このページの占いは娯楽を目的としたもので、結果は傾向とヒントです。<strong style="color:#cda">【PR】</strong>本サイトはアフィリエイト広告を含みます。<br>&copy; 2026 Noe結婚設計室</p>
</div></footer>
<button id="top" onclick="scrollTo({top:0,behavior:'smooth'})">↑</button>"""


def year_opts():
    out = ['<option value="">年</option>']
    for y in range(2008, 1939, -1):
        out.append(f'<option value="{y}">{y}年</option>')
    return ''.join(out)


def month_opts():
    return '<option value="">月</option>' + ''.join(f'<option value="{m}">{m}月</option>' for m in range(1, 13))


def day_opts():
    return '<option value="">日</option>' + ''.join(f'<option value="{d}">{d}日</option>' for d in range(1, 32))


def date_fields(prefix, label):
    return f"""<div class="fld"><span class="person-ttl">{label}</span>
    <div class="date-row">
      <select id="{prefix}y" aria-label="{label}（年）">{year_opts()}</select>
      <select id="{prefix}m" aria-label="{label}（月）">{month_opts()}</select>
      <select id="{prefix}d" aria-label="{label}（日）">{day_opts()}</select>
    </div></div>"""


def note_c_html():
    return '<div class="note-src note-c">' + ''.join(f'<p>{esc(p)}</p>' for p in NOTE_C) + '</div>'


def prbox_html(slug, lead):
    return f"""<div class="prbox">
<p class="pr-h">{PR_HEAD}</p>
<p class="pr-p">{esc(lead)}</p>
<p class="pr-u18">{NOTE_U18}</p>
<p class="pr-lead">{PR_LEAD}</p>
<a class="pr-btn" id="prLink" href="{COCONALA}" rel="nofollow sponsored noopener" target="_blank">ココナラ電話占いを見る</a>
<p class="pr-n">1分ごとに料金がかかります。料金と特典の条件は公式サイトで確認してください。</p>
</div>"""


def other_links(slug):
    items = []
    for s, t in TOOLS.items():
        if s != slug:
            items.append(f'<li><a href="/tools/{s}/">{t["short"]}</a></li>')
    items.append(f'<li><a href="/tools/konkatsu-type-shindan/">婚活タイプ診断（自分に合う婚活の進め方を選ぶ）</a></li>')
    items.append(f'<li><a href="{ARTICLE_URL}">{ARTICLE_TITLE}</a></li>')
    return '<div class="next-links"><h3>あわせて読む・試す</h3><ul>' + ''.join(items) + '</ul></div>'


def related_html(slug):
    items = []
    for s, t in TOOLS.items():
        if s != slug:
            items.append(f'<li><a href="/tools/{s}/">{t["short"]}｜{t["desc"]}</a></li>')
    items.append('<li><a href="/tools/konkatsu-type-shindan/">婚活タイプ診断｜アプリ・相談所・パーティーのどれが自分の生活に合うか</a></li>')
    items.append(f'<li><a href="{ARTICLE_URL}">{ARTICLE_TITLE}</a></li>')
    items.append('<li><a href="/articles/konkatsu-soudan-saki/">婚活の相談は誰にすればよいか</a></li>')
    return '<div class="related"><h2>関連する占い・診断・記事</h2><ul>' + ''.join(items) + '</ul></div>'


def share_html():
    return """<div class="share-block">
<div class="share-title">結果をシェアする</div>
<div class="share-btns">
<a class="share-btn x" id="shareX" href="#" target="_blank" rel="noopener">X でポスト</a>
<button class="share-btn copy" id="shareCopy" type="button">リンクをコピー</button>
</div></div>"""


def faq_html(faqs):
    out = ['<article><h2>よくある質問</h2>']
    for i, (q, a) in enumerate(faqs, 1):
        out.append(f'<h3>Q{i}. {esc(q)}</h3><p>{esc(a)}</p>')
    out.append('</article>')
    return '\n'.join(out)


def jsonld(slug, name, desc, faqs):
    url = f'{SITE}/tools/{slug}/'
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    app = {"@context": "https://schema.org", "@type": "WebApplication", "name": name, "url": url,
           "applicationCategory": "LifestyleApplication", "operatingSystem": "All", "inLanguage": "ja",
           "description": desc, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
           "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": SITE + "/"}}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": SITE + "/#tools"},
        {"@type": "ListItem", "position": 3, "name": name}]}
    return '\n'.join('<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + '</script>'
                     for o in (faq, app, bc))


COMMON_JS = r"""
function track(n,p){try{if(typeof gtag==='function')gtag('event',n,p);}catch(e){}}
function $(id){return document.getElementById(id);}
// 年の選択肢の上限は「ページを開いた年 − 18」（JSで動的に作る。JSなしでは静的な選択肢のまま）
(function(){var max=new Date().getFullYear()-18;['ay','by'].forEach(function(id){var s=$(id);if(!s)return;var h='<option value="">年</option>';for(var y=max;y>=1940;y--)h+='<option value="'+y+'">'+y+'年</option>';s.innerHTML=h;});})();
function readDate(p){
  var y=+$(p+'y').value,m=+$(p+'m').value,d=+$(p+'d').value;
  if(!y||!m||!d)return null;
  var t=new Date(y,m-1,d);
  if(t.getFullYear()!==y||t.getMonth()!==m-1||t.getDate()!==d)return null;
  return {y:y,m:m,d:d};
}
// 星座の区切り（一般的な日付）。[月,開始日,SIGNSの番号]
var CUTS=[[1,20,10],[2,19,11],[3,21,0],[4,20,1],[5,21,2],[6,22,3],[7,23,4],[8,23,5],[9,23,6],[10,24,7],[11,23,8],[12,22,9]];
function signOf(m,d){
  var s=9;
  for(var i=0;i<CUTS.length;i++){if(m>CUTS[i][0]||(m===CUTS[i][0]&&d>=CUTS[i][1]))s=CUTS[i][2];}
  return s;
}
// 境目の前後1日なら、となりの星座の番号を返す（それ以外は -1）
function edgeOf(m,d){
  for(var i=0;i<CUTS.length;i++){
    if(m===CUTS[i][0]&&d===CUTS[i][1])return CUTS[(i+11)%12][2];
    if(m===CUTS[i][0]&&d===CUTS[i][1]-1)return CUTS[i][2];
  }
  return -1;
}
function lifePath(dt){
  var s=String(dt.y)+String(dt.m)+String(dt.d),n=0;
  for(var i=0;i<s.length;i++)n+=+s.charAt(i);
  while(n>9&&n!==11&&n!==22&&n!==33){var t=0;String(n).split('').forEach(function(c){t+=+c;});n=t;}
  return n;
}
var started=false;
[].forEach.call(document.querySelectorAll('.calc select'),function(el){
  el.addEventListener('change',function(){if(!started){started=true;track('uranai_start',{tool:SLUG});}});
});
var lastResult='';
function setShare(name){
  lastResult=name;
  var text=TITLE+'の結果は「'+name+'」でした｜Noe結婚設計室（無料・娯楽）';
  $('shareX').href='https://x.com/intent/post?text='+encodeURIComponent(text)+'&url='+encodeURIComponent(PAGE_URL);
}
$('shareX').addEventListener('click',function(){track('uranai_share',{tool:SLUG,result:lastResult});});
$('shareCopy').addEventListener('click',function(){
  var b=$('shareCopy');
  try{navigator.clipboard.writeText(PAGE_URL).then(function(){b.textContent='コピーしました';setTimeout(function(){b.textContent='リンクをコピー';},1800);});}catch(e){}
  track('uranai_share',{tool:SLUG,result:lastResult});
});
$('prLink').addEventListener('click',function(){track('uranai_pr_click',{tool:SLUG,result:lastResult});});
// 年齢はこのブラウザ内で計算するだけ（送信・保存・GA4・URLに載せない）。18歳未満なら送客枠（広告）を出さない
function isMinor(dt){
  var n=new Date(),age=n.getFullYear()-dt.y;
  if(n.getMonth()+1<dt.m||(n.getMonth()+1===dt.m&&n.getDate()<dt.d))age--;
  return age<18;
}
function showRes(dt,dt2){var box=document.querySelector('.prbox');if(box){var mn=(!!dt&&isMinor(dt))||(!!dt2&&isMinor(dt2));box.hidden=mn;box.style.display=mn?'none':'';}
  $('err').style.display='none';$('res').classList.add('show');$('res').scrollIntoView({behavior:'smooth',block:'start'});}
function showErr(){$('err').style.display='block';}
onscroll=function(){$('top').classList.toggle('show',scrollY>300);};
"""


def page(slug, *, title, desc, og_title, og_desc, h1, hero_p, hero_img, emblem, bg, lead_html,
         form_html, result_html, body_sections, faqs, data_js, run_js, name):
    css = base_css() + EXTRA_CSS.replace('__BG__', bg)
    url = f'{SITE}/tools/{slug}/'
    og_img = f'{SITE}/images/{slug}-og.png'
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VLQBH0S1SL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-VLQBH0S1SL');</script>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(og_desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(og_title)}">
<meta name="twitter:description" content="{esc(og_desc)}">
<meta name="twitter:image" content="{og_img}">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@500;600;700;900&display=swap" rel="stylesheet">
<style>{css}</style>
{jsonld(slug, name, desc, faqs)}
</head>
<body>
{HEADER}
<div class="breadcrumb"><div class="wrap"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ {esc(name)}</div></div>
<main class="wrap">
<div class="tool-hero" style="background-image:url('../../images/lp/{hero_img}')"><div class="tool-hero-inner">
<svg class="hero-mark" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><circle cx="32" cy="32" r="31" fill="#f7f5f2"/><image href="../../images/emblems/{emblem}" x="9" y="9" width="46" height="46"/></svg>
<h1>{esc(h1)}</h1>
<p>{esc(hero_p)}</p>
</div></div>

<article>
<p class="pr-top">【PR】このページには広告（アフィリエイトリンク）が含まれます。</p>
{lead_html}
<div class="calc">
{form_html}
  <button class="calc-btn" id="run" type="button">結果を見る</button>
  <p class="err" id="err">生年月日を正しく選んでください（存在しない日付は選べません）。</p>
</div>
{note_c_html()}

{result_html}

{body_sections}
</article>

{faq_html(faqs)}

{related_html(slug)}
</main>
{FOOTER}
<script>
(function(){{
"use strict";
var SLUG='{slug}';
var TITLE='{TOOLS[slug]["short"]}';
var PAGE_URL='{url}';
{data_js}
{COMMON_JS}
{run_js}
}})();
</script>
</body>
</html>
"""


def result_shell(slug, head_inner, body_inner, pr_lead):
    return f"""<div class="result" id="res" aria-live="polite">
<div class="result-head">
{head_inner}
<div class="wm">noe-match.com/tools/{slug}/</div>
</div>
<div class="result-body">
{body_inner}
<p class="r-disclaimer">※娯楽のための占いです。結果は生年月日から決まった文章を選んで表示した「傾向」と「ヒント」で、将来を予言・保証するものではありません。</p>
{share_html()}
{prbox_html(slug, pr_lead)}
{other_links(slug)}
</div>
</div>"""


# ---------------------------------------------------------------- 星座
def build_seiza():
    slug = 'seiza-renai-uranai'
    name = '星座でみる恋愛傾向占い（無料・娯楽）'
    title = '星座でみる恋愛傾向占い（無料）｜12星座の恋愛傾向と婚活のヒント'
    desc = '生年月日を選ぶと12星座を出し、恋愛の傾向・相性のよい関わり方・婚活で生かせるヒントを表示する無料の娯楽占いです。入力はブラウザの中だけで計算し、送信・保存しません。'
    rows = ''.join(
        f'<tr><td>{s["name"]}</td><td>{s["start"][0]}月{s["start"][1]}日〜{s["end"][0]}月{s["end"][1]}日</td><td>{s["elem"]}</td></tr>'
        for s in SIGNS)
    body = f"""<h2>12星座と誕生日の区切り</h2>
<p>この占いでは、生まれた日に太陽がどの星座の位置にあったか（いわゆる「太陽星座」）で星座を決めています。区切りの日付は、雑誌などで広く使われている一般的なものです。</p>
<div class="table-wrap"><table>
<thead><tr><th>星座</th><th>誕生日</th><th>エレメント</th></tr></thead>
<tbody>{rows}</tbody>
</table></div>
<p class="hint">※太陽が次の星座へ移る日は、生まれた年により1日ほど前後します。境目の前後に生まれた方には、となりの星座の結果も読めるようにしてあります。</p>

<h2>エレメント（火・地・風・水）とは</h2>
<p>西洋占星術では、12星座を4つのエレメントに分けて考えます。同じエレメントの星座どうしは、感じ方や大切にするものが似ているとされます。</p>
<ul>
<li><strong>火</strong>（牡羊座・獅子座・射手座）——{ELEM_DESC["火"]}</li>
<li><strong>地</strong>（牡牛座・乙女座・山羊座）——{ELEM_DESC["地"]}</li>
<li><strong>風</strong>（双子座・天秤座・水瓶座）——{ELEM_DESC["風"]}</li>
<li><strong>水</strong>（蟹座・蠍座・魚座）——{ELEM_DESC["水"]}</li>
</ul>

<h2>結果の読み方</h2>
<p>結果は「恋愛の傾向」「相性のよい関わり方」「婚活で生かせるヒント」の3つに分けてあります。どれも、そういう面が出やすいという<strong>傾向</strong>と、試してみる価値のある<strong>ヒント</strong>です。あてはまらないと感じた部分は読み流してください。</p>
<p>自分の傾向を言葉にしておくと、プロフィールを書くときや、相手に自分のことを伝えるときの材料になります。婚活の手段そのものを選びたい方は、<a href="/tools/konkatsu-type-shindan/">婚活タイプ診断</a>で生活のかたちに合う進め方を比べられます。</p>
"""
    faqs = [
        ('誕生日が星座の境目です。どちらの星座を見ればよいですか？',
         '太陽が星座を移る日は、生まれた年により1日ほど前後します。この占いでは一般的な区切りの日付で判定し、境目の前後1日に生まれた方には、となりの星座の結果も読めるボタンを表示します。両方を読み比べて、しっくりくるほうを参考にしてください。'),
        ('星座で恋愛の相性や結果が決まりますか？',
         '決まりません。この占いは娯楽を目的としたもので、星座ごとに用意した文章を表示しています。恋愛や結婚の進み方は、二人の話し合いや行動によって変わります。結果は自分を振り返るきっかけとして使ってください。'),
        ('入力した生年月日はどこかに送られますか？',
         '送られません。星座の計算はお使いのブラウザの中だけで行い、当サイトのサーバーや第三者には送信せず、保存もしません。アクセス解析には、表示した星座の名前だけを個人が分からない形で記録することがあります。'),
        ('生まれた時間や場所は使いますか？',
         '使いません。この占いが扱うのは、生年月日から決まる太陽星座だけです。生まれた時間や場所から出す月星座などの要素は含めていません。'),
        ('結果を婚活にどう生かせばよいですか？',
         '自分の恋愛の傾向を言葉にしておくと、プロフィールの自己紹介や、初対面で自分のことを話すときの材料になります。また「婚活で生かせるヒント」には、デートの進め方や相手の見方について試しやすい工夫をまとめています。手段選びに迷っている方は婚活タイプ診断もあわせてどうぞ。'),
    ]
    lead = '<blockquote>生年月日を選ぶだけで、あなたの星座と、その星座に出やすい<strong>恋愛の傾向</strong>、<strong>相性のよい関わり方</strong>、<strong>婚活で生かせるヒント</strong>を表示します。名前や悩みの入力はありません。</blockquote>'
    form = date_fields('a', 'あなたの生年月日')
    head = """<div class="lbl">あなたの星座</div>
<div class="num" id="rName">—</div>
<div class="sub" id="rSub"></div>
<div class="type" id="rLabel"></div>"""
    bodyr = """<div class="edge-note" id="rEdge" style="display:none"></div>
<div class="r-block"><h3>恋愛の傾向</h3><p id="rLove"></p></div>
<div class="r-block"><h3>相性のよい関わり方</h3><p id="rRelate"></p></div>
<div class="r-block"><h3>婚活で生かせるヒント</h3><p id="rHint"></p></div>
<div class="r-block"><h3>エレメントについて</h3><p id="rElem"></p></div>"""
    pr_lead = '結果を読んで、自分の気持ちを誰かに話して整理したくなったときの選択肢の一つとして、電話で相談できるサービスがあります。利用するかどうかは自由です。'
    data = 'var SIGNS=' + json.dumps([{k: s[k] for k in ('name', 'elem', 'label', 'love', 'relate', 'hint')} | {
        'range': f'{s["start"][0]}月{s["start"][1]}日〜{s["end"][0]}月{s["end"][1]}日'} for s in SIGNS], ensure_ascii=False) + ';\n'
    data += 'var ELEM=' + json.dumps(ELEM_DESC, ensure_ascii=False) + ';'
    run = r"""
function render(i,edge){
  var s=SIGNS[i];
  $('rName').textContent=s.name;
  $('rSub').textContent=s.elem+'のエレメント・'+s.range+'生まれ';
  $('rLabel').textContent=s.label;
  $('rLove').textContent=s.love;
  $('rRelate').textContent=s.relate;
  $('rHint').textContent=s.hint;
  $('rElem').textContent=ELEM[s.elem];
  var box=$('rEdge');
  if(edge>=0){
    box.style.display='block';
    box.textContent='';
    box.appendChild(document.createTextNode('星座の境目に近い誕生日です。星座の切り替わる日は生まれた年により前後します。'));
    var b=document.createElement('button');b.type='button';
    b.textContent='となりの'+SIGNS[edge].name+'の結果も読む';
    b.addEventListener('click',function(){render(edge,i);});
    box.appendChild(document.createTextNode(' '));box.appendChild(b);
  }else{box.style.display='none';}
  setShare(s.name);
}
$('run').addEventListener('click',function(){
  var dt=readDate('a');
  if(!dt){showErr();return;}
  var i=signOf(dt.m,dt.d);
  render(i,edgeOf(dt.m,dt.d));
  showRes(dt);
  track('uranai_complete',{tool:SLUG,result:SIGNS[i].name});
});
"""
    return slug, page(slug, title=title, desc=desc,
                      og_title='星座でみる恋愛傾向占い（無料・娯楽）',
                      og_desc='生年月日から12星座を出し、恋愛の傾向・相性のよい関わり方・婚活で生かせるヒントを表示します。',
                      h1='星座でみる恋愛傾向占い（無料・娯楽）',
                      hero_p='生年月日から12星座を出し、恋愛の傾向と婚活で生かせるヒントを読みます。登録なし・入力は生年月日だけ。',
                      hero_img='room-light.jpg', emblem='sun.png', bg='room-light.jpg',
                      lead_html=lead, form_html=form, result_html=result_shell(slug, head, bodyr, pr_lead),
                      body_sections=body, faqs=faqs, data_js=data, run_js=run, name=name)


# ---------------------------------------------------------------- 数秘
def build_suhi():
    slug = 'suhi-kekkon-uranai'
    name = '数秘術でみる結婚観占い（無料・娯楽）'
    title = '数秘術でみる結婚観占い（無料）｜ライフパスナンバーで読む結婚観'
    desc = '生年月日からライフパスナンバー（1〜9・11・22・33）を出し、結婚観・パートナーシップの傾向・ふたりで話し合うと良いことを表示する無料の娯楽占いです。入力は送信・保存しません。'
    rows = ''.join(f'<tr><td>{n}</td><td>{NUMBERS[n]["label"]}</td></tr>' for n in NUMBERS)
    body = f"""<h2>ライフパスナンバーの出し方</h2>
<p>数秘術では、生年月日の数字をすべて一桁ずつ足し、一桁になるまで足し続けた数を「ライフパスナンバー」と呼びます。途中で11・22・33になった場合は、そこで止めて特別な数として扱います。</p>
<blockquote><strong>例：1992年7月15日生まれ</strong><br>1＋9＋9＋2＋7＋1＋5＝34 → 3＋4＝<strong>7</strong>（ライフパスナンバー7）</blockquote>
<p class="hint">※年・月・日をそれぞれ一桁にしてから足すなど、計算の仕方は流派によって違いがあり、結果が変わることがあります。この占いは、すべての数字を一桁ずつ足す方法で計算しています。</p>

<h2>ナンバーごとの結婚観</h2>
<div class="table-wrap"><table>
<thead><tr><th>ナンバー</th><th>結婚観の傾向</th></tr></thead>
<tbody>{rows}</tbody>
</table></div>

<h2>結果の読み方</h2>
<p>結果は「結婚観」「パートナーシップの傾向」「ふたりで話し合うと良いこと」の3つに分けてあります。どれも、そういう考え方をしやすいという<strong>傾向</strong>で、どのナンバーが結婚に向いている、向いていないということはありません。</p>
<p>いちばん使いやすいのは「話し合うと良いこと」です。相手と結婚観をすり合わせる話題のきっかけとして使ってください。二人の組み合わせを見たい方は<a href="/tools/aisho-uranai/">生年月日でみる二人の相性占い</a>へ、婚活の進め方を選びたい方は<a href="/tools/konkatsu-type-shindan/">婚活タイプ診断</a>へどうぞ。</p>
"""
    faqs = [
        ('ライフパスナンバーとは何ですか？',
         '数秘術で、生年月日の数字をすべて足して一桁にした数のことです。その人の考え方や大切にするものの傾向を表すとされます。この占いでは、その数ごとに結婚観とパートナーシップの傾向を文章にまとめています。'),
        ('11・22・33が出たのはなぜですか？',
         '数字を足していく途中で11・22・33になった場合、数秘術ではそこで止めて特別な数として扱う考え方があります。この占いもその考え方に従い、11・22・33にはそれぞれ専用の文章を用意しています。一桁まで足す流派では、11は2、22は4、33は6になります。'),
        ('計算方法によって結果が変わることはありますか？',
         'あります。年・月・日をそれぞれ一桁にしてから足すなど、流派によって計算の仕方が異なり、ナンバーが変わることがあります。この占いは、生年月日のすべての数字を一桁ずつ足す方法で計算しています。'),
        ('入力した生年月日は保存されますか？',
         '保存されません。計算はお使いのブラウザの中だけで行い、当サイトのサーバーや第三者には送信しません。アクセス解析には、表示したナンバーだけを個人が分からない形で記録することがあります。'),
        ('相手と結婚観が違ったら、うまくいかないのでしょうか？',
         'そうとは限りません。結婚観が違うことは、話し合っておくべき点が見えているということでもあります。結果の「ふたりで話し合うと良いこと」を話題のきっかけにして、お互いの考えを言葉にしてみてください。'),
    ]
    lead = '<blockquote>生年月日を選ぶと、数秘術の<strong>ライフパスナンバー</strong>を計算し、あなたの<strong>結婚観</strong>、<strong>パートナーシップの傾向</strong>、<strong>ふたりで話し合うと良いこと</strong>を表示します。名前や悩みの入力はありません。</blockquote>'
    form = date_fields('a', 'あなたの生年月日')
    head = """<div class="lbl">あなたのライフパスナンバー</div>
<div class="num" id="rName">—</div>
<div class="sub" id="rSub"></div>
<div class="type" id="rLabel"></div>"""
    bodyr = """<div class="r-block"><h3>結婚観</h3><p id="rView"></p></div>
<div class="r-block"><h3>パートナーシップの傾向</h3><p id="rPartner"></p></div>
<div class="r-block"><h3>ふたりで話し合うと良いこと</h3><p id="rTalk"></p></div>"""
    pr_lead = '結婚観について誰かに話しながら考えを整理したいときの選択肢の一つとして、電話で相談できるサービスがあります。利用するかどうかは自由です。'
    data = 'var NUMS=' + json.dumps({str(k): v for k, v in NUMBERS.items()}, ensure_ascii=False) + ';'
    run = r"""
$('run').addEventListener('click',function(){
  var dt=readDate('a');
  if(!dt){showErr();return;}
  var n=lifePath(dt),r=NUMS[String(n)],nm='ライフパス'+n;
  $('rName').textContent=String(n);
  $('rSub').textContent=(n>9?'特別な数（マスターナンバー）':'ライフパスナンバー');
  $('rLabel').textContent=r.label;
  $('rView').textContent=r.view;
  $('rPartner').textContent=r.partner;
  $('rTalk').textContent=r.talk;
  setShare(nm);
  showRes(dt);
  track('uranai_complete',{tool:SLUG,result:nm});
});
"""
    return slug, page(slug, title=title, desc=desc,
                      og_title='数秘術でみる結婚観占い（無料・娯楽）',
                      og_desc='生年月日からライフパスナンバーを出し、結婚観・パートナーシップの傾向・話し合うと良いことを表示します。',
                      h1='数秘術でみる結婚観占い（無料・娯楽）',
                      hero_p='生年月日のライフパスナンバーから、結婚観とふたりで話し合うと良いことを読みます。登録なし・入力は生年月日だけ。',
                      hero_img='rings-bouquet.jpg', emblem='rings.png', bg='rings-bouquet.jpg',
                      lead_html=lead, form_html=form, result_html=result_shell(slug, head, bodyr, pr_lead),
                      body_sections=body, faqs=faqs, data_js=data, run_js=run, name=name)


# ---------------------------------------------------------------- 相性
def build_aisho():
    slug = 'aisho-uranai'
    name = '生年月日でみる二人の相性占い（無料・娯楽）'
    title = '生年月日でみる二人の相性占い（無料）｜関係の傾向と話し方のヒント'
    desc = '二人の生年月日から、星座のエレメントと数秘術のナンバーを組み合わせて6つの相性タイプに分け、関係の傾向・すれ違いやすい点・話し方のヒントを表示する無料の娯楽占いです。入力は送信・保存しません。'
    types = ''.join(f'<li><strong>{v["name"]}</strong>——{v["trend"].split("。")[0]}。</li>' for v in COMPAT.values())
    body = f"""<h2>相性タイプの決め方</h2>
<p>この占いは、二人それぞれの<strong>星座のエレメント</strong>（火・地・風・水）と、<strong>数秘術のライフパスナンバー</strong>を組み合わせて、相性のタイプを決めています。</p>
<div class="table-wrap"><table>
<thead><tr><th>見るところ</th><th>分け方</th></tr></thead>
<tbody>
<tr><td>エレメントの関係</td><td>同じエレメント／補い合う組み合わせ（火と風、地と水）／性質の異なる組み合わせ</td></tr>
<tr><td>数のリズム</td><td>ナンバーが奇数どうし・偶数どうし（リズムが近い）／奇数と偶数（リズムが異なる）。11・22・33はそれぞれ2・4・6として扱います</td></tr>
</tbody>
</table></div>
<p>この2つの組み合わせで、次の6タイプに分かれます。</p>
<ul>{types}</ul>

<h2>相性に良し悪しはありません</h2>
<p>6つのタイプは、相性の良い順に並べたものではありません。それぞれに、自然にうまくいきやすいところと、すれ違いやすいところがあります。結果の「話し方のヒント」は、すれ違いを小さくするための具体的な工夫です。</p>
<p>二人で結果を見ながら「ここは当てはまる」「ここは違う」と話すだけでも、お互いの考えを知るきっかけになります。それぞれの星座の傾向は<a href="/tools/seiza-renai-uranai/">星座でみる恋愛傾向占い</a>、結婚観は<a href="/tools/suhi-kekkon-uranai/">数秘術でみる結婚観占い</a>で詳しく読めます。</p>
"""
    faqs = [
        ('相性タイプはどうやって決まりますか？',
         '二人の星座のエレメント（火・地・風・水）が同じか、補い合う組み合わせか、性質の異なる組み合わせかの3通りと、数秘術のナンバーのリズムが近いか異なるかの2通りを組み合わせ、6つのタイプに分けています。'),
        ('相性が悪い組み合わせはありますか？',
         'この占いでは、相性を良し悪しで分けていません。どのタイプにも、自然にうまくいきやすい点とすれ違いやすい点があり、それぞれに話し方のヒントを用意しています。'),
        ('相手の生年月日を入力しても大丈夫ですか？',
         '入力した生年月日はお使いのブラウザの中だけで計算し、当サイトのサーバーや第三者には送信せず、保存もしません。それでも相手の個人的な情報なので、できれば相手にひと声かけてから、二人で一緒に楽しむのがおすすめです。'),
        ('星座の境目の日に生まれた場合はどうなりますか？',
         '一般的な区切りの日付で星座を決めています。太陽が星座を移る日は生まれた年により1日ほど前後するため、境目に近い方は、星座でみる恋愛傾向占いでとなりの星座の結果もあわせて読んでみてください。'),
        ('結果を二人の話し合いにどう使えばよいですか？',
         '「すれ違いやすい点」を読んで、二人のあいだで似た場面があったかを話してみてください。そのうえで「話し方のヒント」から一つだけ選んで試すと、取り入れやすくなります。結果は二人の関係を決めるものではなく、話題のきっかけです。'),
    ]
    lead = '<blockquote>二人の生年月日を選ぶと、星座のエレメントと数秘術のナンバーから<strong>相性のタイプ</strong>を出し、<strong>関係の傾向</strong>、<strong>すれ違いやすい点</strong>、<strong>話し方のヒント</strong>を表示します。名前や悩みの入力はありません。</blockquote>'
    form = date_fields('a', 'あなたの生年月日') + '\n' + date_fields('b', 'お相手の生年月日')
    head = """<div class="lbl">二人の相性タイプ</div>
<div class="num" id="rName">—</div>
<div class="pair"><div class="cell">あなた<b id="rA"></b></div><div class="cell">お相手<b id="rB"></b></div></div>
<div class="sub" id="rSub" style="margin-top:10px"></div>"""
    bodyr = """<div class="r-block"><h3>関係の傾向</h3><p id="rTrend"></p></div>
<div class="r-block"><h3>すれ違いやすい点</h3><p id="rGap"></p></div>
<div class="r-block"><h3>話し方のヒント</h3><p id="rTalk"></p></div>"""
    pr_lead = '二人の関係について、第三者に話しながら気持ちを整理したいときの選択肢の一つとして、電話で相談できるサービスがあります。利用するかどうかは自由です。'
    data = 'var SIGNS=' + json.dumps([{'name': s['name'], 'elem': s['elem']} for s in SIGNS], ensure_ascii=False) + ';\n'
    data += 'var COMPAT=' + json.dumps({f'{a}-{b}': v for (a, b), v in COMPAT.items()}, ensure_ascii=False) + ';\n'
    data += "var REL={same:'同じエレメント',comp:'補い合うエレメント',diff:'性質の異なるエレメント'};var RHY={same:'数のリズムが近い',diff:'数のリズムが異なる'};"
    run = r"""
function relOf(a,b){
  if(a===b)return 'same';
  var p=[a,b].sort().join('');
  if(p===['火','風'].sort().join('')||p===['地','水'].sort().join(''))return 'comp';
  return 'diff';
}
function base(n){return n===11?2:n===22?4:n===33?6:n;}
$('run').addEventListener('click',function(){
  var a=readDate('a'),b=readDate('b');
  if(!a||!b){showErr();return;}
  var sa=SIGNS[signOf(a.m,a.d)],sb=SIGNS[signOf(b.m,b.d)];
  var na=lifePath(a),nb=lifePath(b);
  var rel=relOf(sa.elem,sb.elem),rhy=(base(na)%2===base(nb)%2)?'same':'diff';
  var t=COMPAT[rel+'-'+rhy];
  $('rName').textContent=t.name;
  $('rA').textContent=sa.name+'（'+sa.elem+'）・'+na;
  $('rB').textContent=sb.name+'（'+sb.elem+'）・'+nb;
  $('rSub').textContent=REL[rel]+' × '+RHY[rhy];
  $('rTrend').textContent=t.trend;
  $('rGap').textContent=t.gap;
  $('rTalk').textContent=t.talk;
  setShare(t.name);
  showRes(a,b);
  track('uranai_complete',{tool:SLUG,result:t.name});
});
"""
    return slug, page(slug, title=title, desc=desc,
                      og_title='生年月日でみる二人の相性占い（無料・娯楽）',
                      og_desc='二人の生年月日から6つの相性タイプを出し、関係の傾向・すれ違いやすい点・話し方のヒントを表示します。',
                      h1='生年月日でみる二人の相性占い（無料・娯楽）',
                      hero_p='二人の生年月日から、星座のエレメントと数秘術で相性のタイプを出し、話し方のヒントを読みます。登録なし・入力は生年月日だけ。',
                      hero_img='hands-touch.jpg', emblem='couple.png', bg='hands-touch.jpg',
                      lead_html=lead, form_html=form, result_html=result_shell(slug, head, bodyr, pr_lead),
                      body_sections=body, faqs=faqs, data_js=data, run_js=run, name=name)


# ---------------------------------------------------------------- OGP
def build_og(slug, title, sub, chips):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    im = Image.new('RGB', (W, H), '#faf9f7')
    d = ImageDraw.Draw(im)
    font = 'C:/Windows/Fonts/meiryob.ttc'
    fr = 'C:/Windows/Fonts/meiryo.ttc'
    d.rectangle([0, 0, 18, H], fill='#7c2e42')
    d.rectangle([60, 60, W - 60, H - 60], outline='#e6e2dc', width=2)
    f_site = ImageFont.truetype(fr, 26)
    d.text((100, 92), 'Noe結婚設計室｜無料・娯楽の占い', font=f_site, fill='#7c2e42')
    size = 64
    f_t = ImageFont.truetype(font, size)
    while d.textlength(title, font=f_t) > W - 200 and size > 40:
        size -= 2
        f_t = ImageFont.truetype(font, size)
    d.text((100, 150), title, font=f_t, fill='#1d242b')
    f_s = ImageFont.truetype(fr, 30)
    d.text((100, 150 + size + 30), sub, font=f_s, fill='#454b52')
    # カード
    n = len(chips)
    gap = 18
    cw = (W - 200 - gap * (n - 1)) / n
    y0, y1 = 360, 500
    f_c = ImageFont.truetype(font, 32)
    f_c2 = ImageFont.truetype(fr, 20)
    for i, (big, small) in enumerate(chips):
        x0 = 100 + i * (cw + gap)
        d.rectangle([x0, y0, x0 + cw, y1], fill='#ffffff', outline='#d9d2c8', width=2)
        d.rectangle([x0, y0, x0 + cw, y0 + 6], fill='#7c2e42')
        tw = d.textlength(big, font=f_c)
        d.text((x0 + (cw - tw) / 2, y0 + 34), big, font=f_c, fill='#7c2e42')
        sw = d.textlength(small, font=f_c2)
        d.text((x0 + (cw - sw) / 2, y0 + 90), small, font=f_c2, fill='#757c83')
    f_u = ImageFont.truetype(fr, 22)
    d.text((100, 525), f'noe-match.com/tools/{slug}/', font=f_u, fill='#8a9097')
    out = os.path.join(ROOT, 'images', f'{slug}-og.png')
    im.save(out, optimize=True)
    return out


def main():
    built = [build_seiza(), build_suhi(), build_aisho()]
    for slug, src in built:
        dpath = os.path.join(ROOT, 'tools', slug)
        os.makedirs(dpath, exist_ok=True)
        with open(os.path.join(dpath, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(src)
        print('wrote', slug, len(src))
    print(build_og('seiza-renai-uranai', '星座でみる恋愛傾向占い', '生年月日から12星座の恋愛傾向と婚活のヒント',
                   [('火', '牡羊・獅子・射手'), ('地', '牡牛・乙女・山羊'), ('風', '双子・天秤・水瓶'), ('水', '蟹・蠍・魚')]))
    print(build_og('suhi-kekkon-uranai', '数秘術でみる結婚観占い', 'ライフパスナンバーで読む結婚観と話し合いのヒント',
                   [('1〜3', '自立・寄り添い・笑い'), ('4〜6', '土台・変化・家族'), ('7〜9', '静けさ・目標・寛容'), ('11・22・33', '特別な数')]))
    print(build_og('aisho-uranai', '生年月日でみる二人の相性占い', '星座のエレメント×数秘で6つの相性タイプ',
                   [('同じ', 'エレメント'), ('補い合う', 'エレメント'), ('異なる', 'エレメント'), ('×リズム', '近い・異なる')]))


if __name__ == '__main__':
    main()
