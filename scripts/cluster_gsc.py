# -*- coding: utf-8 -*-
"""クラスタ別のGSC実績（正本のABC軸・2026-08-31 新設）

なぜ必要か:
クラスタの状態を聞かれるたびに手で集計していた。軸を取り違える事故も2回起きている
（バンク軸で報告してCEOに訂正された）。**正本は agent/cluster_map.md のA/B/C…軸**なので、
その割付をコードに固定して、いつ実行しても同じ軸で出るようにする。

割付の出どころ: agent/cluster_map.md「## 一覧」「## 詳細」＋「2026-08-27〜29の増援と割付」。
記事を足したらここも足す（cluster_map.md が正本・このファイルは写し）。

実行: python scripts/cluster_gsc.py           # 直近7日 vs 前7日
      python scripts/cluster_gsc.py --days 14 # 窓を変える
"""
import glob
import io
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARC = os.path.join(ROOT, "agent", "gsc_archive")

# --- 正本の割付（agent/cluster_map.md より）--------------------------------
SANGOKEA = """sangokea-higaeri sangokea-houmon sangokea-josei sangokea-moshikomi
sangokea-nankai sangokea-shukuhaku"""

A = """garugaru-ki-guide garugaru-ki-itsumade garugaru-otto-taiou garugaru-nai-hito
garugaru-gibo-jitsubo garugaru-doukyo garugaru-ueno-ko garugaru-otto-genkai
garugaru-sangoutsu-chigai sango-crisis-guide sango-iraira sango-kaji-buntan
sango-otto-kirai sango-rikon sango-satogaeri satogaeri-shinai shinseiji-menkai
maternity-blue-chigai futarime-sango gijikka-ikitakunai ikukyu-fuufu-doji
sango-nukege-itsu-modoru sango-fukeru-taisaku sango-taikei-itsu-modoru
junyuchu-biyou sango-biyou-itsukara"""

B = """dousei-hajimekata shinkon-seikatsu-guide shinkon-koteihi-minaoshi
shinkon-net-kaisen-dandori futari-hikari-kaisen futari-sumaho-minaoshi kazoku-simhikaku
kekkon-hoken-minaoshi futari-kouza-kanri kekkon-chokin-mokuhyou shinkyo-kagu-yosan
kaden-rental-vs-kounyu tomobataraki-shokuji-data kekkon-hiyou-futan futari-kounetsuhi
kakeibo-app-fuufu sengyoshufu-seikatsuhi shinkon-hojokin tokyo-futari-seikatsuhi
dousei-nimotsu-trunkroom keiyaku-jisshitsu-wana kekkon-jutaku-loan yachin-credit-shiharai
fuufu-credit-kanri shinkon-osechi dousei-kekkon-hikaku dousei-kekkon-timing dousei-kaisho"""

C = """soudanjo-hikaku agency-vs-app app-plus-agency app-tsukare-guide konkatsu-roadmap
konkatsu-soudan-saki konkatsu-party-guide nurse-guide nurse-konkatsu-soudanjo
civil-servant-guide engineer-guide otaku-konkatsu pet-konkatsu pocchari-konkatsu
seishain-igai-guide hitomishiri-guide usuge-konkatsu-eikyou over50-guide batsuichi-guide
40s-men 35s-strategy tokyo-guide osaka-guide kyoto-guide soudanjo-hiyou-data"""

CSUB = """nagoya-guide fukuoka-guide sapporo-guide kobe-yokohama-guide saitama-chiba-guide
sendai-hiroshima-guide shizuoka-niigata-guide okinawa-guide inaka-guide kokusai-kekkon-guide"""

D = """matching-app-ranking price-comparison compare-price compare-popular compare-konkatsu
compare-20s omiai-vs-pairs tapple-vs-pairs with-vs-pairs youbride-marrish-hikaku
pairs-guide omiai-guide with-guide tapple-guide youbride-guide marrish-guide
bachelor-date-guide free-vs-paid matching-dansei-cost-data matching-josei-cost-data
members-data age-data kaiin-age-cross-data"""

E = """success-rate-data success-stories appkon-wariai-data pairs-marriage-data
pairs-kaiin-data omiai-30s-women-data tapple-seriousness-data with-seriousness-data
youbride-seikon-data zexy-enmusubi-data marrish-saikon-data kekkon-madeno-kikan-data
hatsushon-nenmei-data renkatsu-vs-konkatsu 20s-guide student-guide late-20s-strategy
30s-konkatsu 40s-guide time-management faq-troubleshooting with-nenreiso-data
omiai-danjohi-data tapple-nenreiso-data pairs-nenreiso-data seikonritsu-data
app-ryokin-data"""

F = """photo-tips profile-photo profile-text konkatsu-photo-guide mens-make-konkatsu
message-strategy line-exchange pairs-men pairs-women with-women women-strategy
first-date-guide first-date-spot date-plan-2kaime ouchi-date-guide ouchi-date-sakuhin
amenohi-date-guide date-sakuhin-ng sakuhin-kachikan enkyori-renai-guide anti-fraud
fraud-detection fraud-statistics safety-guide privacy-protection kekkon-sokou-chousa"""

J = """shikijo-erabi-guide kekkon-okane-data nashikon-data propose-guide konyaku-yubiwa-data
pair-ring-guide christmas-propose-gyakusan yokohama-propose-spot maedori-photo-guide
bridal-esthe-guide bridal-inner-guide kekkonshiki-isho-rental gosyugi-shiharai-houhou
kekkon-uchiiwai-guide kekkon-houkoku-nengajou nyuseki-2027-guide kisei-kekkon-aisatsu
shinkon-ryokou-credit kinsen-kachikan-check"""

L = """rikon-junbi-jyunban rikon-okane-genjitsu koninhiyou-guide tantei-erabikata
uwaki-chousa-kiso tanshin-uwaki-mikiwame"""

M = "kekkon-tenshoku-guide tenshoku-riyu-honne kosodate-zaitaku-guide"
N = "dansei-ninkatsu-guide mitas-formen-kuchikomi mitocore-kuchikomi myseed-kuchikomi"

SEIDO = """daredemo-tsuen-ryokin daredemo-tsuen-yoyaku byoji-hoiku-data kodomo-iryohi-data
funin-josei-data shussan-hiyou-data shussan-ichijikin-data shussan-iryohi-koujo
shussan-mushouka ikukyu-kyufukin-data hitorioya-shien-data
kekkon-shinseikatsu-data"""

# 公的統計だが既存クラスタに帰属が決まっていない3本（2026-08-31に発見）。
# 出産・育休の統計は制度クラスタに入るが、この3本は婚姻・世帯の一般統計で
# 「子育て制度」でも「アプリ実績データ」でもない。**帰属はCEO判断待ち**。
# 暫定で独立表示し、どこかに混ぜて見えなくすることはしない。
TOUKEI = "rikonritsu-data shougai-mikonritsu-data tomobataraki-wariai-data"

# ツールは記事と分けて見る（同じクラスタに属するが役割が違う）
TOOLS = {
    "A":    "garugaru-check fugenbyo-check saigenbyo-check sango-recovery-check sangokea-ryokin",
    "B":    "seikatsuhi-simulator koisaihi-simulator",
    "C":    "konkatsu-type-shindan soudanjo-simulator soudanjo-hiyou-sim",
    "E":    "app-kekkonritsu-data seikonritsu-hikaku app-kakin-hikaku",
    "J":    "kekkon-shikin-keisanki kekkon-yarukoto nyuseki-calendar",
    "L":    "rikongo-seikatsuhi",
    "制度": ("daredemo-tsuen-jichitai byoji-hoiku-ryokin kodomo-iryohi-jichitai "
             "funin-josei-jichitai ikukyu-encho-hantei hoikuen-tensu-nerima "
             "hitorioya-shien-jichitai kekkon-shinseikatsu-jichitai"),
}

ORDER = ["A", "B", "C", "C-sub", "D", "E", "F", "J", "L", "M", "N", "制度", "統計"]
ARTS = {"A": A + " " + SANGOKEA, "B": B, "C": C, "C-sub": CSUB, "D": D, "E": E, "F": F,
        "J": J, "L": L, "M": M, "N": N, "制度": SEIDO, "統計": TOUKEI}


def build_map():
    """slug -> (クラスタ, 種別)。重複所属があれば警告して先勝ちにする。"""
    m, dup = {}, []
    for cl in ORDER:
        for s in ARTS[cl].split():
            if s in m:
                dup.append((s, m[s][0], cl))
            else:
                m[s] = (cl, "記事")
    for cl, ts in TOOLS.items():
        for s in ts.split():
            key = "tool:" + s
            m[key] = (cl, "ツール")
    return m, dup


def load(days, end=None):
    files = sorted(glob.glob(os.path.join(ARC, "*.json")))
    if end:
        files = [f for f in files if os.path.basename(f)[:10] <= end]
    return files[-days:]


def agg(files, m):
    """クラスタ×種別の click/imp と、割付漏れページを返す。"""
    out = defaultdict(lambda: [0, 0])
    per_page = defaultdict(lambda: [0, 0])
    unmapped = defaultdict(lambda: [0, 0])
    for f in files:
        d = json.load(io.open(f, encoding="utf-8"))
        for row in d.get("by_page", []):
            # GSCはアンカー付きURL（/articles/x/#sec-2）を別行で返す。
            # 断片を落として親ページに合算しないと、割付漏れに見えるうえ実績が分散する。
            u = row["p"].split("#")[0].rstrip("/")
            slug = u.rsplit("/", 1)[-1]
            key = ("tool:" + slug) if "/tools/" in u else slug
            hit = m.get(key)
            c, i = row.get("clicks", 0), row.get("imp", 0)
            if hit:
                out[hit][0] += c
                out[hit][1] += i
                per_page[(hit[0], hit[1], slug)][0] += c
                per_page[(hit[0], hit[1], slug)][1] += i
            else:
                unmapped[slug][0] += c
                unmapped[slug][1] += i
    return out, per_page, unmapped


def main():
    days = 7
    if "--days" in sys.argv:
        days = int(sys.argv[sys.argv.index("--days") + 1])
    m, dup = build_map()
    files = sorted(glob.glob(os.path.join(ARC, "*.json")))
    if len(files) < days * 2:
        print("アーカイブが足りない（%d日）" % len(files))
        return
    cur, prev = files[-days:], files[-days * 2:-days]
    c1, pages1, un1 = agg(cur, m)
    c0, _, _ = agg(prev, m)

    def label(fs):
        return "%s〜%s" % (os.path.basename(fs[0])[5:10], os.path.basename(fs[-1])[5:10])

    print("クラスタ別GSC（正本のABC軸）  直近%d日 %s ← 前%d日 %s\n"
          % (days, label(cur), days, label(prev)))
    print("%-6s %-6s %14s %14s   %s" % ("クラスタ", "種別", "click（前）", "表示（前）", "主なページ"))
    tot = [0, 0, 0, 0]
    for cl in ORDER:
        for kind in ("記事", "ツール"):
            k = (cl, kind)
            if k not in c1 and k not in c0:
                continue
            a, b = c1.get(k, [0, 0]), c0.get(k, [0, 0])
            tot[0] += a[0]; tot[1] += a[1]; tot[2] += b[0]; tot[3] += b[1]
            top = sorted([(v[0], v[1], s) for (cc, kk, s), v in pages1.items()
                          if cc == cl and kk == kind], reverse=True)[:2]
            tops = " ".join("%s(c%d/i%d)" % (s, c, i) for c, i, s in top if i)
            print("%-7s %-7s %6d（%3d） %8d（%4d）   %s"
                  % (cl, kind, a[0], b[0], a[1], b[1], tops))
    print("\n%-15s %6d（%3d） %8d（%4d）" % ("合計", tot[0], tot[2], tot[1], tot[3]))
    if un1:
        u = sorted(un1.items(), key=lambda x: -x[1][1])[:8]
        print("\n割付漏れ（cluster_map.mdに無いページ・表示順）:")
        for s, v in u:
            print("   %-34s c%d/i%d" % (s, v[0], v[1]))
    if dup:
        print("\n重複所属（先勝ちで集計）:")
        for s, a, b in dup:
            print("   %s: %s と %s" % (s, a, b))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
