# -*- coding: utf-8 -*-
"""自社商品1号「東京23区 子育て支援 まるごと比較 2026年度版」のドラフトを生成する。

正本: agent/strategy_2026Q4.md「自社商品」節
データ: scripts/_hitorioya_data.py／_kodomo_iryo_data.py／_byoji_funin_data.py／
        _daretsu_data.py／_sangocare_data.py（いずれも正本・手で編集しない）
出力: products/23ku-kosodate-2026/
        index.md            表紙・断り書き・出典と確認日・横断比較表
        NN_<key>.md × 23    区ごとの1ファイル
        _all.md             上記を結合した1本（PDFの元）
        23ku-kosodate-2026.pdf  playwright(Chromium) で組版したPDF
        build_report.txt    リント結果・件数

方針（agent/knowledge.md 2026-08-31 の教訓）
  - 読者向けは note 欄のみ使う。qa_note 欄は読まない（除去）。
  - 「最も」「唯一」などの最上級は手書きせず、全数から機械的に出す（superlative()）。
    データ側の自由記述に最上級が混じっていた場合は、その文を落として件数を報告する。
  - 内部作業メモの語は scripts/build_hitorioya.py の FORBIDDEN をそのまま流用し、
    文単位で落としてから、最終出力に対して同じ lint() を通す（緩めない）。
  - 本文に太字装飾を使わない（見出しのみ）。読者へ語りかける煽り文は書かない。
  - 公開・入稿・push・出品はしない。ローカルにファイルを作るだけ。

生成物は products/ 配下に置く。GitHub Pages のソースと同じリポジトリなので、
push されると公開されてしまう。.gitignore に products/ を入れてある。
"""
import io
import os
import re
import sys
import importlib.util
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "products", "23ku-kosodate-2026")
sys.path.insert(0, os.path.join(BASE, "scripts"))

# 既存の実装を流用（禁止語リスト・lint・住宅支援の型分類・区キー・住宅欄の表示ロジック）
import build_hitorioya as BH  # noqa: E402  (main() は __main__ ガード付きなので副作用なし)

from _hitorioya_data import WARDS as HW, CHECKED as H_CHECKED           # noqa: E402
from _kodomo_iryo_data import WARDS as KW, CHECKED as K_CHECKED, TOKYO_KIJUN  # noqa: E402
from _byoji_funin_data import WARDS as BW, CHECKED as B_CHECKED          # noqa: E402
from _daretsu_data import CITIES as DC, CHECKED as D_CHECKED             # noqa: E402
from _sangocare_data import CITIES as SC, CHECKED as S_CHECKED           # noqa: E402

KEYS = BH.KEYS                       # 区名 -> key
ORDER = [BH.KEYS[w["ward"]] for w in HW]   # 区コード順（ひとり親バンクの並び）
NAME = {v: k for k, v in KEYS.items()}
N = len(ORDER)
assert N == 23

H = {KEYS[w["ward"]]: w for w in HW}
K = {w["key"]: w for w in KW}
B = {w["key"]: w for w in BW}
D = {c["key"]: c for c in DC if c["name"] in KEYS}
S = {c["key"]: c for c in SC if c.get("group") == "東京23区"}
for m in (H, K, B, D, S):
    assert set(m) == set(ORDER), sorted(set(ORDER) ^ set(m))

TITLE = "東京23区 子育て支援 まるごと比較 2026年度版"

# ---------------------------------------------------------------- 文のサニタイズ
# FORBIDDEN は build_hitorioya のものをそのまま使う（リストを緩めない）。
# 商品向けに、内部QAの語と「最上級の手書き」を追加で落とす（厳しくする方向のみ）。
INTERNAL_EXTRA = ["前回調査", "推測を避けて", "修正した", "未精査", "自動取得",
                  "時間の制約", "ばらついた", "null", "jiko_futan", "★",
                  "取得させ", "書き出させ", "全文抽出"]
SUPERLATIVE = ["最も", "唯一", "最大級", "最高級", "一番", "トップクラス", "中でも",
               "23区で最", "23区でも", "23区の中で", "23区内で", "都内で最", "全国で最",
               "一都三県で", "3市で", "3市の中で"]
DROPS = []   # (場所, 理由, 文)


def _sentences(text):
    """「。」で文に分ける。括弧の内側の「。」では切らない（括弧が壊れるのを防ぐ）。"""
    out, buf, depth = [], "", 0
    for ch in text:
        buf += ch
        if ch in "（(「『":
            depth += 1
        elif ch in "）)」』":
            depth = max(0, depth - 1)
        elif ch == "。" and depth == 0:
            out.append(buf)
            buf = ""
    if buf.strip():
        out.append(buf)
    return [p for p in out if p.strip()]


def clean(text, where):
    """自由記述を文単位で検査し、内部メモ・最上級を含む文を落として返す。"""
    if text is None:
        return ""
    text = str(text).strip()
    if not text:
        return ""
    keep = []
    for s in _sentences(text):
        hit = None
        for t in BH.FORBIDDEN:
            if t in s:
                hit = ("禁止語:" + t)
                break
        if hit is None:
            for t in INTERNAL_EXTRA:
                if t in s:
                    hit = ("内部語:" + t)
                    break
        if hit is None:
            for t in SUPERLATIVE:
                if t in s:
                    hit = ("最上級:" + t)
                    break
        if hit:
            DROPS.append((where, hit, s.strip()))
        else:
            keep.append(s)
    return "".join(keep).strip()


def cell(text, where):
    """表のセル用。改行と縦線を潰す。"""
    t = clean(text, where)
    return t.replace("\n", " ").replace("|", "／") if t else "記載なし"


def yen(n):
    return "{:,}円".format(n)


# ---------------------------------------------------------------- 最上級の機械生成
def ranking(values, higher_is_better=True):
    """{key: 数値} -> {key: (順位, 同順位の区数)}。None は対象外。密な順位。"""
    vals = {k: v for k, v in values.items() if v is not None}
    uniq = sorted(set(vals.values()), reverse=higher_is_better)
    rank_of = {v: i + 1 for i, v in enumerate(uniq)}
    cnt = Counter(vals.values())
    return {k: (rank_of[v], cnt[v]) for k, v in vals.items()}, len(vals)


def extreme(values, fmt, label_hi, label_lo):
    """全数から最大・最小を機械的に文にする。同値が複数なら全部並べる。"""
    vals = {k: v for k, v in values.items() if v is not None}
    if not vals:
        return ""
    hi = max(vals.values())
    lo = min(vals.values())
    hi_k = [NAME[k] for k in ORDER if vals.get(k) == hi]
    lo_k = [NAME[k] for k in ORDER if vals.get(k) == lo]
    if hi == lo:
        return "数値を公表している%d区はすべて%s。" % (len(vals), fmt(hi))

    def grp(ks):
        # 同値の区が多いときは区名を列挙せず区数で示す
        return "・".join(ks) if len(ks) <= 8 else "%d区" % len(ks)
    out = "%sは%s（%s）、%sは%s（%s）。" % (label_hi, grp(hi_k), fmt(hi),
                                         label_lo, grp(lo_k), fmt(lo))
    if len(hi_k) == 1:
        out += "%sの%sは23区で1区だけ。" % (fmt(hi), hi_k[0])
    if len(lo_k) == 1:
        out += "%sの%sは23区で1区だけ。" % (fmt(lo), lo_k[0])
    return out


def position(key, values, higher_is_better, unit_fmt, what, none_text="区として数値を公表していない"):
    """区ページ用の位置づけ1行。"""
    ranks, n = ranking(values, higher_is_better)
    if key not in ranks:
        return "%s: %sため順位の対象外（数値のある区は%d区）。" % (what, none_text, n)
    r, tie = ranks[key]
    v = values[key]
    tie_s = "（同じ値が%d区）" % tie if tie > 1 else ""
    direction = "高い順" if higher_is_better else "低い順"
    return "%s: %s。公表%d区のうち%sで%d位%s。" % (what, unit_fmt(v), n, direction, r, tie_s)


# ---------------------------------------------------------------- 各バンクの数値
# 産後ケア: 宿泊型1泊の自己負担（scripts/build_sangocare_navi.py の units_cost/stay_1night と同じ計算）
def units_cost(prices, n):
    if n <= 0:
        return 0
    if not prices:
        return None
    total = 0
    for i in range(1, n + 1):
        p = prices[min(i, len(prices)) - 1]
        if p is None:
            return None
        total += p
    return total


def stay_1night(c):
    if not c["stay_prices"]:
        return None
    return units_cost(c["stay_prices"], 2 if c["stay_unit"] == "day" else 1)


def first(prices):
    return prices[0] if prices else None


V_SHOGAI = {k: H[k]["ikusei_teate"].get("shogai_monthly") for k in ORDER}
V_IKUSEI = {k: H[k]["ikusei_teate"].get("monthly") for k in ORDER}
V_BYOJI = {k: B[k]["byoji_fee"] for k in ORDER}
V_FUNIN = {k: B[k]["funin_jogen_gaku"] for k in ORDER}
V_CAP = {k: D[k]["cap"] for k in ORDER}
V_STAY = {k: stay_1night(S[k]) for k in ORDER}
V_DAY = {k: first(S[k]["day_prices"]) for k in ORDER}
V_VISIT = {k: first(S[k]["visit_prices"]) for k in ORDER}

SHOKUJI_TAISHO = [k for k in ORDER if "対象外" not in K[k]["shokuji_ryoyohi"]]
SHOKUJI_GAI = [k for k in ORDER if "対象外" in K[k]["shokuji_ryoyohi"]]
SEIGEN_NASHI = [k for k in ORDER if K[k]["shotoku_seigen"] is False]
SEIGEN_NONE = [k for k in ORDER if K[k]["shotoku_seigen"] is None]
JIKO_NASHI = [k for k in ORDER if K[k]["jiko_futan"] is False]
JIKO_NONE = [k for k in ORDER if K[k]["jiko_futan"] is None]
FUNIN_JISSHI = [k for k in ORDER if B[k]["funin_jisshi"]]
FUNIN_NASHI = [k for k in ORDER if not B[k]["funin_jisshi"]]
BYOJI_JISSHI = [k for k in ORDER if B[k]["byoji_jisshi"]]
CAP_NONE = [k for k in ORDER if D[k]["cap"] is None]
JUTAKU_TYPE = Counter(BH.TYPE_MAP[k] for k in ORDER)


def names(keys):
    return "・".join(NAME[k] for k in keys) if keys else "なし"


def hours(v):
    return "月%d時間" % v


# ---------------------------------------------------------------- 表紙・断り書き
def cover():
    L = []
    L.append("# %s" % TITLE)
    L.append("")
    L.append("東京23区の子育て支援5制度（ひとり親家庭支援／子ども医療費助成／病児保育・不妊治療助成／"
             "こども誰でも通園制度／産後ケア）を、区ごとに1ページへ束ねた資料です。"
             "数値と条件はすべて各区の公式ページの記述から取り、出典URLと確認日を各項目に付けています。")
    L.append("")
    L.append("## この資料の読み方と断り書き")
    L.append("")
    L.append("- 制度の内容は年度で変わります。申請の前に、各項目に付けた出典URL（区の公式ページ）で必ず再確認してください。")
    L.append("- 本資料は確認日時点の公式ページの記述を整理したものです。制度の適用と最終的な判断は各区が行います。")
    L.append("- 「記載なし」「非公表」は、確認日時点の公式ページ本文にその事項が書かれていなかったことを意味します。制度が無いという意味ではありません。")
    L.append("- 「23区で1区だけ」「高い順で1位」などの比較表現は、収録した数値の全数から機械的に集計したものです。数値を公表していない区は順位の対象外です。")
    L.append("- 金額はすべて自己負担または給付の額面で、税・食事代などの別途費用は各制度の記述に従います。")
    L.append("")
    L.append("## 出典と確認日")
    L.append("")
    L.append("| 制度 | 出典 | 確認日 |")
    L.append("|---|---|---|")
    L.append("| ひとり親家庭支援（児童育成手当・医療費助成・住宅支援・区独自支援） | 各区公式ページ（区ごとに記載） | %s（20区）・2026年8月30日（3区） |" % H_CHECKED)
    L.append("| 子ども医療費助成 | 各区公式ページ（区ごとに記載）・東京都の基準 | %s |" % K_CHECKED)
    L.append("| 病児・病後児保育／不妊治療（先進医療）助成 | 各区公式ページ（区ごとに記載） | %s |" % B_CHECKED)
    L.append("| こども誰でも通園制度 | 各区公式ページ（区ごとに記載） | %s |" % D_CHECKED)
    L.append("| 産後ケア事業 | 各区公式ページ（区ごとに記載） | %s |" % S_CHECKED)
    L.append("")
    L.append("各区の確認日は、その区のページの出典欄に個別に記載しています。")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- 横断比較表
def cross_tables():
    L = []
    L.append("## 横断比較表（23区）")
    L.append("")
    L.append("### 1. ひとり親家庭支援")
    L.append("")
    L.append("| 区 | 児童育成手当（月額/児童1人） | 障害手当（月額） | 医療費助成の負担 | 住宅支援の型 |")
    L.append("|---|---|---|---|---|")
    for k in ORDER:
        w = H[k]
        L.append("| %s | %s | %s | %s | %s |" % (
            NAME[k], yen(w["ikusei_teate"]["monthly"]), yen(w["ikusei_teate"]["shogai_monthly"]),
            BH.med_label(w), BH.TYPE_MAP[k]))
    L.append("")
    L.append("集計: " + extreme(V_IKUSEI, yen, "児童育成手当の月額が高い区", "低い区"))
    L.append("")
    L.append("集計: " + extreme(V_SHOGAI, yen, "障害手当の月額が高い区", "低い区"))
    L.append("")
    L.append("住宅支援の型の内訳（区公式ページの記述にもとづく編集分類）: " +
             "／".join("%s %d区" % (t, c) for t, c in JUTAKU_TYPE.most_common()) + "。")
    L.append("")
    L.append("### 2. 子ども医療費助成")
    L.append("")
    L.append("| 区 | 対象年齢 | 所得制限 | 窓口の一部負担 | 入院時食事療養費 |")
    L.append("|---|---|---|---|---|")
    for k in ORDER:
        w = K[k]
        seigen = "なし" if w["shotoku_seigen"] is False else "記載なし"
        jiko = "なし" if w["jiko_futan"] is False else "記載なし"
        shoku = "対象外" if "対象外" in w["shokuji_ryoyohi"] else "助成対象"
        L.append("| %s | %s | %s | %s | %s |" % (NAME[k], w["age_limit_class"], seigen, jiko, shoku))
    L.append("")
    L.append("集計: 対象年齢は23区すべて「%s」。所得制限なしと明記している区は%d区（%s）、"
             "記載なしは%d区。窓口の一部負担なしと明記している区は%d区、記載なしは%d区（%s）。"
             "入院時食事療養費は%d区が助成対象、%d区が対象外（%s）。" % (
                 K[ORDER[0]]["age_limit_class"], len(SEIGEN_NASHI), names(SEIGEN_NASHI), len(SEIGEN_NONE),
                 len(JIKO_NASHI), len(JIKO_NONE), names(JIKO_NONE),
                 len(SHOKUJI_TAISHO), len(SHOKUJI_GAI), names(SHOKUJI_GAI)))
    L.append("")
    L.append("東京都の基準: %s。%s。%s" % (TOKYO_KIJUN["jiko_futan"], TOKYO_KIJUN["shokuji_ryoyohi"],
                                     clean(TOKYO_KIJUN["note"], "kodomo.TOKYO_KIJUN.note")))
    L.append("")
    L.append("### 3. 病児・病後児保育／不妊治療（先進医療）助成")
    L.append("")
    L.append("| 区 | 病児保育 1日の利用料 | 不妊治療（先進医療）区独自助成 | 上限額 |")
    L.append("|---|---|---|---|")
    for k in ORDER:
        w = B[k]
        fee = yen(w["byoji_fee"]) if w["byoji_fee"] is not None else "非公表"
        fj = "あり" if w["funin_jisshi"] else "区独自助成なし"
        fg = yen(w["funin_jogen_gaku"]) if w["funin_jogen_gaku"] is not None else "—"
        L.append("| %s | %s | %s | %s |" % (NAME[k], fee, fj, fg))
    L.append("")
    mode, mode_n = Counter(v for v in V_BYOJI.values() if v is not None).most_common(1)[0]
    L.append("集計: 病児・病後児保育は%d区が実施。" % len(BYOJI_JISSHI) +
             extreme(V_BYOJI, yen, "1日の利用料が高い区", "低い区") +
             "いちばん多い額は%sで%d区。" % (yen(mode), mode_n))
    L.append("")
    L.append("集計: 不妊治療（先進医療）の区独自助成は%d区にあり、%d区（%s）にはない。" % (
        len(FUNIN_JISSHI), len(FUNIN_NASHI), names(FUNIN_NASHI)) +
             extreme(V_FUNIN, yen, "上限額が高い区", "低い区"))
    L.append("")
    L.append("### 4. こども誰でも通園制度")
    L.append("")
    L.append("| 区 | 月の上限時間 | 利用料 |")
    L.append("|---|---|---|")
    for k in ORDER:
        c = D[k]
        L.append("| %s | %s | %s |" % (NAME[k], cell(c["cap_label"], k + ".daretsu.cap_label"),
                                       cell(c["fee"], k + ".daretsu.fee")))
    L.append("")
    L.append("集計: " + extreme(V_CAP, hours, "月の上限時間が長い区", "短い区") +
             "上限時間を区として公表していないのは%d区（%s）。" % (len(CAP_NONE), names(CAP_NONE)))
    L.append("")
    L.append("### 5. 産後ケア事業")
    L.append("")
    L.append("| 区 | 宿泊型 | 日帰り型 | 訪問型 | 回数上限 |")
    L.append("|---|---|---|---|---|")
    for k in ORDER:
        c = S[k]
        L.append("| %s | %s | %s | %s | %s |" % (
            NAME[k], cell(c["stay_label"], k + ".sango.stay_label"),
            cell(c["day_label"], k + ".sango.day_label"),
            cell(c["visit_label"], k + ".sango.visit_label"),
            limit_cell(c)))
    L.append("")
    L.append("集計（宿泊型1泊＝1泊2日の自己負担。区として単価を公表している区のみ）: " +
             extreme(V_STAY, yen, "高い区", "低い区") +
             "残る%d区は施設ごとに実額が決まり、区としての単価がない。" % sum(1 for v in V_STAY.values() if v is None))
    L.append("")
    L.append("集計（日帰り型1回）: " + extreme(V_DAY, yen, "高い区", "低い区"))
    L.append("")
    L.append("集計（訪問型1回）: " + extreme(V_VISIT, yen, "高い区", "低い区"))
    L.append("")
    return "\n".join(L)


def limit_cell(c):
    parts = []
    for lab, k in (("宿泊", "limit_stay"), ("日帰り", "limit_day"), ("訪問", "limit_visit")):
        v = c[k]
        if v and v != "記載なし":
            parts.append("%s %s" % (lab, cell(v, c["key"] + ".sango." + k)))
    return "／".join(parts) if parts else "非公表"


# ---------------------------------------------------------------- 区ページ
def src_line(label, url, checked):
    return "- %s（%s）  \n  %s" % (label, checked, url)


def ward_page(idx, k):
    nm = NAME[k]
    h, kd, b, d, s = H[k], K[k], B[k], D[k], S[k]
    L = []
    L.append("# %s" % nm)
    L.append("")
    L.append("## 23区での位置づけ（機械集計）")
    L.append("")
    L.append("- " + position(k, V_SHOGAI, True, yen, "ひとり親家庭の障害手当（月額）"))
    L.append("- " + position(k, V_BYOJI, False, yen, "病児保育 1日の利用料"))
    L.append("- " + position(k, V_FUNIN, True, yen, "不妊治療（先進医療）区独自助成の上限額",
                             "区独自助成が区公式ページで確認できない" if not b["funin_jisshi"] else "上限額が非公表の"))
    L.append("- " + position(k, V_CAP, True, hours, "こども誰でも通園制度の月の上限時間",
                             "区として月の上限時間を公表していない"))
    L.append("- " + position(k, V_STAY, False, yen, "産後ケア 宿泊型1泊の自己負担",
                             "施設ごとに実額が決まり区としての単価がない"))
    L.append("- " + position(k, V_VISIT, False, yen, "産後ケア 訪問型1回の自己負担",
                             "区として単価を公表していない" if s["visit_avail"] else "訪問型の実施が区公式ページで確認できない"))
    L.append("- 子ども医療費の入院時食事療養費: %s（助成対象%d区・対象外%d区）。" % (
        "対象外" if k in SHOKUJI_GAI else "助成対象", len(SHOKUJI_TAISHO), len(SHOKUJI_GAI)))
    L.append("")

    # 1. ひとり親
    ik, ir, ju = h["ikusei_teate"], h["iryo_josei"], h["jutaku"]
    hc = BH.checked_jp(h["checked"])
    L.append("## 1. ひとり親家庭支援")
    L.append("")
    L.append("### 児童育成手当")
    L.append("")
    L.append("| 項目 | 内容 |")
    L.append("|---|---|")
    L.append("| 育成手当（児童1人・月額） | %s |" % yen(ik["monthly"]))
    L.append("| 障害手当（月額） | %s |" % yen(ik["shogai_monthly"]))
    L.append("| 所得制限 | %s |" % cell(ik["shotoku_seigen"], k + ".hitorioya.ikusei.shotoku_seigen"))
    note = clean(ik.get("note"), k + ".hitorioya.ikusei.note")
    if note:
        L.append("| 補足 | %s |" % note.replace("\n", " ").replace("|", "／"))
    L.append("")
    L.append("### ひとり親家庭等の医療費助成")
    L.append("")
    L.append("| 項目 | 内容 |")
    L.append("|---|---|")
    L.append("| 制度名 | %s |" % cell(ir["seido_name"], k + ".hitorioya.iryo.seido_name"))
    L.append("| 自己負担 | %s |" % cell(ir["futan"], k + ".hitorioya.iryo.futan"))
    L.append("| 所得制限 | %s |" % cell(ir["shotoku_seigen"], k + ".hitorioya.iryo.shotoku_seigen"))
    L.append("| 対象年齢 | %s |" % cell(ir["age_limit"], k + ".hitorioya.iryo.age_limit"))
    note = clean(ir.get("note"), k + ".hitorioya.iryo.note")
    if note:
        L.append("| 補足 | %s |" % note.replace("\n", " ").replace("|", "／"))
    L.append("")
    L.append("### 住宅支援")
    L.append("")
    sname, snaiyo, ssrc = BH.jutaku_view(h)
    L.append("| 項目 | 内容 |")
    L.append("|---|---|")
    L.append("| 型（編集分類） | %s |" % BH.TYPE_MAP[k])
    L.append("| 制度名 | %s |" % cell(sname, k + ".hitorioya.jutaku.seido_name"))
    L.append("| 内容 | %s |" % cell(snaiyo, k + ".hitorioya.jutaku.kingaku"))
    if ju.get("exists") and ju.get("joken"):
        L.append("| 条件 | %s |" % cell(ju["joken"], k + ".hitorioya.jutaku.joken"))
    note = clean(ju.get("note"), k + ".hitorioya.jutaku.note")
    if note:
        L.append("| 補足 | %s |" % note.replace("\n", " ").replace("|", "／"))
    L.append("")
    L.append("### 区独自の支援（%d件）" % len(h["dokuji"]))
    L.append("")
    L.append("| 制度名 | 概要 | 金額 |")
    L.append("|---|---|---|")
    for dk in h["dokuji"]:
        L.append("| %s | %s | %s |" % (cell(dk["name"], k + ".hitorioya.dokuji.name"),
                                       cell(dk["gaiyo"], k + ".hitorioya.dokuji.gaiyo"),
                                       cell(dk["kingaku"], k + ".hitorioya.dokuji.kingaku")))
    L.append("")
    L.append("出典（確認日）")
    L.append("")
    L.append(src_line(ik["src_label"], ik["src"], hc))
    L.append(src_line(ir["src_label"], ir["src"], hc))
    if ssrc:
        L.append(src_line(ju.get("src_label") or sname or "住宅支援", ssrc, hc))
    for dk in h["dokuji"]:
        if dk.get("src"):
            L.append(src_line(dk["name"], dk["src"], hc))
    L.append("")

    # 2. 子ども医療費
    L.append("## 2. 子ども医療費助成")
    L.append("")
    L.append("| 項目 | 内容 |")
    L.append("|---|---|")
    L.append("| 対象年齢 | %s |" % cell(kd["age_limit"], k + ".kodomo.age_limit"))
    L.append("| 所得制限 | %s |" % ("なし。" if kd["shotoku_seigen"] is False else "") +
             cell(kd["shotoku_seigen_note"], k + ".kodomo.shotoku_seigen_note"))
    L.append("| 窓口の一部負担 | %s |" % ("なし。" if kd["jiko_futan"] is False else "") +
             cell(kd["jiko_futan_note"], k + ".kodomo.jiko_futan_note"))
    L.append("| 入院時食事療養費 | %s |" % cell(kd["shokuji_ryoyohi"], k + ".kodomo.shokuji_ryoyohi"))
    L.append("| 区外・都外で受診したとき | %s |" % cell(kd["kugai"], k + ".kodomo.kugai"))
    L.append("| 申請 | %s |" % cell(kd["apply"], k + ".kodomo.apply"))
    L.append("| 医療証の名称 | %s |" % cell(kd["medical_cert_name"], k + ".kodomo.medical_cert_name"))
    L.append("| 2026年度（令和8年度）の改定 | %s |" % cell(kd["r8_kaitei"], k + ".kodomo.r8_kaitei"))
    note = clean(kd.get("note"), k + ".kodomo.note")
    if note:
        L.append("| 補足 | %s |" % note.replace("\n", " ").replace("|", "／"))
    L.append("")
    L.append("出典（確認日）")
    L.append("")
    L.append(src_line(kd["src_label"], kd["src"], K_CHECKED))
    if kd.get("src2"):
        L.append(src_line(kd["src2_label"] or kd["src2"], kd["src2"], K_CHECKED))
    L.append("")

    # 3. 病児保育・不妊
    L.append("## 3. 病児・病後児保育")
    L.append("")
    L.append("| 項目 | 内容 |")
    L.append("|---|---|")
    L.append("| 実施 | %s |" % ("あり" if b["byoji_jisshi"] else "区公式ページで確認できず"))
    L.append("| 1日の利用料 | %s |" % cell(b["byoji_fee_label"], k + ".byoji.fee_label"))
    L.append("| 減免 | %s |" % cell(b["byoji_genmen"], k + ".byoji.genmen"))
    L.append("| 対象 | %s |" % cell(b["byoji_taisho"], k + ".byoji.taisho"))
    L.append("| 利用上限 | %s |" % cell(b["byoji_jogen"], k + ".byoji.jogen"))
    L.append("| 予約 | %s |" % cell(b["byoji_yoyaku"], k + ".byoji.yoyaku"))
    L.append("")
    L.append("## 4. 不妊治療（先進医療）の区独自助成")
    L.append("")
    L.append("| 項目 | 内容 |")
    L.append("|---|---|")
    L.append("| 区独自助成 | %s |" % ("あり" if b["funin_jisshi"] else "区公式ページで確認できず（東京都の助成のみ）"))
    if b["funin_jisshi"]:
        L.append("| 上限額 | %s |" % (yen(b["funin_jogen_gaku"]) if b["funin_jogen_gaku"] is not None else "非公表"))
        L.append("| 回数 | %s |" % cell(b["funin_jogen_kaisu"], k + ".funin.kaisu"))
        L.append("| 対象 | %s |" % cell(b["funin_taisho"], k + ".funin.taisho"))
        L.append("| 対象となる治療 | %s |" % cell(b["funin_taisho_chiryo"], k + ".funin.chiryo"))
        L.append("| 申請期限 | %s |" % cell(b["funin_shinsei_kigen"], k + ".funin.kigen"))
    note = clean(b.get("note"), k + ".byoji.note")
    if note:
        L.append("| 補足（病児保育・不妊治療） | %s |" % note.replace("\n", " ").replace("|", "／"))
    L.append("")
    L.append("出典（確認日）")
    L.append("")
    L.append(src_line(b["byoji_src_label"], b["byoji_src"], B_CHECKED))
    if b.get("funin_src"):
        L.append(src_line(b["funin_src_label"], b["funin_src"], B_CHECKED))
    L.append("")

    # 5. 誰でも通園
    L.append("## 5. こども誰でも通園制度")
    L.append("")
    L.append("| 項目 | 内容 |")
    L.append("|---|---|")
    L.append("| 月の上限時間 | %s |" % cell(d["cap_label"], k + ".daretsu.cap_label"))
    L.append("| 上限の補足 | %s |" % cell(d["cap_note"], k + ".daretsu.cap_note"))
    L.append("| 利用料 | %s |" % cell(d["fee"], k + ".daretsu.fee"))
    L.append("| その他の費用 | %s |" % cell(d["fee_extra"], k + ".daretsu.fee_extra"))
    L.append("| 予約の流れ | %s |" % cell(d["reserve"], k + ".daretsu.reserve"))
    L.append("| 申請 | %s |" % cell(d["apply"], k + ".daretsu.apply"))
    L.append("| 実施施設 | %s |" % cell(d["facil"], k + ".daretsu.facil"))
    L.append("| 対象年齢 | %s |" % cell(d["age"], k + ".daretsu.age"))
    L.append("")
    L.append("出典（確認日）")
    L.append("")
    L.append(src_line(d["src_label"], d["src"], D_CHECKED))
    L.append("")

    # 6. 産後ケア
    L.append("## 6. 産後ケア事業")
    L.append("")
    L.append("| 項目 | 内容 |")
    L.append("|---|---|")
    L.append("| 宿泊型 | %s |" % cell(s["stay_label"], k + ".sango.stay_label"))
    L.append("| 日帰り型 | %s |" % (cell(s["day_label"], k + ".sango.day_label") if s["day_avail"] else "実施なし（区公式ページで確認できず）"))
    L.append("| 訪問型 | %s |" % (cell(s["visit_label"], k + ".sango.visit_label") if s["visit_avail"] else "実施なし（区公式ページで確認できず）"))
    L.append("| 回数上限 | %s |" % limit_cell(s))
    L.append("| 減免 | %s |" % cell(s["genmen"], k + ".sango.genmen"))
    L.append("| 対象 | %s |" % cell(s["target"], k + ".sango.target"))
    L.append("| 申請 | %s |" % cell(s["apply"], k + ".sango.apply"))
    note = clean(s.get("note"), k + ".sango.note")
    if note:
        L.append("| 補足 | %s |" % note.replace("\n", " ").replace("|", "／"))
    L.append("")
    L.append("出典（確認日）")
    L.append("")
    L.append(src_line(s["src_label"], s["src"], S_CHECKED))
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- 検査
def count_items(md):
    """区ページの項目数＝表の本体行数（見出し行・区切り行を除く）。"""
    n = 0
    for line in md.splitlines():
        if line.startswith("|") and not line.startswith("|---") and not re.match(r"^\|\s*(項目|制度名|区)\s*\|", line):
            n += 1
    return n


def check_style(name, md):
    """太字・語りかけ・最上級の手書きが本文に無いことを機械確認する。"""
    problems = []
    body = "\n".join(l for l in md.splitlines() if not l.startswith("#"))
    if "**" in body:
        problems.append("太字装飾が本文にある")
    for t in ["あなた", "ぜひ", "必見", "お得", "損を", "今すぐ", "見逃"]:
        if t in body:
            problems.append("語りかけ・煽り語: " + t)
    if problems:
        raise SystemExit("体裁チェックFAIL: %s: %s" % (name, "; ".join(problems)))


# ---------------------------------------------------------------- PDF
CSS = """
@page { size: A4; margin: 16mm 14mm 18mm 14mm; }
body { font-family: "Yu Gothic", "Meiryo", "Noto Sans JP", "Hiragino Sans", sans-serif;
       font-size: 10.5pt; line-height: 1.7; color: #1d242b; }
h1 { font-size: 20pt; margin: 0 0 12pt; padding-bottom: 6pt; border-bottom: 2px solid #7c2e42; page-break-before: always; }
h1:first-of-type { page-break-before: auto; }
h2 { font-size: 13.5pt; margin: 18pt 0 8pt; color: #7c2e42; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin: 12pt 0 6pt; page-break-after: avoid; }
p, li { margin: 0 0 6pt; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 10pt; font-size: 9pt; line-height: 1.5;
        page-break-inside: auto; }
th, td { border: 1px solid #c9c4bb; padding: 4pt 6pt; vertical-align: top; word-break: break-all; }
th { background: #f2efe9; text-align: left; white-space: nowrap; }
tr { page-break-inside: avoid; }
td:first-child { white-space: nowrap; }
hr { border: 0; border-top: 1px solid #c9c4bb; margin: 16pt 0; }
a { color: #1d242b; text-decoration: none; }
.cover h1 { page-break-before: auto; font-size: 24pt; border: 0; margin-top: 60pt; }
"""


def build_pdf(all_md, out_pdf):
    """markdown -> HTML(python-markdown) -> PDF(playwright Chromium)。戻り値はページ数。"""
    import markdown
    from playwright.sync_api import sync_playwright
    body = markdown.markdown(all_md, extensions=["tables"])
    # 表紙のh1だけ改ページを入れない
    body = body.replace("<h1>%s</h1>" % TITLE, '<h1 class="cover-title" style="page-break-before:auto;border:0;font-size:24pt;margin-top:60pt">%s</h1>' % TITLE, 1)
    html_doc = ('<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>%s</title>'
                '<style>%s</style></head><body>%s</body></html>' % (TITLE, CSS, body))
    write(os.path.join(OUT, "_all.html"), html_doc)
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page()
        pg.set_content(html_doc, wait_until="load")
        pg.pdf(path=out_pdf, format="A4", print_background=True,
               margin={"top": "16mm", "bottom": "18mm", "left": "14mm", "right": "14mm"},
               display_header_footer=True,
               header_template='<div style="font-size:7pt;color:#8a8f95;width:100%%;padding:0 14mm;">%s</div>' % TITLE,
               footer_template='<div style="font-size:7pt;color:#8a8f95;width:100%;text-align:center;">'
                               '<span class="pageNumber"></span> / <span class="totalPages"></span></div>')
        br.close()
    from pypdf import PdfReader
    return len(PdfReader(out_pdf).pages)


# ---------------------------------------------------------------- 出力
def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    pages = []
    for i, k in enumerate(ORDER, 1):
        pages.append((i, k, ward_page(i, k)))
    index_md = cover() + "\n" + cross_tables() + "\n## 収録している区\n\n" + \
        "\n".join("%d. %s" % (i, NAME[k]) for i, k, _ in pages) + "\n"

    # 最終出力に対する禁止語リント（build_hitorioya.lint をそのまま使う。緩めない）
    files = [("index.md", index_md)]
    for i, k, md in pages:
        files.append(("%02d_%s.md" % (i, k), md))
    for name, md in files:
        BH.lint("products/23ku-kosodate-2026/" + name, md)
        check_style(name, md)

    for name, md in files:
        write(os.path.join(OUT, name), md)
    all_md = "\n\n---\n\n".join(md for _, md in files)
    write(os.path.join(OUT, "_all.md"), all_md)

    # 報告
    R = []
    R.append("build_product_23ku.py 実行結果")
    R.append("生成ファイル: %d（index.md＋区ページ%d）＋_all.md" % (len(files), len(pages)))
    R.append("区ごとの項目数（表の本体行数）:")
    for i, k, md in pages:
        R.append("  %02d %s: %d項目・%d字" % (i, NAME[k], count_items(md), len(md)))
    R.append("文単位で落とした件数: %d" % len(DROPS))
    by = Counter(reason.split(":")[0] for _, reason, _ in DROPS)
    R.append("  内訳: " + "／".join("%s %d" % kv for kv in by.items()))
    for where, reason, s in DROPS:
        R.append("  - [%s] %s: %s" % (reason, where, s[:120]))
    R.append("最終リント（build_hitorioya.FORBIDDEN）: 全%dファイル PASS" % len(files))
    R.append("体裁チェック（太字・語りかけ）: 全%dファイル PASS" % len(files))
    pdf_path = os.path.join(OUT, "23ku-kosodate-2026.pdf")
    try:
        pages_n = build_pdf(all_md, pdf_path)
        R.append("PDF: %s（%dページ・%d bytes）" % (os.path.relpath(pdf_path, BASE), pages_n, os.path.getsize(pdf_path)))
    except Exception as e:  # PDF化できない環境では markdown 結合1本（_all.md）を成果物とする
        R.append("PDF: 生成できず（%s: %s）。_all.md を成果物とする" % (type(e).__name__, e))
    report = "\n".join(R)
    write(os.path.join(OUT, "build_report.txt"), report + "\n")
    sys.stdout.reconfigure(encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
