# -*- coding: utf-8 -*-
"""GSCでクリックが実際に出ている記事にLINE@導線を設置する（2026-08-26）。

なぜ必要か: 8/26のアクセス分析で、実クリックが出ている21記事のうち18本に
LINE導線が無いことが分かった。読者が実際に来ている場所に受け皿が無い状態。
クラスタA（産後）22本への設置（add_line_cta.py）と同じ形式・同じ挿入位置で、
文面だけ各記事の主題に合わせる。冪等: lin.ee が既にある記事は触らない。
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLOCK = """
<!-- LINE-CTA -->
<section id="line-cta" style="max-width:680px;margin:56px auto 64px;padding:36px 28px;background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;">
  <p style="margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif;">NOE OFFICIAL LINE</p>
  <p style="margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5;">%(head)s</p>
  <p style="margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;">婚活から結婚準備・産後までを扱う「NOE結婚設計室」の公式LINEです。<br>%(body)s</p>
  <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{gtag('event','line_add_click',{article:'%(slug)s'});}catch(e){}"
     style="display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;font-size:15px;font-weight:600;text-decoration:none;">友だち追加して受け取る</a>
  <p style="margin:14px 0 0;font-size:11px;color:#8a8f95;">登録は無料です。いつでも解除できます。</p>
</section>
"""

TARGETS = {
    "kyoto-guide": (
        "京都での出会いに効くFACTを、週1回",
        "アプリ選びから会うまでの段取りを短文で届けます。判断に迷ったら、追加後そのままトークでご相談ください。"),
    "okinawa-guide": (
        "沖縄での出会いに効くFACTを、週1回",
        "アプリ選びから会うまでの段取りを短文で届けます。判断に迷ったら、追加後そのままトークでご相談ください。"),
    "sapporo-guide": (
        "札幌での出会いに効くFACTを、週1回",
        "アプリ選びから会うまでの段取りを短文で届けます。判断に迷ったら、追加後そのままトークでご相談ください。"),
    "civil-servant-guide": (
        "公務員の婚活を、身バレさせずに進める",
        "職業を活かすプロフィールと安全設定の実務を、週1回・短文で。個別の相談も、追加後そのままトークでどうぞ。"),
    "with-seriousness-data": (
        "公表データで選ぶ婚活を、週1回の短文で",
        "アプリ各社の公表値と非公表の見分け方を届けます。どれを選ぶか迷ったら、トークでご相談ください。"),
    "tapple-seriousness-data": (
        "公表データで選ぶ婚活を、週1回の短文で",
        "アプリ各社の公表値と非公表の見分け方を届けます。どれを選ぶか迷ったら、トークでご相談ください。"),
    "appkon-wariai-data": (
        "アプリ婚の実像を、統計の一次データで",
        "公的統計と各社公表値の読み方を、週1回・短文で届けます。気になることは、追加後そのままトークでどうぞ。"),
    "youbride-seikon-data": (
        "公表データで選ぶ婚活を、週1回の短文で",
        "アプリ各社の公表値と非公表の見分け方を届けます。どれを選ぶか迷ったら、トークでご相談ください。"),
    "kekkon-madeno-kikan-data": (
        "出会いから結婚までの段取りを、週1回",
        "交際期間の統計と、期間を縮める実務を短文で届けます。いまの進め方の相談も、トークでどうぞ。"),
    "bachelor-date-guide": (
        "デート型アプリの使いどころを、週1回",
        "審査制・デート型の向き不向きと併用の設計を短文で。判断に迷ったら、追加後そのままトークでご相談ください。"),
    "christmas-propose-gyakusan": (
        "プロポーズの逆算を、週1回の材料で",
        "指輪・場所・日取りの段取りを短文で届けます。準備の相談も、追加後そのままトークでどうぞ。"),
    "futari-sumaho-minaoshi": (
        "ふたりの固定費見直しを、週1回の材料で",
        "通信費・保険・住まいの見直し順を短文で届けます。家計の相談も、追加後そのままトークでどうぞ。"),
    "konkatsu-roadmap": (
        "婚活の全体設計を、週1回の短文で",
        "手段の選び方から成婚までの段取りを届けます。いまの立ち位置の相談も、トークでどうぞ。"),
    "matching-app-ranking": (
        "アプリ選びの判断材料を、週1回",
        "ランキングの裏にある公表値と選び方の軸を短文で。どれにするか迷ったら、トークでご相談ください。"),
    "mitas-formen-kuchikomi": (
        "妊活まわりの制度とお金のFACTを、週1回",
        "公的助成・検査・生活の整え方を短文で届けます。気になることは、追加後そのままトークでどうぞ。"),
    "tenshoku-riyu-honne": (
        "結婚と働き方の両立を、週1回の材料で",
        "結婚を機の転職・家計の設計を短文で届けます。個別の相談も、追加後そのままトークでどうぞ。"),
    "time-management": (
        "忙しくても回る婚活の設計を、週1回",
        "時間の使い方と手段の絞り方を短文で届けます。進め方の相談も、追加後そのままトークでどうぞ。"),
    "omiai-guide": (
        "Omiaiの使いどころを、公表データで",
        "アプリ各社の公表値と選び方の軸を週1回・短文で。どれにするか迷ったら、トークでご相談ください。"),
}


def main():
    added, skipped = 0, 0
    for slug, (head, body) in TARGETS.items():
        p = os.path.join(ROOT, "articles", slug, "index.html")
        if not os.path.exists(p):
            print("NOT FOUND:", slug)
            continue
        h = io.open(p, encoding="utf-8").read()
        if "lin.ee/unbDsCR" in h:
            print("skip(設置済み):", slug)
            skipped += 1
            continue
        i = h.find("<footer>")
        if i < 0:
            print("NO footer:", slug)
            continue
        block = BLOCK % {"head": head, "body": body, "slug": slug}
        io.open(p, "w", encoding="utf-8").write(h[:i] + block + h[i:])
        print("added:", slug)
        added += 1
    print(f"設置 {added}本 / スキップ {skipped}本")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
