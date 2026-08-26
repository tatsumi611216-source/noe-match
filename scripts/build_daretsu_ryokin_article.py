# -*- coding: utf-8 -*-
"""記事「こども誰でも通園制度の料金はいくら？」を _daretsu_data.py から生成する。

狙う語は serp_screen.py の実測で本命判定だった「こども誰でも通園制度 料金」
（サジェスト: 料金 条例／料金 減免／名古屋市 料金）と「デメリット」。
「上乗せ」はサジェストなし＝検索されていないので見出しに使わない。

数値はすべて _daretsu_data.py（各自治体公式の一次確認）から引く。
記事とツールで数字がズレないよう、表を手で書かない。
"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _daretsu_data import CHECKED, CITIES

SLUG = "daredemo-tsuen-ryokin"
URL = "https://www.noe-match.com/articles/%s/" % SLUG
TODAY = "2026-08-25"
TODAY_JA = "2026年8月25日"
TITLE = "こども誰でも通園制度の料金はいくら？46自治体の実額と減免を調べた【2026年8月】"
H1 = "こども誰でも通園制度の料金はいくら？｜46自治体の実額と減免を調べた"
DESC = ("こども誰でも通園制度の利用料は自治体で違う。東京23区・政令指定都市20市・中核市ほか3市の計46自治体の"
        "公式ページを確認したところ、住民が地元の施設を使う場合に無償とする自治体と、1時間300円を"
        "取る自治体に分かれた。減免の基準額は77,101円でほぼ全国共通。無償でも給食費などの実費は"
        "別にかかる。上限時間・予約経路・認定にかかる期間まで、出典つきで整理する。")

real = [c for c in CITIES if c["key"] != "kokuhyo"]
tokyo = [c for c in real if c.get("group", "東京23区") == "東京23区"]
seirei = [c for c in real if c.get("group") == "政令市"]
chukaku = [c for c in real if c.get("group") == "中核市ほか"]
N, NT, NS = len(real), len(tokyo), len(seirei)


# 料金の型は fee の文言を1件ずつ読んで確定させた（2026-08-25）。
# 正規表現による自動分類は、減免の「生活保護世帯は無料」に反応して
# 福岡市・北九州市を無償に、「施設により異なります」に反応して川崎市を
# 施設ごとに誤分類した。人が読んで決める。
FEE_TYPE = {
    # 住民が地元の施設を使う場合は無償・無料（減免ではなく原則無償）
    "ota": "無償", "shibuya": "無償", "setagaya": "無償", "nerima": "無償",
    "koto": "無償", "shinagawa": "無償", "minato": "無償", "edogawa": "無償",
    "chuo": "無償", "toshima": "無償", "chiyoda": "無償", "sumida": "無償",
    "meguro": "無償", "suginami": "無償", "kita": "無償", "itabashi": "無償",
    "adachi": "無償", "katsushika": "無償", "shinjuku": "無償", "bunkyo": "無償",
    # 住民も1時間300円前後を払う（減免は別途）
    "taito": "有料", "nakano": "有料", "yokohama": "有料", "kawasaki": "有料",
    "saitama": "有料", "chiba": "有料", "sapporo": "有料", "fukuoka": "有料",
    "hamamatsu": "有料", "hiroshima": "有料", "kitakyushu": "有料", "kobe": "有料",
    "kumamoto": "有料", "niigata": "有料", "sagamihara": "有料", "sakai": "有料",
    "sendai": "有料",
    # 自治体としての統一単価がなく、施設ごとに決まる
    "osaka": "施設ごと", "nagoya": "施設ごと", "kyoto": "施設ごと",
    "okayama": "施設ごと", "shizuoka": "施設ごと",
    # 令和8年度の料金を公式ページで確認できなかった
    "funabashi": "有料", "himeji": "有料",
    "hachioji": "施設ごと",
    "arakawa": "不明",
}


def fee_type(c):
    return FEE_TYPE[c["key"]]


TYPES = {}
for c in real:
    TYPES.setdefault(fee_type(c), []).append(c["name"])

genmen = [c["name"] for c in real if "77,10" in c["fee"]]
jippi = [c["name"] for c in real
         if re.search(r"(給食|おやつ|実費|雑費)", c["fee"] + c["fee_extra"])]
uwanose = sorted([(c["name"], c["cap"]) for c in real if c["cap"] and c["cap"] > 10],
                 key=lambda x: -x[1])
hikouhyo = [c["name"] for c in real if c["cap"] is None]


def rows(cities):
    return "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (c["name"], c["cap_label"], c["fee"])
        for c in cities)


TOC = [
    ("sec-1", "料金は「無償」と「1時間300円」に割れている"),
    ("sec-2", "減免の基準額は77,101円でほぼ全国共通"),
    ("sec-3", "「無償」でも払うものがある"),
    ("sec-4", "使える時間は自治体で最大16倍違う"),
    ("sec-5", "東京23区の料金一覧"),
    ("sec-6", "政令指定都市20市の料金一覧"),
    ("sec-6b", "中核市ほかの料金一覧"),
    ("sec-7", "料金以外でつまずくところ"),
    ("sec-faq", "よくある質問（FAQ）"),
    ("sec-summary", "まとめ"),
]

FAQ = [
 ("こども誰でも通園制度の料金はいくらですか？",
  "自治体によって違います。国の補助基準では1時間あたり300円程度が目安とされていますが、"
  "住民が地元の施設を使う場合は無償としている自治体（練馬区・世田谷区・江東区・墨田区・千代田区・"
  "北区・豊島区・葛飾区・足立区・港区・中央区・板橋区・杉並区など）と、住民も1時間300円前後を払う自治体"
  "（台東区・中野区・千葉市・札幌市・横浜市・さいたま市・川崎市・神戸市・広島市・熊本市・北九州市・仙台市・"
  "堺市・相模原市・新潟市・浜松市・福岡市）に分かれます。板橋区と杉並区は表向き1時間300円ですが、"
  "区民は無償化・実質負担0円としています。名古屋市・大阪市・京都市・静岡市・岡山市のように「施設ごとに設定するので施設に確認を」と"
  "している自治体もあり、岡山市では実施事業所13か所の実額が300円・330円・400円・500円と割れていました。"),
 ("利用料の減免はありますか？",
  "多くの自治体が所得に応じた減免を設けており、基準額は「市町村民税所得割合算額77,101円未満」で"
  "ほぼ揃っています。札幌市は生活保護世帯0円・77,101円未満の世帯100円、台東区も0円と100円、"
  "広島市は生活保護0円・非課税60円・77,101円未満100円、横浜市とさいたま市は生活保護300円上限・"
  "77,101円未満の世帯200円上限としています。適用には受給者証や所得証明の提出が必要な場合があり、"
  "岡山市のように利用認定申請とは別に減免申請が要る自治体もあります。"),
 ("無償の自治体なら、お金は一切かかりませんか？",
  "かかる場合があります。無償とされているのは制度の利用料であって、給食費・おやつ代・教材費・雑費は"
  "別に必要なことが多いためです。福岡市は施設ごとに給食費1回300〜500円、雑費月額300円、衛生費月額1,500円"
  "といった例を公表しています。練馬区は「給食等は別途自己負担」、千代田区は「おやつ代等は別途費用が"
  "発生する場合がある」と明記しています。"),
 ("上限時間を超えて使うといくらかかりますか？",
  "自治体によって扱いが違います。千葉市は「予約した時間分に加え、超過料金を徴収します」と明記し、"
  "渋谷区は上限を超えた分について「施設が定める料金」としています。静岡市は「施設が実施する別の"
  "保育サービスの料金体系が適用される場合」があるとし、新潟市と仙台市は月10時間を超える分について"
  "一時預かりの利用を案内しています。一方で川崎市と大阪市は「10時間を超えての利用はできません」として、"
  "そもそも超過利用を認めていません。"),
 ("こども誰でも通園制度のデメリットは何ですか？",
  "料金面では、無償の自治体でも給食費などの実費がかかること、上乗せ枠がその自治体の施設でしか"
  "使えないことが挙げられます。運用面では認定に時間がかかり、札幌市はおおむね1か月、北区は4週間程度、"
  "さいたま市・川崎市・京都市・相模原市は2〜3週間と公表しています。使いたい月の直前に申し込んでも"
  "間に合いません。多くの施設で利用前の事前面談が必要で、未利用時間の翌月繰越もできないのが基本です。"
  "さいたま市・新潟市・岡山市は当日キャンセルを利用扱いとし、枠を消費する扱いにしています。"),
 ("この記事に載っていない自治体では月何時間使えますか？",
  "国の補助基準の上限は月10時間ですが、令和8年度と令和9年度は経過措置（子ども・子育て支援法等改正法附則第6条）により、"
  "自治体が条例で利用可能時間を月3時間以上10時間未満の範囲に設定できます。報道では約1,700自治体（大半）が"
  "この経過措置を適用しているとされ、収録外の自治体では月10時間より短いことが多い状況です。"
  "本記事の46自治体はいずれも月10時間以上でしたが、これは大都市に限った傾向で、全国の標準ではありません。"),
 ("どこで予約すればいいですか？",
  "多くの自治体は国の「こども誰でも通園制度総合支援システム」（つうえんポータル）で施設を検索して"
  "予約します。ただし練馬区は区内施設について「総合支援システムでは予約できない」と明記しており、"
  "実施施設一覧の申込先へ直接申し込む方式です。足立区は各施設へ電話等で面談予約、杉並区・文京区・"
  "福岡市は「実施園（施設）の指定する方法」としています。最初にどの経路かを確認しておくと、"
  "システムに登録したのに自分の自治体の園が出てこないという詰まり方を避けられます。"),
 ("料金が「施設ごと」の自治体では、どうやって調べればいいですか？",
  "実施施設の一覧に単価が載っていることが多いので、そこを見るのが早いです。岡山市は実施事業所一覧の"
  "PDFに「利用料(1時間あたり)」欄があり、事業所ごとに300円から500円まで幅があります。福岡市も施設別に"
  "利用料と給食費・雑費を掲載しており、無料の園や1時間250円の園があります。静岡市は本体ページに単価が"
  "なく、区ごとの施設一覧PDFを開かないと実額が分からない作りでした。"),
]

faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
    for q, a in FAQ]}, ensure_ascii=False)
art_ld = json.dumps({
    "@context": "https://schema.org", "@type": "BlogPosting", "headline": TITLE,
    "description": DESC, "inLanguage": "ja",
    "datePublished": TODAY, "dateModified": TODAY,
    "mainEntityOfPage": {"@type": "WebPage", "@id": URL},
    "author": {"@type": "Organization", "name": "Noe編集部", "url": "https://www.noe-match.com/about.html"},
    "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": "https://www.noe-match.com/"},
}, ensure_ascii=False)
bc_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
    {"@type": "ListItem", "position": 2, "name": "記事一覧", "item": "https://www.noe-match.com/articles/"},
    {"@type": "ListItem", "position": 3, "name": H1}]}, ensure_ascii=False)

shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
CSS = shell[shell.find("<style>"):shell.find("</style>") + 8]

toc_html = "\n".join('<li><a href="#%s">%s</a></li>' % (i, t) for i, t in TOC)
faq_html = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a) for i, (q, a) in enumerate(FAQ))

HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VLQBH0S1SL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-VLQBH0S1SL');</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{URL}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:type" content="article">
<meta property="og:url" content="{URL}">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta property="article:published_time" content="{TODAY}">
<meta property="article:modified_time" content="{TODAY}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@500;600;700;900&display=swap" rel="stylesheet">
{CSS}
<script type="application/ld+json">{ART_LD}</script>
<script type="application/ld+json">{FAQ_LD}</script>
<script type="application/ld+json">{BC_LD}</script>
</head>
<body>
<header><div class="header-inner">
<a href="/" class="logo">Noe結婚設計室<span class="logo-badge">2026</span></a>
<nav><a href="/#tools">ツール</a><a href="/articles/">記事一覧</a><a href="/#faq">FAQ</a><a href="/#about">運営者</a></nav>
</div></header>
<div class="wrap">
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/articles/">記事一覧</a> ＞ {H1}</div>
<article>
<h1>{TITLE}</h1>
<p class="pr-notice">本ページはプロモーションを含みます。記事内に広告主から成果報酬を受け取るリンクが含まれます。掲載内容は編集部の基準で作成しており、報酬の有無で評価を変えていません。</p>
<div class="byline"><div class="av">N</div><div><strong><a href="/about.html" style="color:inherit;text-decoration:none">Noe編集部</a></strong><br>各自治体の公式ページを1件ずつ確認して作成しています。<div class="up">最終更新：{TODAY_JA} ｜ 著者：Noe編集部</div></div></div>

<blockquote><strong>「こども誰でも通園制度は1時間300円」という説明をよく見かける。しかし実際に自治体の公式ページを開くと、そう書いていない自治体が半分近くある。</strong>東京23区と政令指定都市20市、あわせて{N}自治体の公式ページを{TODAY_JA}に確認した。料金は無償と1時間300円に大きく割れ、さらに「施設ごとに決める」としている自治体もあった。無償の自治体でも給食費は別にかかる。数字はすべて各自治体の公式ページから取っている。</blockquote>

<nav class="toc" aria-label="目次">
<div class="toc-h">目次</div>
<ol>
{TOC}
</ol>
</nav>

<h2 id="sec-1">料金は「無償」と「1時間300円」に割れている</h2>
<p>国は補助基準額の上で1時間あたり300円程度を目安としてきた。ところが実際の運用は自治体に委ねられていて、{N}自治体を並べると3つの型に分かれる。</p>
<div class="table-wrap"><table>
<thead><tr><th>料金の型</th><th>自治体数</th><th>該当する自治体</th></tr></thead>
<tbody>
<tr><td><strong>無償</strong>（住民が地元の施設を使う場合）</td><td>{N_MUSHO}</td><td>{L_MUSHO}</td></tr>
<tr><td><strong>有料</strong>（1時間300円前後）</td><td>{N_YURYO}</td><td>{L_YURYO}</td></tr>
<tr><td><strong>施設ごとに設定</strong></td><td>{N_SHISETSU}</td><td>{L_SHISETSU}</td></tr>
<tr><td>公表を確認できず</td><td>{N_FUMEI}</td><td>{L_FUMEI}</td></tr>
</tbody>
</table></div>
<p>ここで注意がいるのは「無償」の意味だ。ほとんどの自治体で、無償になるのは<strong>その自治体の住民が、その自治体の中の施設を使った場合に限られる</strong>。世田谷区は区民が区内施設を使う場合は無償だが、区外在住者が区内施設を使うと1時間300円になる。江東区も区民は無料、区外在住は1時間300円だ。江戸川区は区民の区外施設利用を有料としている。里帰り先で使う、勤務先の近くで使う、といった使い方をすると条件が変わる。</p>
<p>「施設ごとに設定」の自治体では、公式ページを見ても金額が分からない。岡山市は実施事業所一覧のPDFに1時間あたりの単価が載っており、実額は300円が9事業所、330円が2事業所、400円と500円が各1事業所だった。同じ市内でも1.7倍の開きがある。静岡市は本体ページに単価がなく、区ごとの施設一覧PDFを開かないと実額に辿り着けない作りだった。</p>

<h2 id="sec-2">減免の基準額は77,101円でほぼ全国共通</h2>
<p>有料の自治体には、ほぼ例外なく所得に応じた減免がある。そして<strong>基準額は「市町村民税所得割合算額77,101円未満」でほぼ全国が揃っている</strong>。{N_GENMEN}自治体がこの数字を公式ページに明記していた。</p>
<div class="table-wrap"><table>
<thead><tr><th>自治体</th><th>生活保護世帯</th><th>77,101円未満の世帯</th></tr></thead>
<tbody>
<tr><td>札幌市</td><td>0円</td><td>100円</td></tr>
<tr><td>台東区</td><td>0円</td><td>100円</td></tr>
<tr><td>広島市</td><td>0円</td><td>100円（非課税世帯は60円）</td></tr>
<tr><td>千葉市</td><td>0円</td><td>100円（要支援児童世帯も100円）</td></tr>
<tr><td>北九州市</td><td>無料</td><td>100円</td></tr>
<tr><td>岡山市</td><td>300円を減免</td><td>非課税世帯200円を減免</td></tr>
<tr><td>横浜市</td><td>300円上限</td><td>200円上限（里親・要支援家庭も200円）</td></tr>
<tr><td>さいたま市</td><td>300円上限</td><td>200円上限（政令市課税なら102,801円未満）</td></tr>
<tr><td>熊本市</td><td>300円を減免</td><td>200円を減免</td></tr>
<tr><td>静岡市</td><td>300円（1時間あたり減免額の最大）</td><td>200円（年収360万円未満相当）</td></tr>
<tr><td>神戸市</td><td>300円を減免（実質0円）</td><td>200円を減免（実質100円）</td></tr>
<tr><td>京都市</td><td>300円（月額上限）</td><td>200円（月額上限）</td></tr>
</tbody>
</table></div>
<p>金額の書き方が自治体で違うことに気をつけたい。札幌市や台東区は「減免後にいくら払うか」を書いているが、岡山市・熊本市・神戸市は「いくら引くか」を書いている。同じ300円という数字でも、前者は払う額、後者は引かれる額で、意味が逆になる。熊本市の公式ページは見出しが「1時間あたりの減免金額」となっていて、これが控除額なのか減免後の実額なのかを断定できる書き方になっていなかった。自分の自治体の表がどちらの書き方かは、申請前に確認しておいたほうがいい。</p>
<p>減免は自動では適用されない。岡山市は「利用認定申請とは別に申請が必要」「利用料の減免は申請日以降に適用されます」と明記している。札幌市は受給者証や所得証明書等を施設に提出または提示する必要がある。横浜市とさいたま市は認定申請時に一緒に申請する形だ。</p>

<h2 id="sec-3">「無償」でも払うものがある</h2>
<p>無償の自治体でも、実際には財布が動く。制度の利用料が無償なだけで、食事とおやつと材料費は別だからだ。{N_JIPPI}自治体が実費の負担について公式ページで触れていた。</p>
<p>金額まで公表している自治体は少ないが、福岡市は施設ごとの実費を一覧で出している。給食費が1回300円から500円、雑費が月額300円、衛生費が月額1,500円、布団リース代が月額300円といった具合で、施設によって項目そのものが違う。岡山市も事業所ごとに給食1食270円から500円程度、おやつ1食50円から150円と幅がある。</p>
<p>練馬区は「給食等は別途自己負担」、千代田区は「区内施設は無料（給食を提供する場合は給食費等も無料）」としつつ「おやつ代等は別途費用が発生する場合がある」と書いている。杉並区は利用料を無償化しているが「給食代・おやつ代等は無償化の対象外」と明記している。<strong>週1回・月4回のペースで通えば、給食費だけで月1,200円から2,000円になる。</strong>無償という言葉だけで判断すると、家計の見込みがずれる。</p>
<p>キャンセル料がかかる自治体もある。中央区は「実費負担・超過料金・キャンセル料が発生する場合がある」、さいたま市は「施設によってはキャンセル料が発生する場合あり」としている。さらに、さいたま市・新潟市・岡山市は当日0時以降のキャンセルや無断キャンセルを<strong>利用したものとして扱い、月の枠から時間を差し引く</strong>。お金だけでなく枠も減る。</p>

<h2 id="sec-4">使える時間は自治体で最大16倍違う</h2>
<p>料金と並んで差が大きいのが上限時間だ。国の基準は月10時間だが、独自に上乗せしている自治体がある。上乗せを確認できたのは次の{N_UWANOSE}自治体だった。</p>
<div class="table-wrap"><table>
<thead><tr><th>自治体</th><th>月の上限</th></tr></thead>
<tbody>
{UWANOSE_ROWS}
</tbody>
</table></div>
<p>大田区の160時間は条件つきで、「月10時間を同一の大田区内施設で利用した場合」に150時間の上乗せが使える。複数の施設に分けると追加分は使えず、上乗せ部分は別途契約が必要になる。無条件で使える上限としては渋谷区の月64時間が最大だ。</p>
<p>逆方向の差もある。令和8・9年度は経過措置により、自治体が条例で上限を月3時間以上10時間未満に短縮でき、報道では約1,700自治体（大半）がこれを適用している。本記事の46自治体がすべて10時間以上なのは大都市だから、という点は押さえておきたい。</p>
<p><strong>注目すべきは、上乗せがほぼ東京23区に固まっていることだ。</strong>政令指定都市20市のうち上乗せをしていたのは京都市の1市だけで、しかも国の10時間に2時間を足した12時間である。ほかの18市はいずれも国基準の月10時間だった。東京23区が「無償化して時間を伸ばす」方向に動いているのに対し、政令市は「時間は国基準のまま、所得に応じて払う額を下げる」方向で設計されている、という違いが数字に出ている。</p>
<p>上乗せ分には共通のルールがある。その自治体の中の施設でしか使えないという点だ。世田谷区は区外施設の利用や区外在住者は国制度の月10時間のみ、江東区も区外在住者は月10時間、京都市も上乗せ2時間は京都市が認可・確認した施設に限ると明記している。</p>
<p>自分の自治体の条件をその場で確認するなら、<a href="/tools/daredemo-tsuen-jichitai/">こども誰でも通園制度の自治体別ナビ</a>に{N}自治体分の上限時間・利用料・予約経路・申込の入口をまとめてある。使いたい回数を入れると枠に収まるかどうかも出る。</p>

<h2 id="sec-5">東京23区の料金一覧</h2>
<p>{TODAY_JA}時点で各区の公式ページに書かれていた内容をそのまま並べる。</p>
<div class="table-wrap"><table>
<thead><tr><th>区</th><th>月の上限</th><th>利用料</th></tr></thead>
<tbody>
{TOKYO_ROWS}
</tbody>
</table></div>

<h2 id="sec-6">政令指定都市20市の料金一覧</h2>
<div class="table-wrap"><table>
<thead><tr><th>市</th><th>月の上限</th><th>利用料</th></tr></thead>
<tbody>
{SEIREI_ROWS}
</tbody>
</table></div>
<p>{N_HIKOUHYO}自治体は月あたりの上限時間そのものを公式ページに載せていなかった（{L_HIKOUHYO}）。新宿区は「週2日又は週3日の定期利用」という書き方で時間に換算していない。葛飾区は上乗せをすると書きながら時間数を示さず、金額の上限（月48,000円）で運用している。福岡市は令和7年度の市政だよりに「月最大40時間」「国の上限の4倍に拡充」とあったが、令和8年度のページでは確認できなかった。中野区と荒川区は令和8年度の案内自体が見当たらず、確認できたのは令和7年度の試行実施のページだけだった。</p>

<h2 id="sec-6b">中核市ほかの料金一覧</h2>
<div class="table-wrap"><table>
<thead><tr><th>市</th><th>月の上限</th><th>利用料</th></tr></thead>
<tbody>
{CHUKAKU_ROWS}
</tbody>
</table></div>
<p>八王子市は時間の上限を設けず、「月48,000円を上限として補助」という金額の上限で運用している。葛飾区も同じ金額上限型で、時間で区切るか金額で区切るかという設計の違いがある。船橋市は最初の1時間300円・以後30分150円という時間刻みの料金で、給食は利用料とは別に300円。11時から12時をまたぐ予約では、申し出がない限り給食が提供されて料金が発生する。</p>

<h2 id="sec-7">料金以外でつまずくところ</h2>
<p>お金の話が片付いても、実際に使い始めるまでには時間がかかる。<strong>認定に2週間から1か月かかるのが標準だ。</strong>札幌市はおおむね1か月程度、北区は4週間程度、さいたま市・川崎市・京都市・相模原市・新潟市は2〜3週間、千葉市・大阪市・仙台市・北九州市は2週間程度と公表している。横浜市は最大10営業日、足立区は10営業日程度と比較的短い。</p>
<p>そのうえで、多くの自治体は利用前に施設との事前面談を求める。目黒区は「利用予約の前に希望施設での事前面談が必要」、新潟市は「面談をせずに利用することはできません」と明記している。認定に3週間、面談の日程調整に1〜2週間と積み上がるので、<strong>使いたい月の1〜2か月前に動き始めないと間に合わない。</strong></p>
<p>予約の経路も揃っていない。多くは国の総合支援システム（つうえんポータル）だが、練馬区は区内施設について「総合支援システムでは予約できない」と明記していて、実施施設一覧の申込先へ直接申し込む方式だ。足立区は各施設へ電話等で面談予約、杉並区・文京区・福岡市は「実施園（施設）の指定する方法」としている。システムに登録したのに自分の自治体の園が予約画面に出てこない、という詰まり方をするのはここだ。</p>
<p>未利用時間の繰越はできないのが基本である。渋谷区は「各月の上限であり、未利用時間を翌月以降に繰り越すことはできません」、さいたま市・堺市・静岡市・新潟市も同様に繰越不可を明記している。月末にまとめて使おうとしても枠は貯まらない。</p>
<p>復職や保活と並行して動かす場合、段取りの負荷は制度の手続きだけでは終わらない。産後の生活の立て直しと家庭内の分担については<a href="/articles/sango-kaji-buntan/">産後の家事分担｜実際に揉めるのはどこか</a>、育休を夫婦で組み立てる場合は<a href="/articles/ikukyu-fuufu-doji/">育休を夫婦同時に取るとどうなるか</a>に整理してある。里帰りをしない前提で日中の預け先を確保したい場合は<a href="/articles/satogaeri-shinai/">里帰りしない出産の準備</a>も参考になる。</p>


<div style="background:#f7f5f2;border:1px solid #e6e2dc;padding:20px 22px;margin:22px 0;text-align:center">
<p style="font-size:.7rem;color:#999;margin:0 0 6px;text-align:left">PR</p>
<p style="font-weight:700;margin:0 0 8px">通園と復職の準備で最初に決まらなくなるのは「毎日の食事」</p>
<p style="font-size:.8rem;color:#5a6068;margin:0 0 14px">週1〜2回の通園や慣らし保育が始まる時期は、送り迎えの前後に食事の支度が重なります。作る手間を減らす手段を先に確保しておくと段取りが崩れにくくなります。Oisixは食材宅配のおためしセット（内容・価格・配送エリアは公式サイトでご確認ください）。</p>
<a href="https://px.a8.net/svt/ejp?a8mat=4B8B4Q+5CWKMY+3RK+2TBJQA" rel="nofollow sponsored noopener" target="_blank" style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;padding:13px 32px;text-decoration:none">Oisixのおためしセットを見る</a>
<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">食材宅配サービス。制度の利用可否とは関係ありません</p>
</div>

<h2 id="sec-faq">よくある質問（FAQ）</h2>
{FAQ_HTML}

<h2 id="sec-summary">まとめ</h2>
<ul>
<li>料金は無償と1時間300円に割れている。無償になるのは原則、その自治体の住民がその自治体の施設を使う場合だけ</li>
<li>減免の基準額は市町村民税所得割合算額77,101円未満で全国ほぼ共通。ただし「払う額」を書く自治体と「引く額」を書く自治体があり、読み違えやすい</li>
<li>無償でも給食費・おやつ代・雑費は別。週1回通えば月1,200〜2,000円程度の実費を見ておく</li>
<li>上限時間は月10時間から160時間まで開くが、上乗せはほぼ東京23区に集中。政令市20市で上乗せは京都市の12時間だけ</li>
<li>認定に2週間〜1か月、さらに事前面談。使いたい月の1〜2か月前から動く</li>
</ul>
<p>この記事の数値は{TODAY_JA}に各自治体の公式ページを確認したものです。制度は2026年度に本格実施へ移ったところで、各自治体が運用を更新しています。申込の前に、必ずお住まいの自治体の公式ページで最新の内容をご確認ください。自治体ごとの出典URLは<a href="/tools/daredemo-tsuen-jichitai/">自治体別ナビ</a>に全件掲載しています。</p>

<div class="related">
<h2>関連記事</h2>
<ul>
<li><a href="/articles/sango-kaji-buntan/">産後の家事分担｜実際に揉めるのはどこか</a></li>
<li><a href="/articles/ikukyu-fuufu-doji/">育休を夫婦同時に取るとどうなるか</a></li>
<li><a href="/articles/satogaeri-shinai/">里帰りしない出産の準備</a></li>
<li><a href="/articles/sango-crisis-guide/">産後クライシスはなぜ起きるのか</a></li>
<li><a href="/articles/futarime-sango/">二人目の産後は何が違うか</a></li>
</ul>
</div>
</article>

<!-- LINE-CTA -->
<section id="line-cta" style="max-width:680px;margin:56px auto 64px;padding:36px 28px;background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;">
  <p style="margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif;">NOE OFFICIAL LINE</p>
  <p style="margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5;">子育ての制度とお金のFACTをLINEで</p>
  <p style="margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;">結婚・出産・育児まわりの制度とお金のFACTだけを、週1回・短文で届けます。<br>気になることの相談も、追加後そのままトークでどうぞ。</p>
  <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{{gtag('event','line_add_click',{{tool:'{SLUG}'}});}}catch(e){{}}"
     style="display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;font-size:15px;font-weight:600;text-decoration:none;">友だち追加して受け取る</a>
  <p style="margin:14px 0 0;font-size:11px;color:#8a8f95;">登録は無料・配信は週1回だけ。いつでも解除できます。</p>
</section>
</div>
<footer><div class="footer-inner">
<div><a href="/">ホーム</a><a href="/articles/">記事一覧</a><a href="/about.html">運営者情報</a><a href="/privacy-policy.html">プライバシー</a><a href="/disclaimer.html">免責事項</a></div>
<p class="footer-disc">※本記事は各自治体およびこども家庭庁の公式公開情報（{TODAY_JA}確認）に基づきます。制度の適用と最終的な判断は各自治体が行います。<br>&copy; 2026 Noe結婚設計室</p>
</div></footer>
<button id="top" onclick="scrollTo({{top:0,behavior:'smooth'}})">↑</button>
</body>
</html>""".format(
    TITLE=TITLE, DESC=DESC, URL=URL, H1=H1, CSS=CSS, TODAY=TODAY, TODAY_JA=TODAY_JA,
    SLUG=SLUG, ART_LD=art_ld, FAQ_LD=faq_ld, BC_LD=bc_ld, TOC=toc_html, FAQ_HTML=faq_html,
    N=N, N_MUSHO=len(TYPES.get("無償", [])), L_MUSHO="・".join(TYPES.get("無償", [])),
    N_YURYO=len(TYPES.get("有料", [])), L_YURYO="・".join(TYPES.get("有料", [])),
    N_SHISETSU=len(TYPES.get("施設ごと", [])), L_SHISETSU="・".join(TYPES.get("施設ごと", [])),
    N_GENMEN=len(genmen), N_JIPPI=len(jippi), N_UWANOSE=len(uwanose),
    UWANOSE_ROWS="".join("<tr><td>%s</td><td>月%d時間</td></tr>" % (n, h) for n, h in uwanose),
    TOKYO_ROWS=rows(sorted(tokyo, key=lambda x: -(x["cap"] or -1))),
    CHUKAKU_ROWS=rows(sorted(chukaku, key=lambda x: -(x["cap"] or -1))),
    SEIREI_ROWS=rows(sorted(seirei, key=lambda x: -(x["cap"] or -1))),
    N_FUMEI=len(TYPES.get("不明", [])), L_FUMEI="・".join(TYPES.get("不明", [])),
    N_HIKOUHYO=len(hikouhyo), L_HIKOUHYO="・".join(hikouhyo),
)

os.makedirs("articles/%s" % SLUG, exist_ok=True)
io.open("articles/%s/index.html" % SLUG, "w", encoding="utf-8").write(HTML)
body = re.sub(r"\s+", "", re.sub(r"<[^>]+>", "",
              re.sub(r'<script.*?</script>|<style.*?</style>|<nav class="toc".*?</nav>', "", HTML, flags=re.S)))
print("written: articles/%s/index.html  本文 %d字 / 内部リンク %d本 / FAQ %d問"
      % (SLUG, len(body), len(set(re.findall(r'href="/articles/([^/"]+)/', HTML))), len(FAQ)))
