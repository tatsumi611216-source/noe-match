# -*- coding: utf-8 -*-
"""バンク由来ツールへの結線（2026-08-29・クラスタ編成）

なぜ必要か:
成婚率・相談所費用・アプリ料金のスポーク記事10本が、旧ツール
（app-kekkonritsu-data / soudanjo-simulator）には繋がっているのに、
8/27公開のバンク由来ツールには1本も繋がっていなかった。
唯一クリックが出ている誰でも通園クラスタ（7本接続）に他を寄せる。

書式は既存の記事内ツール導線ボックス（#f7f5f2）と同一。既存リンクは消さない。
挿入位置は既存ボックスの直後＝すでに「道具の並ぶ場所」なので文脈を壊さない。
冪等: 挿入先ツールへのリンクが既にあれば何もしない。
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BOX = ('<div style="background:#f7f5f2;border:1px solid #e6e2dc;padding:20px 22px;margin:26px 0">'
       '<p style="font-weight:700;margin:0 0 8px">%(head)s</p>'
       '<p style="font-size:.9rem;color:#5a6068;margin:0 0 14px">%(body)s</p>'
       '<a href="%(url)s" style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;padding:12px 28px;text-decoration:none">%(cta)s →</a>'
       '<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">無料・登録不要。%(foot)s</p></div>')

SEIKON = dict(
    url="/tools/seikonritsu-hikaku/",
    head="その成婚率、同じ式で計算されていますか",
    body="結婚相談所とアプリ16社の成婚率について、指標の種類・分母・分子・集計期間の4つがそろっているかを判定し、各社の公表文を原文のまま表示します。",
    cta="16社の分母と分子を並べて確認する",
    foot="2社を選ぶと、どの軸がそろっていないかをその場で判定します。")
SOUDANJO = dict(
    url="/tools/soudanjo-hiyou-sim/",
    head="結婚相談所の総額を、同じ条件で積み直す",
    body="活動する月数・お見合いの回数・成婚の有無・相手が連盟会員かどうか。4つを入れると10社の総額を同じ条件で積んで安い順に並べます。12か月・成婚ありで125,400円〜891,000円の7.1倍差でした。",
    cta="10社の総額シミュレーションを使う",
    foot="内訳が色分けバーで出るので、どこにお金がかかるかが見えます。")
APPFEE = dict(
    url="/tools/app-kakin-hikaku/",
    head="同じアプリでも、払う場所で年5,800円変わる",
    body="Web購入とアプリ内購入で料金が違う社があります。期間と決済方法を選ぶと、8社の金額を同じ条件で並べて差額と月あたり単価を出します。",
    cta="アプリ8社の料金差を確認する",
    foot="差額が非公開の社は、推定値を入れずに非公開のまま表示しています。")

# 記事 → (挿入するボックス, 既存の目印＝この直後に入れる)
JOBS = {
 "articles/pairs-marriage-data":   (SEIKON, '/tools/app-kekkonritsu-data/'),
 "articles/with-seriousness-data": (SEIKON, '/tools/app-kekkonritsu-data/'),
 "articles/success-rate-data":     (SEIKON, '/tools/app-kekkonritsu-data/'),
 "articles/youbride-seikon-data":  (SEIKON, '/tools/app-kekkonritsu-data/'),
 "articles/zexy-enmusubi-data":    (SEIKON, '/tools/app-kekkonritsu-data/'),
 # 2026-08-29 第2弾: cluster_audit が検出した成婚率スポークの残り
 "articles/marrish-saikon-data":   (SEIKON, '/tools/app-kekkonritsu-data/'),
 "articles/success-stories":       (SEIKON, '/tools/app-kekkonritsu-data/'),
 "articles/konkatsu-roadmap":      (SEIKON, '/tools/konkatsu-type-shindan/'),
 "articles/soudanjo-hikaku":       (SOUDANJO, '/tools/soudanjo-simulator/'),
 "articles/agency-vs-app":         (SOUDANJO, '/tools/soudanjo-simulator/'),
 "articles/app-plus-agency":       (SOUDANJO, '/tools/soudanjo-simulator/'),
 "articles/compare-price":         (APPFEE, '/tools/app-kekkonritsu-data/'),
 "articles/free-vs-paid":          (APPFEE, '/tools/koisaihi-simulator/'),
}


def main(apply_):
    done = skip = 0
    for path, (box, anchor) in sorted(JOBS.items()):
        f = os.path.join(ROOT, path, "index.html")
        h = io.open(f, encoding="utf-8").read()
        if box["url"] in h:
            print("  済:", path); skip += 1; continue
        i = h.find(anchor)
        if i < 0:
            print("  目印なし:", path, anchor); skip += 1; continue
        # 目印リンクを含むボックス(div)の閉じタグを探す
        j = h.find("</div>", i)
        if j < 0:
            print("  div閉じなし:", path); skip += 1; continue
        ins = j + len("</div>")
        h2 = h[:ins] + BOX % box + h[ins:]
        print("  +%s ← %s" % (box["url"], path))
        if apply_:
            io.open(f, "w", encoding="utf-8").write(h2); done += 1
    print("\n%s: 挿入%d / スキップ%d" % ("適用" if apply_ else "dry-run", done, skip))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main("--apply" in sys.argv)
