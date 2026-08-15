# -*- coding: utf-8 -*-
"""クラスタA（ガルガル／産後）の記事にLINE@導線を差し込む。

なぜ必要か（2026-08-15）:

このクラスタは「集客メイン＋キャッシュ回収」で、主KPIはLINE@登録数。
ところが実地監査の結果、**LINE導線はツールページにしか無く、記事3本からは
LINE@に繋がっていなかった**。集客装置の主KPIへの導線が欠けている状態だった。

GA4イベントは `line_add_click` で統一し、`article` パラメータで設置元を区別する
（ツール側は `tool` パラメータを使っているため、記事とツールの寄与を分けて見られる）。

冪等：既に line-cta がある場合は何もしない。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLOCK = """
<!-- LINE-CTA -->
<section id="line-cta" style="max-width:680px;margin:56px auto 64px;padding:36px 28px;background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;">
  <p style="margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif;">NOE OFFICIAL LINE</p>
  <p style="margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5;">%(head)s</p>
  <p style="margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;">%(body)s</p>
  <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{gtag('event','line_add_click',{article:'%(slug)s'});}catch(e){}"
     style="display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;font-size:15px;font-weight:600;text-decoration:none;">友だち追加して受け取る</a>
  <p style="margin:14px 0 0;font-size:11px;color:#8a8f95;">登録は無料・配信は週1回だけ。いつでも解除できます。</p>
</section>
"""

TARGETS = {
    "articles/garugaru-ki-guide": (
        "産後にもう一度もめないための備えを、LINEで",
        "ガルガル期の対処と産後の段取りを、週1回・短文で届けます。<br>個別の相談も、追加後そのままトークでどうぞ。"),
    "articles/garugaru-ki-itsumade": (
        "「いつまで」を短くする設計を、LINEで",
        "産後の睡眠・分担・支援の整え方を、週1回・短文で届けます。<br>いま何から動くか迷ったら、トークで相談できます。"),
    "articles/sango-crisis-guide": (
        "産後の夫婦運用に効くFACTを、LINEで",
        "感情論ではなく設計で考えるための材料を、週1回・短文で。<br>気になることの相談も、追加後そのままトークでどうぞ。"),
    "articles/garugaru-gibo-jitsubo": (
        "親との調整を、こじれる前に設計する",
        "産後の訪問・助言・写真の扱いを、週1回・短文で届けます。<br>個別の相談も、追加後そのままトークでどうぞ。"),
    "articles/garugaru-otto-taiou": (
        "夫の「担当」を、週1回の材料で固める",
        "産後の分担・親との調整の具体策を短文で届けます。<br>個別の相談も、追加後そのままトークでどうぞ。"),
    "articles/garugaru-otto-genkai": (
        "限界の手前で、条件から立て直す",
        "睡眠・総量削減・担当固定の順で整える材料を週1回。<br>気になることの相談も、追加後そのままトークでどうぞ。"),
    "articles/sango-otto-kirai": (
        "「警戒」か「冷え」かを見分ける材料を、週1回",
        "打つ手が変わるので、切り分けから。短文で届けます。<br>個別の相談も、追加後そのままトークでどうぞ。"),
    "articles/gijikka-ikitakunai": (
        "義実家の調整を、こじれる前に決めておく",
        "訪問の断り方と条件の決め方を、週1回・短文で届けます。<br>個別の相談も、追加後そのままトークでどうぞ。"),
    "articles/garugaru-doukyo": (
        "同居の産後は、境界づくりが先手になる",
        "部屋・時間・役割の区切り方を、週1回・短文で。<br>気になることの相談も、追加後そのままトークでどうぞ。"),
    "articles/shinseiji-menkai": (
        "面会の方針は、産前に決めておくと楽になる",
        "時期・人数・お願いの仕方を、週1回・短文で届けます。<br>個別の相談も、追加後そのままトークでどうぞ。"),
    "articles/sango-satogaeri": (
        "里帰り明けの段差に、先に人を配置する",
        "戻る日の備えと、産後の分担の作り方を週1回・短文で。<br>気になることの相談も、追加後そのままトークでどうぞ。"),
    "articles/garugaru-nai-hito": (
        "環境が変わる前に、崩れる箇所を見ておく",
        "里帰り明け・復職・二人目——条件が変わる前の点検材料を週1回。<br>気になることの相談も、追加後そのままトークでどうぞ。"),
}


def main():
    for slug, (head, body) in TARGETS.items():
        p = os.path.join(ROOT, slug, "index.html")
        h = open(p, encoding="utf-8").read()
        if "line-cta" in h:
            print("SKIP (already has LINE CTA):", slug)
            continue
        i = h.rfind("<footer")
        if i < 0:
            print("NO FOOTER:", slug)
            continue
        block = BLOCK % dict(head=head, body=body, slug=slug.split("/")[-1])
        open(p, "w", encoding="utf-8").write(h[:i] + block + h[i:])
        print("added:", slug)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
