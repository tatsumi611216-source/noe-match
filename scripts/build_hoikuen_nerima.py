# -*- coding: utf-8 -*-
"""練馬区 保育園入園指数計算＋令和8年4月ボーダー逆引きツール生成
データ出典: scratchpad/nerima/{kijun,border}.json（区公式PDFから2026-08-23抽出）"""
import io, os, json, re, sys

NER = r"C:\Users\tatsu\AppData\Local\Temp\claude\C--Users-tatsu\5e64a0b5-6a00-4092-aed9-5e78d8c541fc\scratchpad\nerima"
kij = json.load(io.open(os.path.join(NER, "kijun.json"), encoding="utf-8"))
bor = json.load(io.open(os.path.join(NER, "border.json"), encoding="utf-8"))

# ---- ボーダーを地区→[name, [10列]] に圧縮（＊/*を統一） ----
COLS = bor["meta"]["columns"]
districts = {}
for p in bor["parks"]:
    row = []
    for c in COLS:
        v = p["ages"].get(c, "")
        if isinstance(v, str):
            v = v.replace("*", "＊").replace("４", "4").replace("１", "1").replace("２", "2").replace("３", "3").replace("５", "5").replace("６", "6").replace("７", "7").replace("８", "8").replace("９", "9").replace("０", "0")
        row.append(v)
    districts.setdefault(p["district"], []).append([p["name"], row])
BORDER_JS = json.dumps(districts, ensure_ascii=False, separators=(",", ":"))

SLUG = "hoikuen-tensu-nerima"
TITLE = "練馬区の保育園 点数計算＆内定ボーダー逆引き｜あなたの指数で入れた園が分かる【令和8年4月実績】"
DESC = "練馬区の保育園入園の指数（点数）を、区公式の保育実施基準表（令和8年度版）に基づいて計算。さらに令和8年4月1次利用調整の園別最低指数（区公式公開）と照合し、あなたの点数で内定が出ていた園を地区×年齢クラスで逆引き表示します。無料・登録不要。"
URL = "https://www.noe-match.com/tools/%s/" % SLUG

# ---- 既存ツールからCSSを流用 ----
shell = io.open("tools/seikatsuhi-simulator/index.html", encoding="utf-8").read()
CSS = shell[shell.find("<style>"):shell.find("</style>") + 8]

FAQ = [
 ("練馬区の保育園の点数（指数）はどう計算しますか？", "選考指数＝父の基本指数＋母の基本指数＋調整指数です。基本指数は就労日数×時間で決まり（月20日以上・8時間以上＝40点が上限）、各保護者の上限は40点。ひとり親世帯は＋8点などの調整指数が加わります。本ツールは区公式「練馬区保育実施基準表」（令和8年度版）の数値をそのまま使っています。"),
 ("フルタイム共働きは何点になりますか？", "父母とも月20日以上・1日8時間以上の就労なら40点＋40点＝80点です。ここにきょうだい在園＋2点、育休中（1歳児クラス）＋1点などの調整指数が加わります。令和8年4月1次の実績では、1歳児クラスのボーダーが80〜84点の園が多く、80点ちょうどでは入れない園もありました。"),
 ("ボーダー（最低指数）はどこで公開されていますか？", "練馬区が公式に、園ごと×年齢クラスごとの「最低指数一覧」を4地区（練馬・光が丘・石神井・大泉）のPDFで公開しています。本ツールはその令和8年4月1次利用調整分（204園）を収録しています。東京23区でも園別ボーダーを公式公開している区は少数です。"),
 ("この結果で来年の合否は分かりますか？", "分かりません。表示されるのは令和8年4月1次の実績であり、来年は申込者の構成で変わります。また区の利用調整は指数同点時の優先順位など本ツールで再現できない要素を含みます。目安としてお使いいただき、正確な判定は練馬区保育課にご確認ください。"),
 ("令和9年4月入園の申込締切はいつですか？", "1次申込は令和8年11月6日（金）17時15分受理分までです（郵送は11月2日（月）消印有効）。区公式ページ（2026年8月1日更新）で確認しています。2次以降の日程は10月1日公開予定の「保育利用のご案内（令和9年度版）」に掲載されます。"),
 ("育休中の加点はありますか？", "あります。保護者のいずれかが申込締切日時点で育児休業を取得している場合、1歳児クラスは＋1点、2歳児クラス以上は＋2点です（類型が就労の場合に限る）。0歳児クラスには育休加点はありません。"),
]
faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}, ensure_ascii=False)
app_ld = json.dumps({"@context": "https://schema.org", "@type": "WebApplication", "name": "練馬区 保育園点数計算＆ボーダー逆引き", "url": URL, "applicationCategory": "UtilitiesApplication", "operatingSystem": "All", "inLanguage": "ja", "description": DESC, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}, "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": "https://www.noe-match.com/"}}, ensure_ascii=False)
bc_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"}, {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": "https://www.noe-match.com/#tools"}, {"@type": "ListItem", "position": 3, "name": "練馬区 保育園点数計算＆ボーダー逆引き"}]}, ensure_ascii=False)

faq_html = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a) for i, (q, a) in enumerate(FAQ))

# ---- 保護者の状況 select options（基本指数） ----
def work_opts(prefix, pts):
    # pts: dict day-> list of (label, points) already ordered
    return pts

PARENT_OPTS = """
<optgroup label="就労中（月20日以上）">
<option value="40">1日8時間以上（40点）</option>
<option value="37">1日7〜8時間未満（37点）</option>
<option value="34">1日6〜7時間未満（34点）</option>
<option value="31">1日5〜6時間未満（31点）</option>
<option value="28">1日4〜5時間未満（28点）</option>
</optgroup>
<optgroup label="就労中（月16〜19日）">
<option value="37">1日8時間以上（37点）</option>
<option value="34">1日7〜8時間未満（34点）</option>
<option value="31">1日6〜7時間未満（31点）</option>
<option value="28">1日5〜6時間未満（28点）</option>
<option value="25">1日4〜5時間未満（25点）</option>
</optgroup>
<optgroup label="就労中（月12〜15日）">
<option value="34">1日8時間以上（34点）</option>
<option value="31">1日7〜8時間未満（31点）</option>
<option value="28">1日6〜7時間未満（28点）</option>
<option value="25">1日5〜6時間未満（25点）</option>
<option value="22">1日4〜5時間未満（22点）</option>
</optgroup>
<optgroup label="就労内定（これから働く・月20日以上）">
<option value="27">1日8時間以上（27点）</option>
<option value="25">1日7〜8時間未満（25点）</option>
<option value="23">1日6〜7時間未満（23点）</option>
</optgroup>
<optgroup label="その他の類型">
<option value="24">出産（予定日前後の対象期間）（24点）</option>
<option value="40">疾病・負傷（入院・寝たきり・精神疾患）（40点）</option>
<option value="20">疾病・負傷（自宅療養）（20点）</option>
<option value="40">障害（身障1・2級等）（40点）</option>
<option value="40">介護・看護（重度心身障害者等）（40点）</option>
<option value="30">介護・看護（月48時間以上の付添い）（30点）</option>
<option value="10">求職中（10点）</option>
</optgroup>"""

HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VLQBH0S1SL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-VLQBH0S1SL');document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href*="px.a8.net"],a[href*="t.afi-b.com"]');if(a){try{gtag('event','aff_click',{link_domain:(a.href.indexOf('a8.net')>-1?'a8':'afb'),page_slug:location.pathname});}catch(x){}}},true);</script>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<link rel="canonical" href="__URL__">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:type" content="website">
<meta property="og:url" content="__URL__">
<meta property="og:image" content="https://www.noe-match.com/images/garugaru-og.png">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://www.noe-match.com/images/garugaru-og.png">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@500;600;700;900&display=swap" rel="stylesheet">
__CSS__
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
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ 練馬区 保育園点数計算＆ボーダー逆引き</div>
<style>
.result .big{background:linear-gradient(rgba(250,249,247,.92),rgba(250,249,247,.88)),url('../../images/lp/room-light.jpg') center/cover}
.chk{display:flex;align-items:flex-start;gap:9px;margin:9px 0;font-size:.86rem;font-weight:500;cursor:pointer;line-height:1.6}
.chk input{width:17px;height:17px;margin-top:3px;flex:none;accent-color:#7c2e42}
.chk .pt{color:#7c2e42;font-weight:800;white-space:nowrap}
.chk .pt.minus{color:#3e7d57}
.legend{font-size:.78rem;color:var(--sub);line-height:1.9;background:var(--alt);border-radius:6px;padding:12px 14px;margin:14px 0}
.b-ok{background:#edf3ee!important}
.b-near{background:#f6f0e1!important}
td.mark{color:var(--sub)}
.tag{display:inline-block;font-size:.68rem;font-weight:700;padding:1px 8px;border-radius:10px;vertical-align:1px}
.tag.ok{background:#edf3ee;color:#3e7d57}
.tag.near{background:#f6f0e1;color:#a1761f}
.tag.no{background:#f3e8eb;color:#7c2e42}
</style>

<div class="tool-hero" style="background-image:url('../../images/lp/room-light.jpg')"><div class="tool-hero-inner">
<svg class="hero-mark" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><circle cx="32" cy="32" r="31" fill="#f7f5f2"/><image href="../../images/emblems/scale.png" x="9" y="9" width="46" height="46"/></svg>
<h1>練馬区の保育園 点数計算＆内定ボーダー逆引き</h1>
<p>区公式の指数表（令和8年度版）で点数を計算し、令和8年4月1次の園別最低指数（区公式公開・204園）と照合。あなたの点数で内定が出ていた園を逆引きします。無料・登録不要。</p>
</div></div>

<article>
<blockquote><strong>練馬区は「園ごとの内定最低指数」を公式に公開している数少ない自治体です。</strong>だから点数を出すだけでなく、「その点数でどの園に入れたか」まで実績で確認できます。本ツールの数値はすべて区公式の公開資料から取っています。</blockquote>
<p>計算に使うのは区公式「練馬区保育実施基準表」（保育利用のご案内 令和8年度版）、逆引きに使うのは区公式「最低指数一覧（令和8年4月1次利用調整）」です。<strong>表示されるのは今年4月の実績であり、来年の合否予測ではありません</strong>——この線は最初に引いておきます。</p>

<h2>STEP1｜世帯の点数（選考指数）を計算する</h2>
<p>選考指数＝<strong>父の基本指数＋母の基本指数＋調整指数</strong>。各保護者の基本指数の上限は40点です。</p>
<div class="calc" id="calcForm">
  <div class="row2">
    <div class="fld">
      <label for="p1">保護者A（申込者）の状況</label>
      <select id="p1">__PARENT_OPTS__</select>
    </div>
    <div class="fld">
      <label for="p2">保護者B（配偶者）の状況</label>
      <select id="p2">
      <optgroup label="世帯の形">
      <option value="single">ひとり親世帯（40点＋調整8点を自動加算）</option>
      </optgroup>__PARENT_OPTS2__</select>
      <div class="hint">ひとり親（死亡・離婚・離婚前提の別居・未婚等）は不存在40点＋調整指数8点が適用されます</div>
    </div>
  </div>
  <div class="fld">
    <label for="ageClass">申込む年齢クラス（来年4月時点）</label>
    <select id="ageClass">
      <option value="1歳" selected>1歳児クラス</option>
      <option value="0歳_8か月以上">0歳児クラス（8か月以上）</option>
      <option value="0歳_6か月以上">0歳児クラス（6か月以上）</option>
      <option value="0歳_100日以上">0歳児クラス（100日以上）</option>
      <option value="2歳">2歳児クラス</option>
      <option value="3歳_一般">3歳児クラス</option>
      <option value="4歳_一般">4歳児クラス</option>
      <option value="5歳">5歳児クラス</option>
    </select>
    <div class="hint">育休加点（1歳＋1点／2歳以上＋2点）の判定に使います</div>
  </div>
  <div class="fld"><label>あてはまるものにチェック（調整指数）</label>
    <label class="chk"><input type="checkbox" id="a_ikukyu"><span>保護者のいずれかが申込締切日時点で育児休業中（類型が就労の場合）<span class="pt" id="ikukyuPt">＋1〜2</span></span></label>
    <label class="chk"><input type="checkbox" id="a_kyodai"><span>きょうだいが在園する園への入園・転園を希望<span class="pt">＋2</span></span></label>
    <label class="chk"><input type="checkbox" id="a_douji"><span>同時に2人以上の入園を希望<span class="pt">＋2</span></span></label>
    <label class="chk"><input type="checkbox" id="a_tatai"><span>多胎児（双子等）の入園・転園希望<span class="pt">＋3</span></span></label>
    <label class="chk"><input type="checkbox" id="a_mishu3"><span>未就学児が3人以上いる世帯<span class="pt">＋5</span></span></label>
    <label class="chk"><input type="checkbox" id="a_sho3"><span>小3までの児童が3人以上いる世帯（上と重複不可・自動で高い方を採用）<span class="pt">＋2</span></span></label>
    <label class="chk"><input type="checkbox" id="a_ninkagai"><span>認可外保育施設等に一定時間以上預けている（育休中を除く）<span class="pt">＋2</span></span></label>
    <label class="chk"><input type="checkbox" id="a_hoikushi"><span>保護者が保育士等として区内の保育施設・幼稚園に就労<span class="pt">＋1</span></span></label>
    <label class="chk"><input type="checkbox" id="a_tanshin"><span>保護者に単身赴任の予定<span class="pt">＋1</span></span></label>
    <label class="chk"><input type="checkbox" id="a_shogai"><span>申込児童が障害または配慮を必要とする<span class="pt">＋12</span></span></label>
    <label class="chk"><input type="checkbox" id="a_sofu"><span>65歳未満の同居予定の祖父母が保育にあたれる<span class="pt minus">−4</span></span></label>
    <label class="chk"><input type="checkbox" id="a_kugai"><span>区外在住（勤務地が区内なら−4／区外なら−6。低い方で計算）<span class="pt minus">−4</span></span></label>
    <label class="chk"><input type="checkbox" id="a_keizoku"><span>就労等が同一条件で1か月以上継続していない<span class="pt minus">−3</span></span></label>
  </div>
  <button type="button" class="calc-btn" id="run">点数を計算してボーダーと照合する</button>
</div>

<div class="result" id="result" aria-live="polite">
  <div class="big">
    <div class="lbl">あなたの世帯の選考指数（目安）</div>
    <div class="num" id="total">—</div>
  </div>
  <div class="grid3">
    <div class="cell"><div class="lbl">保護者A 基本指数</div><div class="num" id="r1">—</div></div>
    <div class="cell"><div class="lbl">保護者B 基本指数</div><div class="num" id="r2">—</div></div>
    <div class="cell"><div class="lbl">調整指数 合計</div><div class="num" id="r3">—</div></div>
  </div>
  <p class="sub-num" id="rNote"></p>

  <h3>STEP2｜この点数で内定が出ていた園（令和8年4月1次実績）</h3>
  <div class="fld" style="margin:10px 0">
    <label for="district">地区を選ぶ</label>
    <select id="district">
      <option value="練馬地区">練馬地区</option>
      <option value="光が丘地区">光が丘地区</option>
      <option value="石神井地区">石神井地区</option>
      <option value="大泉地区">大泉地区</option>
    </select>
  </div>
  <div id="summary"></div>
  <div class="table-wrap"><table id="parks"></table></div>
  <div class="legend"><strong>記号の意味（区公式PDFの表記のまま）：</strong>数字＝その園・クラスで内定した世帯の最低指数／<span class="tag ok">圏内</span>＝あなたの点数が最低指数以上／<span class="tag near">あと1〜2点</span>＝最低指数まで1〜2点差／「残N」＝1次終了時点の表記（欠員数とみられる・区の凡例に説明なし）／「全員内定」「なし」＝卒園枠等の表記／「×」＝欠員なし／「＊」＝内定者が少なく非公開／「―」＝当該クラスの設定なし。</div>
</div>

<h2>この計算の前提（出典をすべて示します）</h2>
<div class="table-wrap"><table>
<tr><th>データ</th><th>出典</th><th>確認日</th></tr>
<tr><td>基本指数・調整指数</td><td>練馬区「練馬区保育実施基準表」（保育利用のご案内 令和8年度版 P.44〜48）</td><td>2026年8月23日</td></tr>
<tr><td>園別の最低指数（204園）</td><td>練馬区「最低指数一覧（令和8年4月1次利用調整）」認可保育園・4地区PDF</td><td>2026年8月23日</td></tr>
<tr><td>申込締切日</td><td>練馬区「【保育園等】申込みの締切日」（2026年8月1日更新）</td><td>2026年8月23日</td></tr>
</table></div>
<blockquote><strong>本ツールが再現していないもの：</strong>指数が同点だった場合の優先順位（区の内部基準）、基本指数の「その他」類型（10〜40点の幅で区が判定）、調整指数26番（児童福祉法上の配慮・3〜4点）など。また各調整指数には適用条件の細目があり、最終判定は区が行います。<strong>正確な点数と合否は練馬区保育課にご確認ください。</strong></blockquote>

<h2>令和9年4月入園の申込締切</h2>
<p><strong>1次申込：令和8年11月6日（金）17時15分受理分まで</strong>（郵送は11月2日（月）消印有効）。区公式ページで確認済みです（2026年8月1日更新）。2次以降の日程は10月1日公開予定の「保育利用のご案内（令和9年度版）」に掲載されます。指数を上げる要素（就労時間の変更・認可外の利用実績など）は締切日時点で判定されるため、動くならこの日から逆算してください。</p>

<h2>点数の実際の水準｜「80点」がスタートライン</h2>
<p>令和8年4月1次の実績を集計すると、数値が公表されている枠の多くで最低指数は70点台後半〜80点台前半でした。フルタイム共働き（40＋40＝80点）は<strong>多数派であって優位ではありません</strong>。差がつくのは調整指数——きょうだい在園＋2、育休加点＋1〜2、認可外利用＋2——の側です。逆に、祖父母同居−4や就労継続1か月未満−3は効き方が大きいので、申込前に条件を確認する価値があります。</p>

<h2>保活は「点数」と「時間の分担」の両輪</h2>
<p>点数の計算はこのツールで数分で終わります。実際に大変なのは、見学・申込書類・復職準備を産後の生活の中でこなす段取りの方です。保活を片方の親だけが抱えると、点数以前に家庭の側が回らなくなります。役割の分け方は<a href="/articles/sango-kaji-buntan/">産後の家事分担｜実際に揉めるのはどこか</a>に、復職前の体調と自分の時間の立て直しは<a href="/tools/sango-recovery-check/">産後リカバリー診断</a>に整理しています。</p>

<div style="background:#f7f5f2;border:1px solid #e6e2dc;padding:20px 22px;margin:22px 0;text-align:center">
<p style="font-size:.7rem;color:#999;margin:0 0 6px;text-align:left">PR</p>
<p style="font-weight:700;margin:0 0 8px">復職準備で最初に決まらなくなるのは「毎日の食事」</p>
<p style="font-size:.8rem;color:#5a6068;margin:0 0 14px">慣らし保育と復職が重なる時期は、作る手間を減らす手段を先に確保しておくと段取りが崩れにくくなります。Oisixは食材宅配のおためしセット（内容・価格・配送エリアは公式サイトでご確認ください）。</p>
<a href="https://px.a8.net/svt/ejp?a8mat=4B8B4Q+5CWKMY+3RK+2TBJQA" rel="nofollow sponsored noopener" target="_blank" style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;padding:13px 32px;text-decoration:none">Oisixのおためしセットを見る</a>
<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">食材宅配サービス。保育園の入園可否とは関係ありません</p>
</div>

<h2>あわせて読む</h2>
<ul>
<li><a href="/articles/sango-kaji-buntan/">産後の家事分担｜実際に揉めるのはどこか</a></li>
<li><a href="/tools/sango-recovery-check/">【無料】産後リカバリー診断｜復職前の体調と段取りを整理</a></li>
<li><a href="/articles/sango-biyou-itsukara/">産後の美容はいつから再開できるのか</a></li>
<li><a href="/tools/garugaru-check/">【無料】ガルガル期セルフチェック</a></li>
</ul>
</article>

<!-- LINE-CTA -->
<section id="line-cta" style="max-width:680px;margin:56px auto 64px;padding:36px 28px;background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;">
  <p style="margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif;">NOE OFFICIAL LINE</p>
  <p style="margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5;">保活と復職の段取りに効くFACTをLINEで</p>
  <p style="margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;">結婚・出産まわりのお金と制度のFACTだけを、週1回・短文で届けます。<br>気になることの相談も、追加後そのままトークでどうぞ。</p>
  <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{gtag('event','line_add_click',{tool:'__SLUG__'});}catch(e){}"
     style="display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;font-size:15px;font-weight:600;text-decoration:none;">友だち追加して受け取る</a>
  <p style="margin:14px 0 0;font-size:11px;color:#8a8f95;">登録は無料・配信は週1回だけ。いつでも解除できます。</p>
</section>

<script>
(function(){
"use strict";
var BORDER=__BORDER__;
var COLS=__COLS__;
function $(id){return document.getElementById(id);}
function ageLabel(k){return {"0歳_100日以上":"0歳（100日〜）","0歳_6か月以上":"0歳（6か月〜）","0歳_8か月以上":"0歳（8か月〜）","1歳":"1歳","2歳":"2歳","3歳_一般":"3歳（一般）","4歳_一般":"4歳（一般）","5歳":"5歳"}[k]||k;}
$('ageClass').addEventListener('change',function(){
  var a=this.value; $('ikukyuPt').textContent = a==='1歳' ? '＋1' : (a.indexOf('0歳')===0 ? '対象外' : '＋2');
});
function calc(){
  var age=$('ageClass').value;
  var single=$('p2').value==='single';
  var b1=Math.min(40,+$('p1').value||0);
  var b2=single?40:Math.min(40,+$('p2').value||0);
  var adj=0, notes=[];
  if(single){adj+=8;notes.push('ひとり親＋8');}
  if($('a_ikukyu').checked){
    if(age==='1歳'){adj+=1;notes.push('育休中＋1');}
    else if(age.indexOf('0歳')!==0){adj+=2;notes.push('育休中＋2');}
    else{notes.push('育休加点は0歳児クラス対象外（＋0）');}
  }
  if($('a_kyodai').checked){adj+=2;notes.push('きょうだい在園＋2');}
  if($('a_douji').checked){adj+=2;notes.push('同時申込＋2');}
  if($('a_tatai').checked){adj+=3;notes.push('多胎児＋3');}
  if($('a_mishu3').checked){adj+=5;notes.push('未就学3人＋5');}
  else if($('a_sho3').checked){adj+=2;notes.push('小3まで3人＋2');}
  if($('a_mishu3').checked&&$('a_sho3').checked){notes.push('※未就学3人と小3まで3人は重複不可のため高い方（＋5）のみ適用');}
  if($('a_ninkagai').checked){if($('a_ikukyu').checked){notes.push('※認可外利用＋2は育休中は対象外のため未適用');}else{adj+=2;notes.push('認可外利用＋2');}}
  if($('a_hoikushi').checked){adj+=1;notes.push('保育士等＋1');}
  if($('a_tanshin').checked){adj+=1;notes.push('単身赴任予定＋1');}
  if($('a_shogai').checked){adj+=12;notes.push('児童の障害・配慮＋12');}
  if($('a_sofu').checked){adj-=4;notes.push('祖父母同居−4');}
  if($('a_kugai').checked){adj-=4;notes.push('区外在住−4（勤務地区外なら−6）');}
  if($('a_keizoku').checked){adj-=3;notes.push('就労継続1か月未満−3');}
  var total=b1+b2+adj;
  $('r1').textContent=b1+'点'; $('r2').textContent=b2+'点';
  $('r3').textContent=(adj>=0?'＋':'')+adj+'点';
  $('total').innerHTML=total+'<small>点</small>';
  $('rNote').textContent=notes.length?('内訳：'+notes.join('／')):'調整指数の適用なし';
  render(total,age);
  $('result').classList.add('show');
  try{gtag('event','tool_calc',{tool:'__SLUG__',score:total});}catch(e){}
  $('result').scrollIntoView({behavior:'smooth',block:'start'});
}
function render(score,age){
  var d=$('district').value;
  var ci=COLS.indexOf(age);
  var rows=BORDER[d]||[];
  var ok=0,near=0,over=0,open=0;
  var tb='<thead><tr><th>園名</th><th>'+ageLabel(age)+'の最低指数<br>（R8年4月1次）</th><th>あなたの点数で</th></tr></thead><tbody>';
  rows.forEach(function(r){
    var v=r[1][ci];
    var cls='',tag='',cell;
    if(typeof v==='number'){
      if(score>=v){cls=' class="b-ok"';tag='<span class="tag ok">圏内</span>';ok++;}
      else if(score>=v-2){cls=' class="b-near"';tag='<span class="tag near">あと'+(v-score)+'点</span>';near++;}
      else{tag='<span class="tag no">'+(v-score)+'点差</span>';over++;}
      cell=v+'点';
    } else if(v==='全員内定'||String(v).indexOf('残')===0){
      cls=' class="b-ok"';tag='<span class="tag ok">空きあり表記</span>';open++;cell=String(v);
    } else if(v==='50以下'){
      cls=' class="b-ok"';tag=score>=50?'<span class="tag ok">圏内</span>':'<span class="tag near">50点以下で内定</span>';ok++;cell='50以下';
    } else {
      cell='<span class="mark">'+(v===''?'—':v)+'</span>';tag='';
    }
    tb+='<tr'+cls+'><td>'+r[0]+'</td><td>'+cell+'</td><td>'+tag+'</td></tr>';
  });
  tb+='</tbody>';
  $('parks').innerHTML=tb;
  $('summary').innerHTML='<p style="font-size:.9rem"><strong>'+d+'・'+ageLabel(age)+'：'+score+'点</strong>で見ると、数値公表枠のうち<strong style="color:#3e7d57">圏内 '+ok+'園</strong>／あと1〜2点 '+near+'園／届かず '+over+'園。ほかに「残」「全員内定」表記が'+open+'園。<span style="color:#8a9097;font-size:.8rem">※令和8年4月1次の実績です。来年の合否を保証するものではありません。</span></p>';
}
$('run').addEventListener('click',calc);
$('district').addEventListener('change',function(){
  if($('result').classList.contains('show')) calc();
});
})();
onscroll=function(){document.getElementById("top").classList.toggle('show',scrollY>300)};
</script>

<article>
<h2 id="faq">よくある質問</h2>
__FAQ__
</article>
<footer><div class="footer-inner">
<div><a href="/">ホーム</a><a href="/articles/">記事一覧</a><a href="/about.html">運営者情報</a><a href="/privacy-policy.html">プライバシー</a><a href="/disclaimer.html">免責事項</a></div>
<p class="footer-disc">※本ツールは練馬区公式の公開資料（2026年8月23日確認）に基づく目安です。利用調整の最終判定は練馬区が行います。<strong style="color:#cda">【PR】</strong>本サイトはアフィリエイト広告を含みます。<br>&copy; 2026 Noe結婚設計室</p>
</div></footer>
<button id="top" onclick="scrollTo({top:0,behavior:'smooth'})">↑</button>
<script>
document.addEventListener('click',function(e){
  var b=e.target.closest&&e.target.closest('.calc-btn,#run,#calc,button[type="submit"],.btn-primary');
  if(b){try{gtag('event','tool_result',{tool:'__SLUG__'});}catch(x){}}
},true);
</script>
</body>
</html>
"""

out = (HTML.replace("__TITLE__", TITLE).replace("__DESC__", DESC).replace("__URL__", URL)
       .replace("__CSS__", CSS).replace("__FAQLD__", faq_ld).replace("__APPLD__", app_ld)
       .replace("__BCLD__", bc_ld)
       .replace("__PARENT_OPTS2__", PARENT_OPTS.replace('value="40">1日8時間以上（40点）', 'value="40" selected>1日8時間以上（40点）', 1))
       .replace("__PARENT_OPTS__", PARENT_OPTS)
       .replace("__BORDER__", BORDER_JS).replace("__COLS__", json.dumps(COLS, ensure_ascii=False))
       .replace("__FAQ__", faq_html).replace("__SLUG__", SLUG))

os.makedirs("tools/%s" % SLUG, exist_ok=True)
io.open("tools/%s/index.html" % SLUG, "w", encoding="utf-8").write(out)
n_parks = sum(len(v) for v in districts.values())
print("built tools/%s/ | %d parks | %d KB" % (SLUG, n_parks, len(out.encode("utf-8")) // 1024))
