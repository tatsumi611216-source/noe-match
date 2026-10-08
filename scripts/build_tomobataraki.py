# -*- coding: utf-8 -*-
"""共働き世帯の割合｜ツールページを生成する（2026-10-08 新設）

狙う語: 「共働き 割合」「共働き世帯 推移」
  tool_gate 記録: GO（月2,880）
  GSC 実績: 表示515・平均54位（既存 articles/tomobataraki-wariai-data に着地）

正本: scripts/data/setai_kyoudou_sengyou.json（build_sengyoshufu.py と同じ）
対のデータ記事 articles/tomobataraki-wariai-data は 2026-10-13 までロック中＝触らない。

ASPゲート: 2026-08-31 last_updated → 38日 → 閉鎖
  → Oisixアフィリエイトなし。LINE CTAのみ。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import faq_html, source_list, table, write

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(io.open(os.path.join(HERE, "data", "setai_kyoudou_sengyou.json"), encoding="utf-8"))

TODAY = "2026-10-08"
CHECKED = D["checked"]
TOOL_SLUG = "tomobataraki-wariai"
ART_SLUG = "tomobataraki-wariai-data"
TOOL_URL = "https://www.noe-match.com/tools/%s/" % TOOL_SLUG

S = {s["year"]: s for s in D["series"]}
YEARS = sorted(S)
LATEST = YEARS[-1]
FIRST = YEARS[0]


def share_k(y):
    """共働き世帯 ÷（専業主婦世帯＋共働き世帯）。全国値が無い年は None"""
    s = S[y]
    if s["sengyou"] is None:
        return None
    return 100.0 * s["kyoudou"] / (s["sengyou"] + s["kyoudou"])


def share_k_excl3(y):
    s = S[y]
    return 100.0 * s["kyoudou_excl3"] / (s["sengyou_excl3"] + s["kyoudou_excl3"])


def bai(y):
    """共働き世帯 ÷ 専業主婦世帯"""
    s = S[y]
    return None if s["sengyou"] is None else float(s["kyoudou"]) / s["sengyou"]


def man(v):
    return "{:,}万世帯".format(v)


def rate(key, a, b):
    return (S[b][key] - S[a][key]) * 100.0 / S[a][key]


L = S[LATEST]
SH_L = share_k(LATEST)
SH_F = share_k(FIRST)

# 検算: 共働き割合は専業主婦割合の裏なので合計100%になる
for y in YEARS:
    s = S[y]
    if s["sengyou"] is not None:
        assert abs((100.0 * s["sengyou"] / (s["sengyou"] + s["kyoudou"])) + share_k(y) - 100.0) < 0.01, \
            "合計100%%にならない年: %d" % y

assert LATEST == 2025 and L["sengyou"] == 358 and L["kyoudou"] == 1254, "正本の最新年が想定と違う"

SRC = [(s["url"], s["label"]) for s in D["sources"]]
SRC_INTRO = ("このページの数値はすべて次の内閣府の公表値（原資料は総務省『労働力調査』）です。"
             "割合・倍率は、公表された世帯数から当サイトが計算しました。")

ALL_ROWS = []
for y in YEARS:
    s = S[y]
    if s["sengyou"] is None:
        ALL_ROWS.append(("%d年" % y, "（全国値なし）", "（全国値なし）", "—", "—"))
    else:
        ALL_ROWS.append(("%d年" % y, man(s["kyoudou"]), man(s["sengyou"]),
                         "%.1f%%" % share_k(y), "%.2f倍" % bai(y)))

FIVE = [y for y in YEARS if y % 5 == 0]

# ------------------------------------------------------------------ ツール
TOOL_TITLE = "共働き世帯の割合を年別に調べる｜%d〜%d年" % (FIRST, LATEST)
TOOL_H1 = "共働き世帯の割合を年で調べる｜%d年〜%d年の世帯数と割合" % (FIRST, LATEST)
assert len(TOOL_TITLE) <= 32, "title %d字" % len(TOOL_TITLE)

FAQ_TOOL = [
    ("このツールで何が分かりますか？",
     "%d年から%d年までの好きな年を選ぶと、その年の共働き世帯数、専業主婦世帯数、"
     "2つの合計に占める共働き世帯の割合、共働き世帯が専業主婦世帯の何倍か、"
     "最新年との差が出ます。もう1つ年を選ぶと、2つの年の差も出ます。"
     "数値は内閣府『男女共同参画白書 令和8年版』の公表値です。" % (FIRST, LATEST)),
    ("%d年の共働き世帯の割合はいくつですか？" % LATEST,
     "内閣府『男女共同参画白書 令和8年版』の系列では、%d年の共働き世帯は%s、専業主婦世帯は%sで、"
     "両者の合計に占める共働き世帯の割合は%.1f%%です。共働き世帯は専業主婦世帯の%.2f倍にあたります。"
     "この系列は「妻が64歳以下で、夫が非農林業の雇用者」の世帯に限った数字で、全世帯に占める割合ではありません。"
     % (LATEST, man(L["kyoudou"]), man(L["sengyou"]), SH_L, bai(LATEST))),
    ("割合はどう計算していますか？",
     "共働き世帯 ÷（共働き世帯 ＋ 専業主婦世帯）です。"
     "どちらも「妻が64歳以下で、夫が非農林業の雇用者」の世帯に限った数なので、"
     "全世帯や全女性に占める割合ではありません。自営業の家庭や、妻が65歳以上の家庭は含まれていません。"),
    ("共働き世帯はいつ専業主婦世帯を上回りましたか？",
     "この系列で計算すると、共働き世帯の数が専業主婦世帯を初めて上回ったのは%d年です。"
     "「1997年に逆転した」という説明を見かけますが、現在公表されているこの系列の実数では、"
     "%d年には共働き世帯（%s）が専業主婦世帯（%s）をすでに上回っていました。"
     % (next(y for y in YEARS if S[y]["sengyou"] is not None and S[y]["kyoudou"] > S[y]["sengyou"]),
        1997, man(S[1997]["kyoudou"]), man(S[1997]["sengyou"]))),
    ("2011年の数字が無いのはなぜですか？",
     "東日本大震災の影響で、2011年は全国の値が公表されていません。岩手県・宮城県・福島県を除いた値"
     "（共働き世帯%s・専業主婦世帯%s）だけがあります。3県を除いた値で計算すると共働き世帯の割合は%.1f%%ですが、"
     "前後の年の全国値とはそのまま比べられません。"
     % (man(S[2011]["kyoudou_excl3"]), man(S[2011]["sengyou_excl3"]), share_k_excl3(2011))),
    ("30代・40代など年代別の共働き割合は分かりますか？",
     "この系列では分かりません。白書のこの図表は妻が64歳以下の世帯をまとめた合計で、"
     "妻の年代別の内訳はありません。年代別の数字を載せているページは別の統計を使っているはずです。"
     "見るときはどの統計のどの表からの数字か、分母が何かを確認してください。"
     "当サイトでは年代別の一次データを確認できていないため、掲載していません。"),
]

JS_DATA = [{"y": y, "s": S[y]["sengyou"], "k": S[y]["kyoudou"],
             "p": S[y]["part"], "f": S[y]["fulltime"],
             "s3": S[y]["sengyou_excl3"], "k3": S[y]["kyoudou_excl3"],
             "sh": (None if share_k(y) is None else round(share_k(y), 1)),
             "bai": (None if bai(y) is None else round(bai(y), 2))} for y in YEARS]

FIVE_ROWS = [r for r in ALL_ROWS if int(r[0][:4]) % 5 == 0]

TOOL_TPL = u"""<!DOCTYPE html>
<html lang="ja">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VLQBH0S1SL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-VLQBH0S1SL');</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<link rel="canonical" href="__URL__">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__OGD__">
<meta property="og:type" content="website">
<meta property="og:url" content="__URL__">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__TITLE__">
<meta name="twitter:description" content="__OGD__">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@500;600;700;900&display=swap" rel="stylesheet">
__CSS__
<style>
.pick{display:flex;flex-wrap:wrap;gap:14px 22px;align-items:flex-end}
.pick label{display:block;font-weight:700;color:#1d242b;font-size:.92rem;margin:0 0 6px}
.pick select{padding:10px 12px;border:1px solid #d8d2c8;border-radius:4px;font-size:1rem;background:#fff;min-width:150px}
.dt{width:100%;min-width:0;table-layout:fixed;border-collapse:collapse;margin:14px 0 0;font-size:.9rem;word-break:break-all}
.dt th,.dt td{border-bottom:1px solid #e6e2da;padding:9px 8px;text-align:left}
.dt th{width:54%;color:#5a6068;font-weight:500}
.dt td{font-weight:700;color:#7c2e42}
.bars{margin:18px 0 0}
.bars .row{display:flex;align-items:center;gap:8px;font-size:.72rem;color:#6b7178;line-height:1;margin:2px 0}
.bars .row span.y{width:3.2em;text-align:right;flex:none}
.bars .row span.b{display:block;height:9px;background:#d9cfc4;border-radius:2px}
.bars .row.on span.b{background:#7c2e42}
.bars .row.on{color:#1d242b;font-weight:700}
.bars .row span.v{flex:none}
table.cmp td.n{text-align:right;font-weight:700;color:#7c2e42;white-space:nowrap}
.srcline{font-size:.78rem;color:#6b7178;line-height:1.9;margin:8px 0 0}
</style>
<script type="application/ld+json">__FAQLD__</script>
<script type="application/ld+json">__APPLD__</script>
<script type="application/ld+json">__BCLD__</script>
</head>
<body>
<header><div class="header-inner">
<a href="/" class="logo">Noe結婚設計室<span class="logo-badge">2026</span></a>
<nav><a href="/#tools">ツール</a><a href="/articles/">記事一覧</a><a href="/#faq">FAQ</a><a href="/#about">運営者</a></nav>
</div></header>
<div class="wrap">
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ 共働き世帯の割合を年別に調べる</div>

<div class="tool-hero" style="background-image:url('../../images/lp/room-light.jpg')"><div class="tool-hero-inner">
<h1>__H1__</h1>
<p>年を選ぶと、その年の共働き世帯と専業主婦世帯の数、共働き世帯の割合、最新年との差が出ます。数値は内閣府『男女共同参画白書 令和8年版』の公表値で、__CHECKED__に原典のCSVで確認しました。</p>
</div></div>

<article>
<p class="pr-notice">本ページはプロモーションを含みます。掲載している統計の数値と計算は、広告とは関係なく公表値にもとづいています。</p>
<blockquote><strong>__LATEST__年の共働き世帯の割合は__SHK__%です（共働き世帯__LK__万世帯・専業主婦世帯__LS__万世帯）。</strong>この割合は「共働き世帯 ÷（共働き世帯＋専業主婦世帯）」で、どちらも妻が64歳以下・夫が雇用者の世帯に限った数です。全世帯に占める割合ではありません。</blockquote>

<h2 id="shiraberu">年を選ぶ</h2>
<div class="calc" id="calcForm">
  <div class="pick">
    <div><label for="y1">調べたい年</label><select id="y1"></select></div>
    <div><label for="y2">比べる年（任意）</label><select id="y2"></select></div>
  </div>
  <button type="button" class="calc-btn" id="run" style="margin-top:18px">この年の数字を見る</button>
</div>

<div class="result" id="result" aria-live="polite">
  <div class="big"><div class="lbl" id="rLbl"></div><div class="num" id="rNum"></div></div>
  <table class="dt" id="rTable"></table>
  <div id="rCmp"></div>
  <p id="rNote" style="font-size:.8rem;color:#6b7178;margin:14px 0 0;line-height:1.9"></p>
  <div class="bars" id="bars" aria-hidden="true"></div>
  <p style="font-size:.78rem;color:#6b7178;margin:14px 0 0;line-height:1.9">棒は共働き世帯の割合（__FIRST__年〜__LATEST__年）。出典は内閣府『男女共同参画白書 令和8年版』特-5図・特-6図（__CHECKED__確認）。割合と倍率は公表された世帯数から当サイトが計算しています。差は四捨五入する前の値から計算しているため、表示された割合どうしの引き算と0.1ずれることがあります。</p>
  <section id="line-cta-result" style="border:1px solid #e3ddd3;background:#f7f5f2;padding:18px 18px 20px;margin:24px 0 0;text-align:center">
    <p style="margin:0 0 6px;font-size:11px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif">NOE OFFICIAL LINE</p>
    <p style="margin:0 0 10px;font-size:16px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5">公表値が更新されたらお知らせします</p>
    <p style="margin:0 0 16px;font-size:13px;color:#5a6068;line-height:1.85">白書・国勢調査・人口動態統計など、このサイトで使っている統計の更新を月1回まとめて配信します。</p>
    <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{gtag('event','line_add_result',{tool:'__SLUG__'});}catch(e){}" style="display:inline-block;background:#7c2e42;color:#ffffff;padding:12px 30px;font-size:14px;font-weight:600;text-decoration:none">友だち追加する</a>
    <p style="margin:10px 0 0;font-size:11px;color:#8a8f95">登録は無料。いつでも解除できます。</p>
  </section>
</div>

<h2 id="teigi">この割合が指しているもの</h2>
<p>このツールの割合は、次の式で計算しています。</p>
<p><strong>共働き世帯 ÷（共働き世帯 ＋ 専業主婦世帯）</strong></p>
<ul>
<li><strong>共働き世帯</strong>：__T_KYOUDOU__</li>
<li><strong>専業主婦世帯</strong>：__T_SENGYOU__</li>
</ul>
<p>__T_FUKUMANAI__ 分母は「夫が会社などに雇われていて、妻が64歳以下の夫婦」だけなので、「日本の女性の何%が共働きか」「全世帯の何%が共働き世帯か」という問いの答えにはなりません。その数字はこの系列からは計算できないため、載せていません。</p>

<h2 id="ichiran">5年ごとの早見表</h2>
__FIVE_TABLE__
<p class="srcline">全__TOTAL__年ぶんの表と、逆転した年・5年ごとの増減率・フルタイムとパートの内訳は、<a href="/articles/__ART__/">共働き世帯の割合はどれくらい？</a>にまとめています。</p>

<h2 id="chui">数字を見るときの注意</h2>
<h3>2011年は全国値がありません</h3>
<p>__Y2011__ このツールで2011年を選ぶと、3県を除く値を参考として表示します。</p>
<h3>調査が途中で切り替わっています</h3>
<p>__CHOUSA__</p>
<h3>年代別の割合は出せません</h3>
<p>この系列は妻が64歳以下の世帯をまとめた合計で、30代・40代といった妻の年代別の内訳はありません。当サイトでは年代別の一次データを確認できていないため、掲載していません。</p>

<h2 id="faq">よくある質問（FAQ）</h2>
__FAQHTML__

<h2 id="src">出典</h2>
<p>__SRCINTRO__（__CHECKED__確認）</p>
<ul style="font-size:.86rem;line-height:2">
__SRCLIST__
</ul>

<h2 id="related">関連するツールと記事</h2>
<ul>
<li><a href="/articles/__ART__/">共働き世帯の割合はどれくらい？</a>｜全年分の表・逆転した年・増減率</li>
<li><a href="/tools/sengyoshufu-wariai/">専業主婦の割合を年別に調べる</a>｜同じ系列を専業主婦の側から読む</li>
<li><a href="/articles/sengyoshufu-wariai-data/">専業主婦世帯の割合｜40年の推移データ</a>｜全41年の表と節目の年</li>
<li><a href="/articles/tomobataraki-shokuji-data/">共働き夫婦の食事はどうしている？</a>｜自炊・ミールキット・外食の費用と時間</li>
<li><a href="/tools/seikatsuhi-simulator/">ふたりの生活費シミュレーション</a>｜家賃・食費・分担を試算</li>
</ul>
</article>

<!-- LINE-CTA -->
<section id="line-cta" style="max-width:680px;margin:56px auto 64px;padding:36px 28px;background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;">
  <p style="margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif;">NOE OFFICIAL LINE</p>
  <p style="margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5;">公表値が更新されたらお知らせします</p>
  <p style="margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;">白書・国勢調査・人口動態統計など、このサイトで使っている統計の更新を月1回まとめて配信します。</p>
  <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{gtag('event','line_add_click',{tool:'__SLUG__'});}catch(e){}"
     style="display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;font-size:15px;font-weight:600;text-decoration:none;">友だち追加する</a>
  <p style="margin:14px 0 0;font-size:11px;color:#8a8f95;">登録は無料・配信は月1回だけ。いつでも解除できます。</p>
</section>
</div>
<footer><div class="footer-inner">
<div><a href="/">ホーム</a><a href="/articles/">記事一覧</a><a href="/about.html">運営者情報</a><a href="/privacy-policy.html">プライバシー</a><a href="/disclaimer.html">免責事項</a></div>
<p class="footer-disc">※本ツールの数値は内閣府男女共同参画局『男女共同参画白書 令和8年版』の公表値（__CHECKED__確認）です。割合・倍率は公表された世帯数から当サイトが計算しています。<strong style="color:#cda">【PR】</strong>本サイトはアフィリエイト広告を利用しています。</p>
</div></footer>
<button id="top" onclick="scrollTo({top:0,behavior:'smooth'})">↑</button>
<script>
(function(){
  var DATA=__JSDATA__;
  var LATEST=__LATEST__;
  var by={};DATA.forEach(function(d){by[d.y]=d;});
  function $(id){return document.getElementById(id);}
  function fmt(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,',');}
  var y1=$('y1'),y2=$('y2');
  var o0=document.createElement('option');o0.value='';o0.textContent='選ばない';y2.appendChild(o0);
  for(var i=DATA.length-1;i>=0;i--){
    var a=document.createElement('option');a.value=DATA[i].y;a.textContent=DATA[i].y+'年';y1.appendChild(a);
    var b=document.createElement('option');b.value=DATA[i].y;b.textContent=DATA[i].y+'年';y2.appendChild(b);
  }
  function vals(d){
    if(d.s!==null){
      var sh=Math.round(d.k*1000/(d.s+d.k))/10;
      return {s:d.s,k:d.k,sh:sh,shr:d.k*100/(d.s+d.k),bai:d.bai,ex:false};
    }
    var sh=Math.round(d.k3*1000/(d.s3+d.k3))/10;
    return {s:d.s3,k:d.k3,sh:sh,shr:d.k3*100/(d.s3+d.k3),bai:Math.round(d.k3*100/d.s3)/100,ex:true};
  }
  function row(th,td){return '<tr><th>'+th+'</th><td>'+td+'</td></tr>';}
  function sign(n,unit){var r=Math.round(n*10)/10;var t=(unit==='ポイント')?r.toFixed(1):fmt(Math.abs(r));if(unit!=='ポイント'){t=(r<0?'-':'')+t;}return (r>0?'+':'')+t+unit;}
  function draw(sel){
    var max=100,h='';
    DATA.forEach(function(d){
      if(d.sh===null){h+='<div class="row'+(d.y==sel?' on':'')+'"><span class="y">'+d.y+'</span><span class="v">全国値なし</span></div>';return;}
      h+='<div class="row'+(d.y==sel?' on':'')+'"><span class="y">'+d.y+'</span><span class="b" style="width:'+(d.sh/max*78).toFixed(1)+'%"></span><span class="v">'+d.sh.toFixed(1)+'%</span></div>';
    });
    $('bars').innerHTML=h;
  }
  function run(){
    var d=by[y1.value],v=vals(d),Lv=vals(by[LATEST]);
    $('rLbl').textContent=d.y+'年の共働き世帯の割合'+(v.ex?'（岩手・宮城・福島を除く参考値）':'');
    $('rNum').textContent=v.sh.toFixed(1)+'%';
    var t=row('共働き世帯',fmt(v.k)+'万世帯')+row('専業主婦世帯',fmt(v.s)+'万世帯')+row('共働き世帯 ÷ 専業主婦世帯',v.bai.toFixed(2)+'倍');
    if(d.f!==null){t+=row('共働きのうち妻フルタイム（週35時間以上）',fmt(d.f)+'万世帯')+row('共働きのうち妻パート（週35時間未満）',fmt(d.p)+'万世帯');}
    if(d.y!=LATEST){t+=row('最新（'+LATEST+'年・'+Lv.sh.toFixed(1)+'%）との差',sign(Lv.shr-v.shr,'ポイント'))+row('共働き世帯の増減（'+LATEST+'年まで）',sign(Lv.k-v.k,'万世帯'));}
    $('rTable').innerHTML=t;
    var c='';
    if(y2.value&&y2.value!=y1.value){
      var e=by[y2.value],w=vals(e);
      c='<h3 style="font-size:.96rem;margin:22px 0 0;color:#1d242b">'+d.y+'年と'+e.y+'年を比べる</h3><table class="dt">'
        +row(e.y+'年の共働き世帯の割合',w.sh.toFixed(1)+'%'+(w.ex?'（3県を除く参考値）':''))
        +row('割合の差（'+e.y+'年 − '+d.y+'年）',sign(w.shr-v.shr,'ポイント'))
        +row('共働き世帯の差',sign(w.k-v.k,'万世帯'))
        +row('専業主婦世帯の差',sign(w.s-v.s,'万世帯'))+'</table>';
    }
    $('rCmp').innerHTML=c;
    var n=[];
    if(v.ex||(y2.value&&by[y2.value]&&by[y2.value].s===null)){n.push('2011年は全国値が公表されていないため、岩手県・宮城県・福島県を除く値を参考として表示しています。前後の年の全国値とはそのまま比べられません。');}
    if(d.y<=2001||(y2.value&&Number(y2.value)<=2001)){n.push('1985〜2001年は『労働力調査特別調査』（各年2月）、2002年以降は『労働力調査（詳細集計）』で、調査の方法が違います。離れた年どうしの差は目安として見てください。');}
    $('rNote').textContent=n.join(' ');
    draw(d.y);
    $('result').classList.add('show');
    try{gtag('event','tool_result',{tool:'__SLUG__',year:String(d.y),compare:String(y2.value||'')});}catch(x){}
    try{$('result').scrollIntoView({behavior:'smooth',block:'start'});}catch(x){}
  }
  $('run').addEventListener('click',run);
})();
</script>
</body>
</html>"""


def build_tool():
    desc = ("%d年から%d年までの年を選ぶと、その年の共働き世帯数・専業主婦世帯数・共働き世帯の割合・最新年との差が出ます。"
            "%d年は共働き世帯%s・専業主婦世帯%sで、割合は%.1f%%。2つの年を比べることもできます。"
            "内閣府『男女共同参画白書 令和8年版』の公表値を%sに確認。割合の分母（妻64歳以下・夫が雇用者の世帯）も明記しています。"
            % (FIRST, LATEST, LATEST, man(L["kyoudou"]), man(L["sengyou"]), SH_L, CHECKED))
    ogd = ("共働き世帯の割合は%d年が%.1f%%、%d年が%.1f%%。年を選んで、その年の世帯数と割合を確かめられます。"
           % (FIRST, SH_F, LATEST, SH_L))
    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in FAQ_TOOL]}, ensure_ascii=False)
    app_ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebApplication",
        "name": "共働き世帯の割合を年別に調べる", "url": TOOL_URL,
        "applicationCategory": "UtilitiesApplication", "operatingSystem": "All",
        "inLanguage": "ja", "description": desc,
        "datePublished": TODAY, "dateModified": TODAY,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
        "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                      "url": "https://www.noe-match.com/"}}, ensure_ascii=False)
    bc_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
        {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": "https://www.noe-match.com/#tools"},
        {"@type": "ListItem", "position": 3, "name": "共働き世帯の割合を年別に調べる"}]}, ensure_ascii=False)
    shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
    css = shell[shell.find("<style>"):shell.find("</style>") + 8]
    html = TOOL_TPL
    for k, v in (("__TITLE__", TOOL_TITLE), ("__DESC__", desc), ("__OGD__", ogd), ("__URL__", TOOL_URL),
                 ("__H1__", TOOL_H1), ("__CSS__", css), ("__FAQLD__", faq_ld), ("__APPLD__", app_ld),
                 ("__BCLD__", bc_ld), ("__CHECKED__", CHECKED), ("__SLUG__", TOOL_SLUG), ("__ART__", ART_SLUG),
                 ("__LATEST__", str(LATEST)), ("__FIRST__", str(FIRST)),
                 ("__SHK__", "%.1f" % SH_L), ("__LK__", "{:,}".format(L["kyoudou"])),
                 ("__LS__", "{:,}".format(L["sengyou"])),
                 ("__T_KYOUDOU__", D["teigi"]["kyoudou"]), ("__T_SENGYOU__", D["teigi"]["sengyou"]),
                 ("__T_FUKUMANAI__", D["teigi"]["fukumanai"]), ("__Y2011__", D["y2011"]),
                 ("__CHOUSA__", D["chousa"]), ("__TOTAL__", str(len(YEARS))),
                 ("__FIVE_TABLE__", table(["年", "共働き世帯", "専業主婦世帯", "共働き世帯の割合", "共働き÷専業主婦"],
                                          FIVE_ROWS, ["", "n", "n", "n", "n"])),
                 ("__FAQHTML__", faq_html(FAQ_TOOL)), ("__SRCINTRO__", SRC_INTRO.rstrip("。") + "。"),
                 ("__SRCLIST__", "\n".join('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % s for s in SRC)),
                 ("__JSDATA__", json.dumps(JS_DATA, ensure_ascii=False, separators=(",", ":")))
                 ):
        html = html.replace(k, v)
    assert "__" not in html.replace("__proto__", ""), [m for m in __import__("re").findall(r"__[A-Z0-9_]+__", html)]
    os.makedirs("tools/%s" % TOOL_SLUG, exist_ok=True)
    io.open("tools/%s/index.html" % TOOL_SLUG, "w", encoding="utf-8", newline="\n").write(html)
    print("written: tools/%s/index.html  %d chars  title %d字: %s" % (TOOL_SLUG, len(html), len(TOOL_TITLE), TOOL_TITLE))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    os.chdir(os.path.dirname(HERE))
    build_tool()
