# -*- coding: utf-8 -*-
"""区選択ハブ「23区の子育て支援を比較」（2026-09-08 新設・strategy_2026Q4 月4 #4）

東京23区から1区を選ぶと、既存バンク5本の当該区の値を1画面に並べる。
  ひとり親支援   scripts/_hitorioya_data.py
  子ども医療費   scripts/_kodomo_iryo_data.py
  病児保育       scripts/_byoji_funin_data.py（病児のみ・不妊は出さない）
  こども誰でも通園 scripts/_daretsu_data.py（東京23区のみ）
  産後ケア       scripts/_sangocare_data.py（東京23区のみ）

原則:
- データはこの5ファイルから読むだけ。新規実査はしない。手で数字を書かない。
- 出す項目は下の pick_* で明示的に選ぶ。note は読者向けなので出してよいが、
  qa_note・kakunin_dekinakatta などの内部フィールドは出さない（8/31の教訓）。
  病児保育・産後ケアの note には「本調査」が混ざるので出さない（禁止語リントで止まる）。
- 生成物 tools/<slug>/index.html を公開後に直接パッチしたら、同じ行をこちらにも写す
  （9/6の教訓: 再実行でパッチが消える）。
- 頭語「保育園 点数」はこのページで受ける。練馬区限定ツールへのリンクは
  区が練馬のときだけ JS で出す（hoikuen-tensu-nerima 自体は実験中なので触らない）。

使い方:  python scripts/build_kosodate_hub.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
os.chdir(ROOT)

import _hitorioya_data as H
import _kodomo_iryo_data as K
import _byoji_funin_data as B
import _daretsu_data as D
import _sangocare_data as S

SLUG = "kosodate-shien-23ku"
URL = "https://www.noe-match.com/tools/%s/" % SLUG
PUBLISHED = "2026-09-08"

# ---------- 区の並び（キーは kodomo_iryo の順＝区コード順） ----------
WARD_ORDER = [(w["key"], w["name"]) for w in K.WARDS]
KEY_BY_NAME = {n: k for k, n in WARD_ORDER}
assert len(WARD_ORDER) == 23

H_BY_NAME = {w["ward"]: w for w in H.WARDS}
K_BY_KEY = {w["key"]: w for w in K.WARDS}
B_BY_KEY = {w["key"]: w for w in B.WARDS}
# 誰でも通園は WARD_ORDER の23キーで絞る（group 未設定の "kokuhyo"（国基準の参考行・cap=10）を
# 23区として数えると月10時間の区が9区になる。9/8 inspector BLOCK の再発防止）
_WARD_KEYS = {k for k, _ in WARD_ORDER}
D_BY_KEY = {c["key"]: c for c in D.CITIES if c["key"] in _WARD_KEYS}
assert len(D_BY_KEY) == 23, len(D_BY_KEY)
S_BY_KEY = {c["key"]: c for c in S.CITIES if c.get("group") == "東京23区"}

NA = "情報なし"          # 区の公式ページに記載が無い／取れていない（推測で埋めない）
NOT_APPLICABLE = "対象外"  # 制度としてその区に無い


def yen(v):
    return "情報なし" if v is None else "{:,}円".format(v)


# データファイルの作業メモ調の言い回しを読者向けに置き換える（表示側のみ。データは変更しない）
READER_WORDING = [
    ("区に直接確認することを勧める。", "利用時は区に確認が必要。"),
    ("本ページ本文中には数値の直接記載を確認できなかった", "区の案内に金額の直接の記載がない"),
]


def s(v):
    """None・空文字は「情報なし」。文字列は読者向けの言い回しに整えて返す。"""
    if v is None:
        return NA
    v = str(v).strip()
    for a, b in READER_WORDING:
        v = v.replace(a, b)
    return v if v else NA


def tri(v, yes, no):
    if v is True:
        return yes
    if v is False:
        return no
    return "区の公式ページに記載なし"


# ---------- 各バンクから出す項目を明示的に選ぶ ----------
JUTAKU_NONE = "ひとり親向けの家賃助成・住宅費給付の専用制度は区公式サイトで確認できず"


def jutaku_view(key, w):
    """住宅欄の表示。scripts/build_hitorioya.py の jutaku_view と同じ判定（正は公開済みツール
    hitorioya-shien-jichitai の表示）。練馬のみ data 上 jutaku.exists=False だが、区独自支援欄の
    「ひとり親家庭転宅支援給付金（上限40万円）」が一時金型なので住宅欄でも同給付金を参照する。
    戻り値: (表示文字列, 住宅支援の記載があるか)"""
    ju = w["jutaku"]
    if key == "nerima":
        d = w["dokuji"][0]
        assert "転宅支援" in d["name"], d["name"]
        return (s(d["name"]) + "（区分上は区独自支援）：" + s(d["kingaku"]), True)
    if not ju.get("exists"):
        return (JUTAKU_NONE, False)
    return (s(ju.get("seido_name")) + "：" + s(ju.get("kingaku")), True)


def pick_hitorioya(name):
    w = H_BY_NAME.get(name)
    if not w:
        return None
    it, ir = w["ikusei_teate"], w["iryo_josei"]
    jutaku_txt, _has = jutaku_view(KEY_BY_NAME[name], w)
    dokuji = [{"name": s(x.get("name")), "kingaku": s(x.get("kingaku"))}
              for x in w.get("dokuji", []) if x.get("name")]
    return {
        "ikusei": yen(it.get("monthly")) if it.get("exists") else NOT_APPLICABLE,
        "ikusei_shogai": yen(it.get("shogai_monthly")),
        "ikusei_shotoku": s(it.get("shotoku_seigen")),
        "iryo_name": s(ir.get("seido_name")),
        "iryo_futan": s(ir.get("futan")),
        "iryo_age": s(ir.get("age_limit")),
        "jutaku": jutaku_txt,
        "dokuji": dokuji,
        "checked": s(w.get("checked")),
    }


def pick_kodomo(key):
    w = K_BY_KEY.get(key)
    if not w:
        return None
    return {
        "age": s(w.get("age_limit")),
        "age_class": s(w.get("age_limit_class")),
        "shotoku": tri(w.get("shotoku_seigen"), "所得制限あり", "所得制限なし") + "（" + s(w.get("shotoku_seigen_note")) + "）",
        "jiko": tri(w.get("jiko_futan"), "一部負担あり", "窓口負担なし") + "（" + s(w.get("jiko_futan_note")) + "）",
        "shokuji": s(w.get("shokuji_ryoyohi")),
        "cert": s(w.get("medical_cert_name")),
    }


def pick_byoji(key):
    w = B_BY_KEY.get(key)
    if not w:
        return None
    if not w.get("byoji_jisshi"):
        return {"fee": NOT_APPLICABLE, "genmen": NA, "jogen": NA, "yoyaku": NA, "taisho": NA}
    return {
        "fee": s(w.get("byoji_fee_label")),
        "genmen": s(w.get("byoji_genmen")),
        "jogen": s(w.get("byoji_jogen")),
        "yoyaku": s(w.get("byoji_yoyaku")),
        "taisho": s(w.get("byoji_taisho")),
    }


def pick_daretsu(key):
    c = D_BY_KEY.get(key)
    if not c:
        return None
    return {
        "cap": s(c.get("cap_label")) if c.get("cap") is not None else "上限時間は公表を確認できず",
        "cap_note": s(c.get("cap_note")),
        "fee": s(c.get("fee")),
        "reserve": s(c.get("reserve")),
        "age": s(c.get("age")),
    }


def pick_sango(key):
    c = S_BY_KEY.get(key)
    if not c:
        return None
    return {
        "stay": s(c.get("stay_label")),
        "day": s(c.get("day_label")) if c.get("day_avail") else NOT_APPLICABLE,
        "visit": s(c.get("visit_label")) if c.get("visit_avail") else NOT_APPLICABLE,
        "limit_stay": s(c.get("limit_stay")),
        "limit_day": s(c.get("limit_day")),
        "limit_visit": s(c.get("limit_visit")),
        "genmen": s(c.get("genmen")),
        "target": s(c.get("target")),
    }


DATA = {}
for key, name in WARD_ORDER:
    DATA[key] = {
        "name": name,
        "hitorioya": pick_hitorioya(name),
        "kodomo": pick_kodomo(key),
        "byoji": pick_byoji(key),
        "daretsu": pick_daretsu(key),
        "sango": pick_sango(key),
    }

# ---------- 集計（本文の主張はすべてここから。手で数字を書かない） ----------
n_wards = len(WARD_ORDER)
n_hit = sum(1 for v in DATA.values() if v["hitorioya"])
n_kod = sum(1 for v in DATA.values() if v["kodomo"])
n_byo = sum(1 for v in DATA.values() if v["byoji"])
n_dar = sum(1 for v in DATA.values() if v["daretsu"])
n_san = sum(1 for v in DATA.values() if v["sango"])
ikusei_vals = sorted(set(w["ikusei_teate"]["monthly"] for w in H.WARDS))
# 住宅支援の記載がある区数。既存ツール（専用制度を確認できなかった区は5区＝18区に記載あり）と同じ数え方
n_jutaku = sum(1 for w in H.WARDS if jutaku_view(KEY_BY_NAME[w["ward"]], w)[1])
assert n_jutaku == 23 - 5, n_jutaku  # 既存ツール hitorioya-shien-jichitai の「確認できなかった区は5区」と一致させる
n_kod_kou = sum(1 for w in K.WARDS if w.get("age_limit_class") == "高校生相当")
n_kod_nofutan = sum(1 for w in K.WARDS if w.get("jiko_futan") is False)
n_kod_shotoku_none = sum(1 for w in K.WARDS if w.get("shotoku_seigen") is False)
byoji_fees = sorted(set(w["byoji_fee"] for w in B.WARDS if w.get("byoji_fee") is not None))
dar_caps = sorted([(c["cap"], c["name"]) for c in D_BY_KEY.values() if c["cap"] is not None], key=lambda x: -x[0])
n_dar_na = sum(1 for c in D_BY_KEY.values() if c["cap"] is None)
n_dar_10 = sum(1 for c in D_BY_KEY.values() if c["cap"] == 10)
n_san_visit_no = sum(1 for c in S_BY_KEY.values() if not c.get("visit_avail"))

CHECKED_TXT = ("ひとり親支援は%s、子ども医療費は%s、病児保育は%s、こども誰でも通園制度は%s、産後ケアは%sに各区の公式ページを確認"
               % (H.CHECKED, K.CHECKED, B.CHECKED, D.CHECKED, S.CHECKED))

TITLE = "23区の子育て支援を比較｜区を選ぶとひとり親手当・医療費助成・病児保育・誰でも通園・産後ケアが1画面【2026年度】"
H1 = "23区の子育て支援を比較｜区を選ぶと5つの制度が1画面に並びます"
DESC = ("東京23区の子育て支援を区ごとに比較できるページです。区を選ぶと、児童育成手当（ひとり親）・子ども医療費助成・病児保育の料金・"
        "こども誰でも通園制度の上限時間・産後ケアの自己負担が1画面に並びます。数字は各区の公式ページを一次確認した5つのデータ"
        "（%s）から取り出しており、記載が無い項目は「情報なし」と表示します。各制度の詳しい比較ツールと記事にもここから移動できます。" % CHECKED_TXT)
OGD = "区を選ぶだけで、ひとり親手当・医療費助成・病児保育・誰でも通園・産後ケアの5制度が1画面に。東京23区の公式ページを一次確認した数字だけを載せています。"

FAQ = [
 ("このページの数字はどこから取っていますか？",
  "東京23区の公式ページを制度ごとに一次確認して作った5つのデータ（%s）から、そのまま取り出しています。区の公式ページに記載が無い項目は推測で埋めず「情報なし」と表示します。各制度の詳細と出典URLは、各ブロックのリンク先（制度別の比較ツール・記事）に載せています。" % CHECKED_TXT),
 ("児童育成手当は区で金額が違いますか？",
  "%sに確認した範囲では、東京23区の児童育成手当（育成手当）は全%d区で月額%sでした。金額そのものより、所得制限の基準額や、区が独自に上乗せしている制度（家賃助成・入学祝金・学習支援など）の有無で差が出ます。" % (H.CHECKED, n_hit, "／".join("{:,}円".format(v) for v in ikusei_vals))),
 ("子ども医療費助成はどの区も高校生まで使えますか？",
  "%sに確認した範囲では、%d区すべてが高校生相当（18歳に達した日以降最初の3月31日まで）を対象にしていました。差が出るのは所得制限（「なし」と明記していたのは%d区）、窓口での一部負担（「負担なし」と確認できたのは%d区）、入院時の食事代を助成するかどうかです。" % (K.CHECKED, n_kod, n_kod_shotoku_none, n_kod_nofutan)),
 ("病児保育の料金はいくらですか？",
  "区の公式ページで確認できた1日あたりの基本料金は%sでした（%s確認）。減免の条件と予約の経路が区ごとに違うので、料金だけでなくその2つも並べて表示しています。" % ("・".join("{:,}円".format(v) for v in byoji_fees), B.CHECKED)),
 ("こども誰でも通園制度の上限時間はどの区が長いですか？",
  "%sに確認した範囲では、%sが%s、%sが%s、%sが%sでした。国基準どおり月10時間の区は%d区、令和8年度の上限時間を公式ページで確認できなかった区が%d区あります（表示にもその旨を出しています）。" % (D.CHECKED, dar_caps[0][1], "最大月%d時間（条件つき）" % dar_caps[0][0] if dar_caps[0][0] >= 100 else "月%d時間" % dar_caps[0][0], dar_caps[1][1], "月%d時間" % dar_caps[1][0], dar_caps[2][1], "月%d時間" % dar_caps[2][0], n_dar_10, n_dar_na)),
 ("保育園の点数（入園指数）も比較できますか？",
  "このページでは比較していません。入園指数の表と園ごとのボーダーは区ごとに別の資料で、23区を同じ基準で並べることができないためです。当サイトで点数計算とボーダー逆引きを用意しているのは練馬区だけで、区の選択で練馬区を選ぶと案内が出ます。ほかの区は各区の入園案内（指数表）でご確認ください。"),
 ("引っ越し先を決めるために使ってよいですか？",
  "制度の有無と数字の比較には使えますが、それだけで決めないでください。同じ制度でも施設の数や空き状況、申込の締切、年度途中の改定はこのページに載っていません。候補の区が絞れたら、各制度のリンク先で出典URLを開き、区の公式ページで最新の内容を確認してください。"),
]

faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}, ensure_ascii=False)
app_ld = json.dumps({"@context": "https://schema.org", "@type": "WebApplication",
    "name": "23区の子育て支援 区選択ハブ", "url": URL, "applicationCategory": "UtilitiesApplication",
    "operatingSystem": "All", "inLanguage": "ja", "description": DESC,
    "datePublished": PUBLISHED, "dateModified": PUBLISHED,
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
    "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": "https://www.noe-match.com/"}}, ensure_ascii=False)
bc_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
    {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": "https://www.noe-match.com/#tools"},
    {"@type": "ListItem", "position": 3, "name": "23区の子育て支援を比較"}]}, ensure_ascii=False)

# CSS供給元は既存の制度ツールと同じ（build_daretsu_navi.py と同じ shell から <style> を取る）
shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
CSS = shell[shell.find("<style>"):shell.find("</style>") + 8]
assert ".table-scroll{" in CSS, "CSS供給元に .table-scroll が無い（8/27の教訓）"

opts = "".join('<option value="%s">%s</option>' % (k, n) for k, n in WARD_ORDER)


def short(v, n=28):
    v = s(v)
    return v if len(v) <= n else v[:n] + "…"


# 静的な23区早見表（JS無しでも読める面）
rows = []
for key, name in WARD_ORDER:
    v = DATA[key]
    rows.append('<tr><td><strong>%s</strong></td><td class="num-cell">%s</td><td>%s</td><td>%s</td><td class="num-cell">%s</td><td>%s</td></tr>' % (
        name,
        v["hitorioya"]["ikusei"] if v["hitorioya"] else NA,
        short(v["kodomo"]["jiko"].split("（")[0]) if v["kodomo"] else NA,
        short(v["byoji"]["fee"], 22) if v["byoji"] else NA,
        short(v["daretsu"]["cap"], 22) if v["daretsu"] else NA,
        short(v["sango"]["stay"], 26) if v["sango"] else NA,
    ))
ROWS = "\n".join(rows)

faq_html = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a) for i, (q, a) in enumerate(FAQ))

INTRO_FACTS = (
    "児童育成手当は全%d区で月額%s（差はほぼ無い）。子ども医療費助成は%d区すべてが高校生相当まで対象で、差が出るのは窓口負担と入院時の食事代。"
    "病児保育の1日あたり基本料金は%s〜%s。こども誰でも通園制度の上限時間は%sの%sから国基準の月10時間まで開いており、産後ケアの宿泊型は区ごとに単価の決め方そのものが違います。"
    % (n_hit, "／".join("{:,}円".format(v) for v in ikusei_vals), n_kod,
       "{:,}円".format(byoji_fees[0]), "{:,}円".format(byoji_fees[-1]),
       dar_caps[0][1], "最大月%d時間（条件つき）" % dar_caps[0][0]))

CHECKED_JS = json.dumps({"hitorioya": H.CHECKED, "kodomo": K.CHECKED, "byoji": B.CHECKED, "daretsu": D.CHECKED, "sango": S.CHECKED}, ensure_ascii=False)
DATA_JS = json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))

TPL = io.open("scripts/_kosodate_hub_body.html", encoding="utf-8").read()
HTML = (TPL.replace("__TITLE__", TITLE).replace("__DESC__", DESC).replace("__OGD__", OGD)
        .replace("__URL__", URL).replace("__H1__", H1).replace("__CSS__", CSS)
        .replace("__FAQLD__", faq_ld).replace("__APPLD__", app_ld).replace("__BCLD__", bc_ld)
        .replace("__OPTS__", opts).replace("__ROWS__", ROWS).replace("__FAQHTML__", faq_html)
        .replace("__INTRO_FACTS__", INTRO_FACTS).replace("__CHECKED_TXT__", CHECKED_TXT)
        .replace("__N_JUTAKU__", str(n_jutaku)).replace("__N_DAR_NA__", str(n_dar_na))
        .replace("__CHECKED_JS__", CHECKED_JS).replace("__DATA__", DATA_JS).replace("__SLUG__", SLUG))
assert "__" not in HTML.replace("__ui", "").replace("__proto", ""), "未置換のプレースホルダが残っている"

# ---------- 禁止語リント（scripts/build_hitorioya.py と同じ型） ----------
# 内部作業メモの語が生成HTMLへ漏れたらビルドを失敗させる。
# 検出したら直すのは pick_* の選ぶ項目（内部フィールドを出さない）。リストを緩めて通さない。
FORBIDDEN = ["検算アンカー", "基準アンカー", "本タスク", "指示の", "WebFetch",
             "本調査", "未取得", "取り込む", "qa_note", "kakunin_dekinakatta"]


def lint(name, content):
    hits = []
    for t in FORBIDDEN:
        i = content.find(t)
        if i >= 0:
            hits.append("%s（…%s…）" % (t, content[max(0, i - 30):i + len(t) + 30].replace("\n", " ")))
    if hits:
        raise SystemExit("禁止語リントFAIL: %s に内部文言が漏れている:\n  %s\n"
                         "→ pick_* で出す項目を見直す（内部フィールドを出さない）" % (name, "\n  ".join(hits)))


def main():
    path = os.path.join("tools", SLUG, "index.html")
    lint(path, HTML)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(HTML)
    print("wrote %s (%d bytes) — 禁止語リントPASS  区%d（ひとり親%d／医療費%d／病児%d／通園%d／産後ケア%d）"
          % (path, len(HTML.encode("utf-8")), n_wards, n_hit, n_kod, n_byo, n_dar, n_san))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
