# -*- coding: utf-8 -*-
"""こども誰でも通園制度 自治体別ナビ（上限時間・利用料・予約方法の早見）

データ出典: 各自治体の公式ページ＋こども家庭庁。確認日は CHECKED。
数値は原文どおりに入れる。公表が確認できないものは cap=None にして
「公表を確認できず」と表示する（推測で埋めない）。
"""
import io, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SLUG = "daredemo-tsuen-jichitai"
URL = "https://www.noe-match.com/tools/%s/" % SLUG
from _daretsu_data import CHECKED, CITIES

TITLE = "こども誰でも通園制度は月何時間使える？東京23区＋政令市20市の上限時間・利用料早見表【令和8年度】"
DESC = "こども誰でも通園制度（乳児等通園支援事業）の月の上限時間は自治体で違います。国基準は月10時間ですが、大田区は条件つきで最大160時間、渋谷区64時間、世田谷区・練馬区48時間、江東区40時間、品川区30時間、港区・江戸川区24時間。東京23区と政令指定都市20市の計43自治体を全部調べて早見表にしました。政令市で上乗せがあるのは京都市（月12時間）だけでした。自治体を選ぶと上限時間・利用料・予約の経路・申込の入口が出ます。出典は各自治体公式（2026年8月25日確認）。"
H1 = "こども誰でも通園制度は月何時間使える？｜東京23区＋政令市の上限時間・利用料早見表"
OGD = "国の基準は月10時間。大田区は条件つき最大160時間、渋谷区64時間、練馬区48時間、足立区10時間。東京23区と政令市の上限時間・利用料・予約の経路を早見表で。"


FAQ = [
 ("こども誰でも通園制度は月何時間まで使えますか？",
  "国の基準は月10時間ですが、自治体が独自に上乗せしている場合があります。東京23区を2026年8月25日に確認した範囲では、大田区が条件つきで最大160時間（同一施設で継続利用する場合の上乗せ150時間を含む）、渋谷区が最大64時間、世田谷区・練馬区が48時間、江東区が40時間、品川区が30時間、港区・江戸川区が24時間、中央区が20時間、豊島区が16時間、千代田区・台東区・墨田区・目黒区・杉並区・北区・板橋区・足立区が10時間でした。上乗せ分は原則としてその区の中の施設でしか使えません。"),
 ("いちばん長く使えるのはどの区ですか？",
  "2026年8月25日時点で公表を確認できた範囲では大田区です。国制度の月10時間に区が150時間を上乗せし、合計で最大月160時間となります。ただし上乗せが使えるのは「月10時間を同一の大田区内施設で利用した場合」に限られ、複数の施設に分けると追加分は使えません。上乗せ部分は別途契約が必要です。無条件の上限としては渋谷区の月64時間が最大です。"),
 ("利用料はいくらですか？",
  "自治体によって違います。多くの区は区民が区内施設を使う場合は無償ですが、有料の区もあります。台東区は1時間300円（30分150円／生活保護世帯0円、非課税世帯と所得割77,101円未満の世帯は100円）、中野区は1時間300円（減免あり）です。板橋区と杉並区は1時間300円ですが区民は実質負担0円としています。文京区は区民以外が月額9,600円という料金体系です。給食費・おやつ代・教材費などの実費は別にかかる場合があります。"),
 ("政令指定都市でも上乗せはありますか？",
  "2026年8月25日に政令指定都市20市すべての公式ページを確認した範囲では、時間の上乗せをしているのは京都市だけでした。京都市は「国の上限利用時間である10時間に本市が独自に2時間を上乗せし、合計12時間とします」としており、上乗せ分は京都市が認可・確認した施設でのみ使えます。ほかの18市（横浜・川崎・さいたま・千葉・大阪・名古屋・札幌・神戸・広島・仙台・北九州・熊本・堺・岡山・新潟・静岡・浜松・相模原）はいずれも国基準の月10時間でした。福岡市は令和8年度の上限時間を公式ページに掲載していません。時間の上乗せは東京23区に集中しており、政令市は所得に応じた減免で負担を下げる設計が主流です。"),
 ("本格実施はいつからですか？",
  "2025年度に子ども・子育て支援法に基づく地域子ども・子育て支援事業として制度化され、2026年度から同法に基づく新たな給付として全国の自治体で実施されます（こども家庭庁）。認定申請の受付開始日は自治体ごとに違い、渋谷区は令和8年2月2日、江戸川区は令和8年3月4日、板橋区は令和8年3月5日からでした。"),
 ("対象になるのは何歳のこどもですか？",
  "国の制度としては0歳6か月から満3歳未満の未就園児です。区によって表現が異なり、「3歳の誕生日の前々日まで」（千代田区・台東区・墨田区・北区・板橋区など）、「3歳の誕生日の2日前まで」（目黒区・杉並区）、「満3歳を迎える年度の年度末まで」（港区・江東区・足立区など）と分かれます。保育所などに在籍していないことが前提です。"),
 ("予約はどこからしますか？",
  "多くの自治体は国の「こども誰でも通園制度総合支援システム」（つうえんポータル）で施設検索と予約を行います。ただし練馬区は区内施設について「総合支援システムでは予約できない」と明記しており、実施施設一覧の申込先へ直接申し込む方式です。足立区は各施設へ電話等で面談予約、杉並区と文京区は「実施園の指定する方法」としています。予約の経路は自治体で違うので、最初に確認してください。"),
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
def _rows(group):
    sel = sorted([c for c in CITIES if c.get("group", "東京23区") == group],
                 key=lambda x: -(x["cap"] if x["cap"] is not None else -1))
    return "".join('<tr><td><strong>%s</strong></td><td class="num-cell">%s</td><td>%s</td><td>%s</td></tr>'
                   % (c["name"], c["cap_label"], c["fee"], c["reserve"]) for c in sel)
rows = _rows("東京23区")
rows_seirei = _rows("政令市")
faq_html = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a) for i, (q, a) in enumerate(FAQ))
src_rows = "".join('<tr><td>%s</td><td><a href="%s" rel="noopener" target="_blank">%s</a></td><td>%s</td></tr>'
                   % (c["name"], c["src"], c["src_label"], CHECKED) for c in CITIES)
for c in CITIES:
    c.setdefault("group", "国基準" if c["key"] == "kokuhyo" else "東京23区")
DATA_JS = json.dumps({c["key"]: c for c in CITIES}, ensure_ascii=False, separators=(",", ":"))

TPL = io.open("scripts/_daretsu_body.html", encoding="utf-8").read()
HTML = (TPL.replace("__TITLE__", TITLE).replace("__DESC__", DESC).replace("__OGD__", OGD)
        .replace("__URL__", URL).replace("__H1__", H1).replace("__CSS__", CSS)
        .replace("__FAQLD__", faq_ld).replace("__APPLD__", app_ld).replace("__BCLD__", bc_ld)
        .replace("__OPTS__", opts).replace("__ROWS__", rows).replace("__ROWS_SEIREI__", rows_seirei).replace("__SRCROWS__", src_rows)
        .replace("__FAQHTML__", faq_html).replace("__DATA__", DATA_JS).replace("__SLUG__", SLUG))

os.makedirs("tools/%s" % SLUG, exist_ok=True)
io.open("tools/%s/index.html" % SLUG, "w", encoding="utf-8").write(HTML)
print("written: tools/%s/index.html  %d chars  自治体%d件（うち上限非公表%d件）"
      % (SLUG, len(HTML), len(CITIES), sum(1 for c in CITIES if c["cap"] is None)))
