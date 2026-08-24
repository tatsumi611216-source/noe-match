# -*- coding: utf-8 -*-
"""こども誰でも通園制度 自治体別ナビ（上限時間・利用料・予約方法の早見）
データ出典: 各自治体公式ページ＋こども家庭庁（2026-08-25 確認）。数値は原文どおり。"""
import io, json, os

SLUG = "daredemo-tsuen-jichitai"
URL = "https://www.noe-match.com/tools/%s/" % SLUG
TITLE = "こども誰でも通園制度は月何時間使える？自治体別の上限時間・利用料早見表【令和8年度】"
DESC = "こども誰でも通園制度（乳児等通園支援事業）の月の上限時間は自治体で違います。国基準は月10時間ですが、渋谷区は最大月64時間、世田谷区・練馬区は月48時間、品川区は月30時間、江戸川区は月24時間、足立区は月10時間。自治体を選ぶと上限時間・利用料・予約方法・申込の開始時期が出ます。出典は各自治体公式（2026年8月25日確認）。"
H1 = "こども誰でも通園制度は月何時間使える？｜自治体別の上限時間・利用料早見表"
OGD = "国の基準は月10時間。渋谷区は最大月64時間、世田谷区・練馬区は月48時間、足立区は月10時間。自治体別の上限時間・利用料・予約方法を早見表で。"

CITIES = [
 {"key": "shibuya", "name": "渋谷区", "cap": 64, "cap_label": "最大 月64時間",
  "cap_note": "「児童1人あたり、最大月64時間上限」。3歳の誕生日の前日からは月54時間。未利用時間の翌月繰越は不可。",
  "fee": "「1時間あたり300円程度」。ただし「都内在住者は原則無料です」。施設ごとに料金は異なる。",
  "fee_extra": "教材費などの実費、上限時間を超えた分は施設が定める料金。",
  "reserve": "こども誰でも通園制度総合支援システム",
  "apply": "電子申請フォーム「乳児等支援給付認定申請フォーム」。認定申請の受付は令和8年2月2日から。認定証の発行は令和8年3月下旬、システムの利用は令和8年4月1日以降。",
  "facil": "区立保育園4園・区立保育室2室・私立保育園12園・認定こども園1園・認証保育所5施設",
  "age": "未就園児（0歳6か月〜2歳児クラス）。3歳の誕生日前日から対象外",
  "src": "https://www.city.shibuya.tokyo.jp/kodomo/hoiku/hoiku-service/kodomodaredemotsuen.html",
  "src_label": "渋谷区「令和8年度こども誰でも通園制度」"},
 {"key": "setagaya", "name": "世田谷区", "cap": 48, "cap_label": "最大 月48時間",
  "cap_note": "国制度10時間＋区の上乗せ枠38時間。区民が区内施設を利用する場合。区外施設の利用や区外在住者は国制度の月10時間のみ。",
  "fee": "区民が区内施設を使う場合は無償。区外在住者が区内施設を使う場合は1時間あたり300円（給食費等を含む）。",
  "fee_extra": "そのほか実費負担あり。",
  "reserve": "こども誰でも通園制度総合支援システム（施設を検索して初回面談を申込→面談・契約で曜日と時間を決める）",
  "apply": "総合支援システムから利用申込。4月の利用は2月中の申請が必要。",
  "facil": "実施施設一覧をPDFで公開（令和8年7月23日更新）",
  "age": "生後6か月〜2歳児クラス年齢（3歳の誕生日を迎えた年度末まで／施設種別により異なる）",
  "src": "https://www.city.setagaya.lg.jp/02243/29576.html",
  "src_label": "世田谷区「世田谷版こども誰でも通園制度（乳児等通園支援事業）について」"},
 {"key": "nerima", "name": "練馬区", "cap": 48, "cap_label": "月48時間（1日8時間まで）",
  "cap_note": "月48時間のうち10時間が全国で使える国制度、38時間が練馬区内の園で使える区の上乗せ。1日あたりの上限は8時間。",
  "fee": "無償（当分の間）。ただし区内施設に限る。",
  "fee_extra": "給食等は別途自己負担。",
  "reserve": "区内施設は総合支援システムでは予約できない。実施施設一覧に記載の申込先へ直接申し込む。",
  "apply": "ぴったりサービス（児童のマイナンバーカード）またはLoGoフォームから申請。認定まで3週間程度。",
  "facil": "実施施設一覧を区公式ページに掲載",
  "age": "0歳6か月〜2歳児までの未就園児",
  "src": "https://www.city.nerima.tokyo.jp/kosodatekyoiku/kodomo/hoiku/daredemo.html",
  "src_label": "練馬区「練馬区こども誰でも通園事業」"},
 {"key": "shinagawa", "name": "品川区", "cap": 30, "cap_label": "月30時間",
  "cap_note": "月30時間までを上限に定期的な預かりを実施。",
  "fee": "1時間あたり300円。区内在住の子どもが区内施設を利用した場合の利用料金は無料。",
  "fee_extra": "実費の扱いはページに記載なし（施設に確認）。",
  "reserve": "こども誰でも通園制度総合支援システム（認定後にアカウント発行通知メールが届く）。予約システムで利用予定の施設に直接申し込む。",
  "apply": "認定申請は原則電子（マイナポータル）。郵送・窓口も可。事業の開始は令和8年4月1日（水）。",
  "facil": "認可保育所・認定こども園・家庭的保育事業等 59施設",
  "age": "0歳6か月〜2歳児クラス（満3歳に達した年度末まで）の未在籍児",
  "src": "https://www.city.shinagawa.tokyo.jp/PC/kodomo/kodomo-hoyou/20251215111822.html",
  "src_label": "品川区「【令和8年度】乳児等通園支援事業（こども誰でも通園制度）について」"},
 {"key": "edogawa", "name": "江戸川区", "cap": 24, "cap_label": "月24時間",
  "cap_note": "子ども1人につき月24時間まで。区民が区外施設を使う場合と、区外在住者が区内施設を使う場合は月10時間。",
  "fee": "区民が区内施設を利用する場合は無償。区民の区外施設利用および区外在住者は有料（施設ごとに異なる）。",
  "fee_extra": "用具などの実費がかかる場合あり。",
  "reserve": "こども誰でも通園制度総合支援システム（施設を選び、面談日の調整から利用予約まで行う）",
  "apply": "原則としてオンラインのみ。受付開始は令和8年3月4日から。",
  "facil": "「令和8年度乳児等通園支援事業認可予定事業者一覧」をPDFで公開",
  "age": "0歳6か月〜2歳児の子ども（医療的ケア児対応施設は満1歳〜2歳児）",
  "src": "https://www.city.edogawa.tokyo.jp/e047/kosodate/kosodate/hoiku/ichiji/kodomodaredemotsuen.html",
  "src_label": "江戸川区「こども誰でも通園制度（乳児等通園支援事業）」"},
 {"key": "adachi", "name": "足立区", "cap": 10, "cap_label": "月10時間（国基準どおり）",
  "cap_note": "月10時間まで。ただし私立幼稚園および私立認定こども園の2歳児クラスに限り、月10時間を超えて利用できる。",
  "fee": "無料（足立区民が区内施設を利用する場合）。区外施設の利用には補助あり。",
  "fee_extra": "利用料以外に別途費用が発生する場合あり。",
  "reserve": "各施設に電話等で面談予約。事前面談のあと、施設で利用予約。",
  "apply": "足立区オンライン申請システムまたは窓口から申込。認定まで10営業日程度。",
  "facil": "実施施設一覧をPDFで公開（総合支援システム内でも公開）",
  "age": "0歳6か月〜3歳（満3歳到達後、最初の3月31日）まで",
  "src": "https://www.city.adachi.tokyo.jp/kodomo-unei/daredemo-riyousya1.html",
  "src_label": "足立区「令和8年度足立区こども誰でも通園制度」"},
 {"key": "kokuhyo", "name": "上記以外の自治体（国の基準）", "cap": 10, "cap_label": "月10時間",
  "cap_note": "国は補助基準額の上で月の上限を10時間としており、令和8年度は「月10時間」とすることとされている。上乗せの有無は自治体ごとに違うため、お住まいの自治体の公式ページで必ず確認してください。",
  "fee": "利用料は自治体が定める。試行段階では1時間あたり300円程度が目安として使われてきた。",
  "fee_extra": "実費の扱いは自治体・施設による。",
  "reserve": "こども誰でも通園制度総合支援システム（つうえんポータル）",
  "apply": "お住まいの市町村に申請し、認定を受けたうえでシステムに登録。",
  "facil": "つうえんポータルで都道府県・市町村を選ぶと利用できるか確認できる",
  "age": "0歳6か月から満3歳未満（未就園児）",
  "src": "https://www.cfa.go.jp/policies/hoiku/daredemo-tsuen",
  "src_label": "こども家庭庁「こども誰でも通園制度について」"},
]

FAQ = [
 ("こども誰でも通園制度は月何時間まで使えますか？",
  "国の基準は月10時間ですが、自治体が独自に上乗せしている場合があります。2026年8月25日に公式ページを確認した範囲では、渋谷区が最大月64時間（3歳の誕生日前日から月54時間）、世田谷区と練馬区が月48時間、品川区が月30時間、江戸川区が月24時間、足立区が月10時間でした。上乗せ分は原則としてその自治体の中の施設でしか使えず、区外施設の利用や区外在住者は国制度の月10時間になります。"),
 ("利用料はいくらですか？",
  "自治体によって違います。国の試行段階では1時間あたり300円程度が目安とされてきました。渋谷区は「1時間あたり300円程度。ただし都内在住者は原則無料」、品川区は「1時間300円。区内在住の子どもが区内施設を利用した場合は無料」、世田谷区・練馬区・江戸川区・足立区は区民が区内施設を使う場合は無償・無料と公表しています。給食費や教材費などの実費が別にかかる場合があります。"),
 ("本格実施はいつからですか？",
  "2025年度に子ども・子育て支援法に基づく地域子ども・子育て支援事業として制度化され、2026年度から同法に基づく新たな給付として全国の自治体で実施されます（こども家庭庁）。認定申請の受付開始日は自治体ごとに違い、渋谷区は令和8年2月2日から、江戸川区は令和8年3月4日からでした。"),
 ("対象になるのは何歳のこどもですか？",
  "国の制度としては0歳6か月から満3歳未満の未就園児です。自治体によって表現が異なり、足立区は「0歳6か月から3歳（満3歳到達後、最初の3月31日）まで」、渋谷区は「3歳の誕生日の前日から対象外」としています。保育所などに在籍していないことが前提です。"),
 ("予約はどこからしますか？",
  "多くの自治体は国の「こども誰でも通園制度総合支援システム」（つうえんポータル）で施設検索と予約を行います。ただし練馬区は区内施設について「総合支援システムでは予約できない」と明記しており、実施施設一覧の申込先へ直接申し込む方式です。足立区も各施設へ電話等で面談予約をします。予約の経路は自治体で違うので、最初に確認してください。"),
 ("未利用の時間は翌月に繰り越せますか？",
  "渋谷区は「各月の上限であり、未利用時間を翌月以降に繰り越すことはできません」と明記しています。他の自治体でも月単位の上限として運用されるのが基本です。繰り越しの可否は各自治体の公式ページで確認してください。"),
]

faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}, ensure_ascii=False)
app_ld = json.dumps({"@context": "https://schema.org", "@type": "WebApplication",
    "name": "こども誰でも通園制度 自治体別ナビ", "url": URL, "applicationCategory": "UtilitiesApplication",
    "operatingSystem": "All", "inLanguage": "ja", "description": DESC,
    "datePublished": "2026-08-25", "dateModified": "2026-08-25",
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
    "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": "https://www.noe-match.com/"}}, ensure_ascii=False)
bc_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
    {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": "https://www.noe-match.com/#tools"},
    {"@type": "ListItem", "position": 3, "name": "こども誰でも通園制度 自治体別ナビ"}]}, ensure_ascii=False)

shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
CSS = shell[shell.find("<style>"):shell.find("</style>") + 8]

opts = "".join('<option value="%s">%s</option>' % (c["key"], c["name"]) for c in CITIES)
rows = "".join('<tr><td><strong>%s</strong></td><td class="num-cell">%s</td><td>%s</td><td>%s</td></tr>'
               % (c["name"], c["cap_label"], c["fee"], c["reserve"])
               for c in sorted(CITIES, key=lambda x: -x["cap"]))
faq_html = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a) for i, (q, a) in enumerate(FAQ))
src_rows = "".join('<tr><td>%s</td><td><a href="%s" rel="noopener" target="_blank">%s</a></td><td>2026年8月25日</td></tr>'
                   % (c["name"], c["src"], c["src_label"]) for c in CITIES)
DATA_JS = json.dumps({c["key"]: c for c in CITIES}, ensure_ascii=False, separators=(",", ":"))

TPL = io.open("scripts/_daretsu_body.html", encoding="utf-8").read()

HTML = (TPL.replace("__TITLE__", TITLE).replace("__DESC__", DESC).replace("__OGD__", OGD)
        .replace("__URL__", URL).replace("__H1__", H1).replace("__CSS__", CSS)
        .replace("__FAQLD__", faq_ld).replace("__APPLD__", app_ld).replace("__BCLD__", bc_ld)
        .replace("__OPTS__", opts).replace("__ROWS__", rows).replace("__SRCROWS__", src_rows)
        .replace("__FAQHTML__", faq_html).replace("__DATA__", DATA_JS).replace("__SLUG__", SLUG))

os.makedirs("tools/%s" % SLUG, exist_ok=True)
io.open("tools/%s/index.html" % SLUG, "w", encoding="utf-8").write(HTML)
print("written: tools/%s/index.html  %d chars" % (SLUG, len(HTML)))
