# -*- coding: utf-8 -*-
"""産後ケアのデータ記事を _sangocare_data.py から生成する（2026-08-27 新設）

狙う語は data_gate.py でGO判定だった2語:
  「産後ケア 何回」（サジェスト10件）／「産後ケア 助成」（サジェスト8件）
どちらも既存の受け皿が無く、43自治体の一次データは自社にしかない。

データ記事の型は「複数の公表値を横断で1枚の表にする＋出典＋確認日」。
実測ではこの型の流入はAI（chatgpt/copilot）とBingがほぼ全部で、
Google/Yahooは2セッションしかない。Google順位ではなくAIの引用を取りに行く。

分類は原文に忠実にする。上限が合算枠かどうかは自治体ごとに書き方が違うので、
こちらで意味を解釈せず、公表文に合算を示す語が含まれるかだけを機械的に見て、
表には必ず原文を載せる（8/25・8/27の教訓: 分類を勝手に決めない）。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _sangocare_data import CHECKED, CITIES

TODAY = "2026-08-27"
OISIX = "https://px.a8.net/svt/ejp?a8mat=45C0YR+2VBK6Q+3250+5YZ77"
GASSAN = ("あわせて", "合わせて", "合算", "通算", "内数", "合計")

real = [c for c in CITIES if c["key"] != "kokuhyo"]
N = len(real)


def has_gassan(c):
    s = c["limit_stay"] + c["limit_day"] + c["limit_visit"]
    return any(w in s for w in GASSAN)


gassan = [c for c in real if has_gassan(c)]

# 減免の書きぶりが「免除・0円」と明記されているものだけを拾う。
# 「減額」「半額」しか書いていない自治体は0円にならないので混ぜない。
menjo = [c for c in real if ("免除" in c["genmen"] or "無料" in c["genmen"]
                             or "無償" in c["genmen"] or "0円" in c["genmen"])]

# 所得を問わない減額枠を持つ自治体（実査本文で確認できたものだけを列挙する）
SHOTOKU_TOWANAI = {
    "chiyoda": "全利用者に2,500円引きの減免クーポンを5枚配付",
    "bunkyo": "全世帯対象に1回2,500円の減免を合計5回まで",
    "taito": "全世帯対象に1日2,500円の減免を合計5日まで",
    "saitama": "利用承認時にクーポン券5枚を自動配付（宿泊・デイは1枚2,500円引き）",
    "kawasaki": "一般世帯にも5回（日）目まで1日2,500円の減免",
    "sakai": "所得を問わない減額枠を3類型あわせて5回まで",
}
towanai = [c for c in real if c["key"] in SHOTOKU_TOWANAI]

shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
CSS = shell[shell.find("<style>"):shell.find("</style>") + 8]

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
<style>.src-cell a{{font-size:.8rem}} table.cmp td{{vertical-align:top;font-size:.85rem;line-height:1.85}}</style>
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
<p style="font-size:.78rem;color:#8a8f95;margin:6px 0 24px">公開 {today}／{checked}に{n}自治体の公式ページで確認</p>
<p class="pr-notice">本ページはプロモーションを含みます。記事内に広告主から成果報酬を受け取るリンクが含まれます。掲載内容は編集部の基準で作成しており、報酬の有無で評価を変えていません。</p>
{body}
<div style="border:1px solid #e3ddd3;border-radius:6px;padding:22px 24px;margin:32px 0;background:#faf8f5">
<p style="font-size:.7rem;color:#999;margin:0 0 6px">PR</p>
<p style="font-weight:900;margin:0 0 6px;color:#1d242b">産後ケアを使わない日の負担をどう下げるか</p>
<p style="font-size:.86rem;color:#5a6068;margin:0 0 16px;line-height:1.9">産後ケアの回数には上限があります。使える日は限られるので、それ以外の日をどう回すかが実際の問題になります。買い物と献立を考える時間を削るのはその一つです。</p>
<a href="{oisix}" rel="sponsored noopener" target="_blank" style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;padding:13px 32px;text-decoration:none">Oisixのおためしセットを見る</a>
<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">食材宅配サービス。産後ケア事業の利用可否とは関係ありません</p>
</div>
</article>
<!-- LINE-CTA -->
<section id="line-cta" style="max-width:680px;margin:56px auto 64px;padding:36px 28px;background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;">
  <p style="margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif;">NOE OFFICIAL LINE</p>
  <p style="margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5;">自治体の制度は年度で変わります</p>
  <p style="margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;">産後ケア・こども誰でも通園制度など、自治体ごとに違う制度の変更点を月1回お知らせします。<br>お住まいの自治体について調べてほしいことは、追加後そのままトークでどうぞ。</p>
  <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{{gtag('event','line_add_click',{{article:'{slug}'}});}}catch(e){{}}"
     style="display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;font-size:15px;font-weight:600;text-decoration:none;">友だち追加する</a>
  <p style="margin:14px 0 0;font-size:11px;color:#8a8f95;">登録は無料・配信は月1回だけ。いつでも解除できます。</p>
</section>
</div>
<footer><div class="footer-inner">
<div><a href="/">ホーム</a><a href="/articles/">記事一覧</a><a href="/about.html">運営者情報</a><a href="/privacy-policy.html">プライバシー</a><a href="/disclaimer.html">免責事項</a></div>
<p class="footer-disc">※本記事は各自治体の公式公開情報（{checked}確認）にもとづく整理です。制度の適用と最終的な判断は各自治体が行います。<strong style="color:#cda">【PR】</strong>本サイトはアフィリエイト広告を含みます。<br>&copy; 2026 Noe結婚設計室</p>
</div></footer>
<button id="top" onclick="scrollTo({{top:0,behavior:'smooth'}})">↑</button>
</body>
</html>"""


def build_ld(slug, title, desc, faq, h1):
    url = "https://www.noe-match.com/articles/%s/" % slug
    faqld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in faq]}, ensure_ascii=False)
    artld = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": title,
        "description": desc, "inLanguage": "ja",
        "datePublished": TODAY, "dateModified": TODAY,
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
    return url, faqld, artld, bcld


def faq_html(faq):
    return "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a)
                     for i, (q, a) in enumerate(faq))


def src_table():
    rows = "".join(
        '<tr><td>%s</td><td class="src-cell"><a href="%s" rel="noopener" target="_blank">%s</a></td><td>%s</td></tr>'
        % (c["name"], c["src"], c["src_label"], CHECKED) for c in real)
    return ('<h2 id="src">出典</h2>\n<p>数値はすべて各自治体の公式ページで確認しました。'
            '確認日は%s です。制度は年度で変わるため、利用前に必ず公式ページをご確認ください。</p>\n'
            '<div class="table-scroll"><table class="cmp"><thead><tr><th>自治体</th>'
            '<th>出典ページ</th><th>確認日</th></tr></thead><tbody>%s</tbody></table></div>'
            % (CHECKED, rows))


def write(slug, title, h1, desc, ogd, faq, body):
    url, faqld, artld, bcld = build_ld(slug, title, desc, faq, h1)
    html = HEAD.format(title=title, desc=desc, ogd=ogd, url=url, css=CSS,
                       faqld=faqld, artld=artld, bcld=bcld, h1=h1, n=N,
                       today=TODAY, checked=CHECKED, body=body, slug=slug,
                       oisix=OISIX)
    os.makedirs("articles/%s" % slug, exist_ok=True)
    io.open("articles/%s/index.html" % slug, "w", encoding="utf-8").write(html)
    print("written: articles/%s/index.html  %d chars" % (slug, len(html)))


# ---------------------------------------------------------------- 記事1: 何回
def article_nankai():
    rows = "".join(
        '<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
        % (c["name"], c["limit_stay"], c["limit_day"], c["limit_visit"],
           "記載あり" if has_gassan(c) else "—")
        for c in real)
    body = """
<blockquote><strong>産後ケアの「何回使えるか」は、回数の数字だけを見ても比べられません。</strong>類型ごとに枠を持つ自治体と、宿泊型・日帰り型・訪問型をまとめて数える自治体があるためです。%s自治体を確認したところ、上限の公表文に「あわせて」「合算」「通算」などの語が含まれる自治体が%d件ありました。同じ「7回まで」でも、3類型それぞれ7回なのか、3類型あわせて7回なのかで、受けられるケアの総量は3倍違います。</blockquote>

<h2 id="ichiran">%s自治体の上限一覧（公表文のまま）</h2>
<p>解釈を加えず、各自治体が公表している文言をそのまま載せています。「合算の記載」列は、上限の公表文に合算を示す語が含まれるかどうかだけを示すもので、制度の解釈ではありません。実際の数え方は必ず自治体にご確認ください。</p>
<div class="table-scroll">
<table class="cmp">
<thead><tr><th>自治体</th><th>宿泊型</th><th>日帰り型</th><th>訪問型</th><th>合算の記載</th></tr></thead>
<tbody>%s</tbody>
</table>
</div>

<h2 id="chui">回数を比べるときに間違えやすいところ</h2>
<h3>「1泊2日」が何日ぶんになるかが自治体で違う</h3>
<p>宿泊型の枠の消費のしかたも揃っていません。1泊2日を「2日」と数える自治体と、「1回」と数える自治体があります。名古屋市は泊数に1を足して日数を数えるため1泊2日は2日ぶん、京都市は1回を24時間とするため1泊2日で1回です。同じ「7日（回）まで」でも、実際に泊まれる回数が倍違います。</p>
<h3>多胎児は上限が増える自治体がある</h3>
<p>多胎児（双子以上）の場合に上限を上乗せする自治体があります。公表文にその旨が書かれている場合は上の表にも含めています。加算の有無と幅は自治体ごとに違うため、該当する場合は個別に確認してください。</p>
<h3>キャンセルが枠を消費することがある</h3>
<p>当日キャンセルや前日の一定時刻以降のキャンセルを、利用したものとして枠から差し引く自治体があります。回数に余裕がない設計なので、キャンセル規定は申込みの前に確認しておくと安全です。</p>
<h3>対象期間が短いと、回数があっても使い切れない</h3>
<p>制度としては産後1年未満でも、宿泊型と日帰り型は「産後4か月未満」「産後5か月未満」と短く設定している自治体があります。さらに施設ごとに受入可能な月齢が決まっているため、回数の上限より先に期間で使えなくなることがあります。</p>

<h2 id="calc">自分の場合の自己負担を計算する</h2>
<p>回数と自己負担額をあわせて確かめる場合は、<a href="/tools/sangokea-ryokin/">産後ケアの料金を自治体別に調べるツール</a>が使えます。使いたい回数を入れると、その自治体の自己負担の合計と上限の公表文が出ます。</p>

<h2 id="faq">よくある質問（FAQ）</h2>
%s

%s

<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/tools/sangokea-ryokin/">産後ケアの料金はいくら？自治体別の自己負担</a></li>
<li><a href="/articles/sangokea-josei/">産後ケアの助成はいくら？非課税世帯の減免と所得を問わない減額枠</a></li>
<li><a href="/articles/daredemo-tsuen-ryokin/">こども誰でも通園制度の料金はいくら？46自治体の実額と減免</a></li>
<li><a href="/articles/sango-crisis-guide/">産後クライシスはいつから？原因と、こじれる前の手当て</a></li>
<li><a href="/articles/sango-satogaeri/">里帰り出産する・しないの判断材料</a></li>
<li><a href="/tools/ikukyu-encho-hantei/">育休はいつまで延長できる？条件と必要書類の判定</a></li>
</ul>
""" % (N, len(gassan), N, rows, faq_html(FAQ_NANKAI), src_table())

    write("sangokea-nankai",
          "産後ケアは何回使える？東京23区＋政令市%s自治体の上限一覧【2026年度】" % N,
          "産後ケアは何回使える？｜%s自治体の上限回数と「合算枠」の落とし穴" % N,
          "産後ケアの利用回数の上限は市区町村が決めるため自治体で違います。さらに類型ごとに枠を持つ自治体と、"
          "宿泊型・日帰り型・訪問型をまとめて数える自治体があり、同じ「7回まで」でも受けられるケアの総量が3倍"
          "違います。東京23区と政令指定都市の計%s自治体について、公表文のまま上限を一覧にしました。"
          "1泊2日が何日ぶんになるかの違い、多胎児の上乗せ、キャンセルの扱いも整理しています。確認日は%s。" % (N, CHECKED),
          "産後ケアの回数上限を%s自治体ぶん、公表文のまま一覧に。類型ごとの枠か合算枠かで総量が3倍違います。" % N,
          FAQ_NANKAI, body)


FAQ_NANKAI = [
 ("産後ケアは何回まで使えますか？",
  "市区町村が決めるため自治体で違います。1回の出産あたりで上限を設けるのが基本で、"
  "宿泊型・日帰り型・訪問型それぞれに枠を持つ自治体と、3類型をまとめて数える自治体があります。"
  "本記事では東京23区と政令指定都市の計%s自治体について、各自治体が公表している文言を"
  "そのまま一覧にしています。同じ「7回まで」でも、類型ごとに7回なのか3類型あわせて7回なのかで"
  "実際に受けられる量は3倍違うため、数字だけの比較はできません。" % N),
 ("「合算枠」とはどういう意味ですか？",
  "宿泊型・日帰り型・訪問型を別々に数えず、まとめて上限を設ける方式のことです。"
  "たとえば3類型あわせて7回までとされている場合、宿泊型を7日使うと日帰り型も訪問型も使えません。"
  "一方で類型ごとに枠を持つ自治体では、宿泊型7日・日帰り型7回・訪問型5回のように積み上げられます。"
  "本記事の表では、上限の公表文に合算を示す語が含まれるかどうかだけを機械的に示しています。"
  "制度の解釈は加えていないので、実際の数え方は自治体にご確認ください。"),
 ("1泊2日は何日ぶんとして数えられますか？",
  "自治体で違います。泊数に1を足して日数で数える自治体では1泊2日が2日ぶんになり、"
  "1回を24時間として数える自治体では1泊2日で1回です。名古屋市は前者、京都市は後者でした。"
  "同じ上限日数でも、実際に泊まれる回数が倍変わります。"),
 ("多胎児の場合は回数が増えますか？",
  "上乗せする自治体があります。公表文に多胎児の加算が明記されている場合は本記事の表にも"
  "含めています。加算の有無と幅は自治体ごとに異なるため、該当する場合は個別に確認してください。"),
 ("キャンセルすると回数が減りますか？",
  "減る場合があります。当日キャンセルや前日の一定時刻以降のキャンセルを利用したものとして"
  "枠から差し引く自治体があります。もともと回数に余裕のない設計なので、"
  "申込みの前にキャンセル規定を確認しておくと安全です。"),
 ("回数の上限を超えて使いたい場合はどうなりますか？",
  "事業の枠外になり、施設が定める自費の料金がかかります。自治体によっては一時預かりなど"
  "別の制度を案内している場合があります。自己負担がいくらになるかは施設によって大きく違うため、"
  "枠を使い切る前に確認しておくことをおすすめします。"),
]


# ---------------------------------------------------------------- 記事2: 助成
def article_josei():
    rows = "".join(
        '<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>'
        % (c["name"], c["genmen"],
           SHOTOKU_TOWANAI.get(c["key"], "—"))
        for c in real)
    body = """
<blockquote><strong>産後ケアの助成は「非課税世帯なら0円」とは限りません。</strong>%s自治体を確認したところ、減免の設計は大きく3通りに分かれました。非課税世帯・生活保護世帯を0円にする全額免除型、半額や定額まで下げる減額型、そして自治体の負担額を上げるだけで施設の料金次第では自己負担が残る方式です。さらに、所得を問わず全員が使える減額枠を持つ自治体もあります。</blockquote>

<h2 id="kata">減免の3つの型</h2>
<h3>全額免除型</h3>
<p>住民税非課税世帯・生活保護世帯の自己負担を0円にする方式です。公表文に「免除」「無料」「0円」と明記している自治体がこれにあたります。</p>
<h3>減額型</h3>
<p>半額にする、あるいは定額まで下げる方式です。0円にはなりません。北九州市は減免世帯でも宿泊型1,000円などの負担が残ります。「減免あり」という一言で全額免除と同じに扱うと、実際の負担を取り違えます。</p>
<h3>自治体負担を上げる方式</h3>
<p>利用者負担額を直接下げるのではなく、自治体が施設に払う負担額を増やす方式です。岡山市がこの型で、施設の料金設定によっては減免世帯でも自己負担が残ります。</p>

<h2 id="towanai">所得を問わない減額枠を持つ自治体</h2>
<p>非課税世帯向けの減免とは別に、所得にかかわらず全員が使える減額枠を設けている自治体があります。申請が要らず自動で配付されることが多く、見落とすと実際より高く見積もることになります。</p>
<ul>
%s
</ul>

<h2 id="muryou">自己負担が無料になるのはどの自治体か</h2>
<p>「産後ケア 無料」で調べる方が多いので、無料または0円と明記している自治体を先に示します。ただし無料には2つの型があり、どちらかで意味が変わります。</p>
<h3>もともと利用者負担を設定していない自治体</h3>
<p>葛飾区は宿泊型・通所型・訪問型の3類型とも基本利用料が0円です。宿泊型については差額ベッド代も1日10,000円まで区が補助します。品川区は訪問型が利用者負担なし（0円）、日帰り型も荏原保健センターの産後ケア室は0円です。</p>
<h3>非課税世帯・生活保護世帯だけが0円になる自治体</h3>
<p>多くの自治体はこちらで、課税世帯には自己負担が発生します。下の一覧の「減免の内容」列で、免除・無料・0円と明記されているかを確認してください。<strong>「減免あり」と書かれていても0円にならない自治体があります</strong>（北九州市は減免世帯でも宿泊型1,000円などが残り、岡山市は市の負担額が上がるだけで施設の料金次第では自己負担が残ります）。</p>
<p>なお無料とされていても、食事代・差額ベッド代・オプションのケア代は別にかかることがあります。自治体が補助しているのは基本の利用料までという設計が多いためです。</p>

<h2 id="ichiran">%s自治体の減免一覧（公表文のまま）</h2>
<p>解釈を加えず、各自治体が公表している文言をそのまま載せています。適用に別途申請が必要かどうかも自治体で違うため、申込み先で確認してください。</p>
<div class="table-scroll">
<table class="cmp">
<thead><tr><th>自治体</th><th>減免の内容（公表文）</th><th>所得を問わない減額枠</th></tr></thead>
<tbody>%s</tbody>
</table>
</div>

<h2 id="chui">助成を調べるときに間違えやすいところ</h2>
<h3>減免は自動で適用されるとは限らない</h3>
<p>利用登録の申請とは別に、減免だけの申請や証明書の提出が必要な自治体があります。一方で、課税情報の照会に同意すれば書類が不要になる自治体もあります。申込みの時点で確認しておかないと、通常料金で請求されることがあります。</p>
<h3>「助成」と「利用者負担」は別の数字</h3>
<p>自治体のページには、利用者が払う額ではなく自治体が施設に払う負担額しか書かれていないことがあります。この数字を助成額と読むと、自己負担がいくらになるのかは分かりません。利用者負担が明記されているかどうかを先に確かめてください。</p>
<h3>無料でも実費がかかることがある</h3>
<p>利用料が0円でも、食事代・差額ベッド代・オプションのケア代などが別にかかることがあります。自治体が補助しているのは基本の利用料までという設計が多いためです。</p>

<h2 id="calc">自分の場合の自己負担を計算する</h2>
<p>減免前の自己負担がいくらになるかは、<a href="/tools/sangokea-ryokin/">産後ケアの料金を自治体別に調べるツール</a>で確かめられます。世帯の区分を選ぶと、その自治体が公表している減免の内容も表示されます。</p>

<h2 id="faq">よくある質問（FAQ）</h2>
%s

%s

<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/tools/sangokea-ryokin/">産後ケアの料金はいくら？自治体別の自己負担</a></li>
<li><a href="/articles/sangokea-nankai/">産後ケアは何回使える？%s自治体の上限一覧</a></li>
<li><a href="/articles/daredemo-tsuen-ryokin/">こども誰でも通園制度の料金はいくら？46自治体の実額と減免</a></li>
<li><a href="/articles/futarime-sango/">2人目の産後は何が変わるか</a></li>
<li><a href="/articles/sango-kaji-buntan/">産後の家事分担はどう決めるか</a></li>
<li><a href="/tools/ikukyu-encho-hantei/">育休はいつまで延長できる？条件と必要書類の判定</a></li>
</ul>
""" % (N,
       "\n".join("<li><strong>%s</strong>｜%s</li>" % (c["name"], SHOTOKU_TOWANAI[c["key"]])
                 for c in towanai),
       N, rows, faq_html(FAQ_JOSEI), src_table(), N)

    write("sangokea-josei",
          "産後ケアの助成・減免はいくら？東京23区＋政令市%s自治体の一覧【2026年度】" % N,
          "産後ケアの助成はいくら？｜非課税世帯の減免と、所得を問わない減額枠",
          "産後ケアの助成は「非課税世帯なら0円」とは限りません。%s自治体を確認したところ、"
          "減免は全額免除型・減額型・自治体負担を上げる方式の3通りに分かれ、減免世帯でも自己負担が"
          "残る自治体がありました。さらに所得を問わず全員が使える減額枠を持つ自治体もあります。"
          "各自治体の公表文のまま一覧にし、申請の要否と実費の扱いまで整理しました。確認日は%s。" % (N, CHECKED),
          "産後ケアの減免は3通りに分かれ、非課税でも0円にならない自治体があります。%s自治体の公表文を一覧に。" % N,
          FAQ_JOSEI, body)


FAQ_JOSEI = [
 ("産後ケアの助成で自己負担は0円になりますか？",
  "自治体によります。%s自治体を確認したところ、減免の設計は3通りに分かれました。"
  "非課税世帯・生活保護世帯を0円にする全額免除型、半額や定額まで下げる減額型、"
  "自治体が施設に払う負担額を上げるだけの方式です。北九州市は減免世帯でも宿泊型1,000円などの"
  "負担が残り、岡山市は施設の料金次第で自己負担が残ります。「減免あり」で横に並べると"
  "実態を取り違えます。" % N),
 ("課税世帯でも使える助成はありますか？",
  "あります。非課税世帯向けの減免とは別に、所得を問わず全員が使える減額枠を設けている"
  "自治体があります。千代田区・文京区・台東区・さいたま市・川崎市・堺市で確認できました。"
  "回数を限って自己負担を一定額引く形が多く、申請が要らず自動で配付されることもあります。"
  "見落とすと実際より高く見積もることになります。"),
 ("助成を受けるのに申請は必要ですか？",
  "利用登録の申請とは別に、減免だけの申請や非課税証明書の提出が必要な自治体があります。"
  "一方で、課税情報の照会に同意すれば書類が不要になる自治体もあります。"
  "申込みの時点で確認しておかないと通常料金で請求されることがあるため、"
  "申込み先に「減免の適用に何が必要か」を必ず聞いてください。"),
 ("自治体のページに書いてある金額が助成額かどうか分かりません",
  "自治体のページには、利用者が払う額ではなく自治体が施設に払う負担額しか書かれていないことが"
  "あります。この数字を助成額として読むと、自分がいくら払うのかは分かりません。"
  "利用者負担が明記されているかどうかを先に確かめ、書かれていない場合は"
  "施設の料金一覧と突き合わせる必要があります。"),
 ("助成で無料になれば、お金は一切かかりませんか？",
  "かからないとは限りません。無料とされているのは制度の利用料であって、食事代・差額ベッド代・"
  "オプションのケア代などが別にかかることがあります。自治体が補助しているのは基本の利用料までと"
  "いう設計が多いためです。"),
]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    article_nankai()
    article_josei()
    print("合算の記載あり: %d / %d 自治体" % (len(gassan), N))
    print("免除・0円と明記: %d 自治体" % len(menjo))
    print("所得を問わない減額枠: %s" % "・".join(c["name"] for c in towanai))
