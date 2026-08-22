# -*- coding: utf-8 -*-
"""Eクラスタ（アプリ実績データ）22本に、結婚率・公表データ早見表への導線を設置する。

2026-08-22の実測: Eは22本中21本にツール導線が無かった（③の脚がゼロ）。
記事ごとに文面を変える（定型文を貼ると広告バナーに見える）。冪等。
位置: 関連リンク直前。
"""
import io, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = "/tools/app-kekkonritsu-data/"
CTA = {
 "with-seriousness-data": ("withが公表していない数字は、他のアプリも公表していないのか", "主要7アプリについて、結婚率・成婚者数・会員数・年齢構成を「公表しているか」で並べた早見表です。アプリを選ぶと出典と確認日つきで表示されます。"),
 "kekkon-madeno-kikan-data": ("期間だけでなく、結婚率も各社は公表していない", "この記事で扱った「公表されていない数字」を、アプリ別に一覧で確認できます。公表している項目が何割あるかも表示します。"),
 "success-rate-data": ("アプリごとの公表状況を、一画面で確認する", "本文で分けた「公表されている数字・されていない数字」を、アプリを選ぶだけで表示する早見表です。"),
 "20s-guide": ("選ぶ前に、そのアプリが何を公表しているかを見る", "20代向けに名前が挙がるアプリが、結婚率や年齢構成を公表しているかを一覧で確認できます。"),
 "appkon-wariai-data": ("全体の13.6%は公的統計。アプリ別の数字は？", "アプリ婚の割合は公的統計にありますが、アプリ別の結婚率は各社非公表です。どのアプリが何を公表しているかを早見表で確認できます。"),
 "student-guide": ("そのアプリは結婚率を公表しているか", "学生・20代向けに挙がるアプリの公表状況を、アプリを選ぶだけで確認できます。"),
 "30s-konkatsu": ("30代向けの比較記事にある「結婚率」の出どころ", "各社が公表している数字と、していない数字をアプリ別に一覧化した早見表です。30代の比率を公表している社がどれだけあるかも分かります。"),
 "tapple-seriousness-data": ("タップル以外のアプリは、何を公表しているか", "主要7アプリの公表状況を同じ項目で並べた早見表です。タップルの非公表項目が他社と比べてどうかが見えます。"),
 "with-nenreiso-data": ("年齢構成を公表しているアプリは何社あるか", "年齢構成・男女比・結婚率の公表状況を7アプリで横断比較できる早見表です。"),
 "time-management": ("時間をかける前に、公表データで候補を絞る", "各アプリが何を公表しているかを一覧で確認してから選ぶと、試す回数が減ります。"),
 "omiai-30s-women-data": ("Omiaiが公表している数字を、他社と並べて見る", "Omiaiの男女比・年齢構成の公表値を、他のアプリの公表状況と同じ項目で比較できる早見表です。"),
 "youbride-seikon-data": ("成婚の実数を公表しているのは、他にあるか", "ユーブライドの成婚退会者数を、主要7アプリの公表状況の中で位置づけて確認できます。"),
 "marrish-saikon-data": ("マリッシュの非公表項目は、他社も非公表か", "結婚率・成婚者数・年齢構成の公表状況を、7アプリ横断で確認できる早見表です。"),
 "40s-guide": ("40代向けに挙がるアプリの公表状況", "年齢構成を公表しているアプリはごく少数です。どの社が何を公表しているかを早見表で確認できます。"),
 "zexy-enmusubi-data": ("終了したサービスの代わりに、いま公表データがあるのはどこか", "現在運営中の主要アプリについて、結婚率・成婚者数・会員数の公表状況を一覧で確認できます。"),
 "success-stories": ("事例の次は、各社の公表データを見る", "体験談は個別の事例です。アプリごとに何が公表されているかを早見表で確認してから選んでください。"),
 "renkatsu-vs-konkatsu": ("恋活・婚活それぞれのアプリが公表している数字", "結婚率・会員数・年齢構成の公表状況をアプリ別に確認できます。婚活向けほど公表が多いとは限りません。"),
 "pairs-marriage-data": ("Pairsの非公表項目を、他社と比べる", "Pairsが公表している数字と、していない数字を、主要7アプリの早見表で横並びにできます。"),
 "pairs-kaiin-data": ("会員数以外に、Pairsは何を公表しているか", "会員数・結婚率・年齢構成・男女比の公表状況を、アプリを選ぶだけで確認できる早見表です。"),
 "late-20s-strategy": ("20代後半で候補に挙がるアプリの公表状況", "各社が結婚率や年齢構成を公表しているかを、一覧で確認できます。"),
 "hatsushon-nenmei-data": ("年齢のデータは公的統計にある。アプリ別は？", "アプリ別の年齢構成は大半が非公表です。どの社が何を公表しているかを早見表で確認できます。"),
 "faq-troubleshooting": ("うまくいかないとき、まず公表データを確認する", "使っているアプリが何を公表しているかを、早見表で確認できます。"),
}
BLOCK = ('<div style="background:#f7f5f2;border:1px solid #e6e2dc;padding:20px 22px;margin:26px 0">'
         '<p style="font-weight:700;margin:0 0 8px">%s</p>'
         '<p style="font-size:.9rem;color:#5a6068;margin:0 0 14px">%s</p>'
         '<a href="' + TOOL + '" style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;padding:12px 28px;text-decoration:none">'
         'アプリ別の公表データ早見表へ →</a>'
         '<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">無料・登録不要。結婚率・成婚者数・会員数・年齢構成・男女比の公表状況を出典つきで表示。</p></div>')

def main():
    n = 0
    for slug, (head, body) in CTA.items():
        p = os.path.join(ROOT, "articles", slug, "index.html")
        if not os.path.exists(p): print("NOT FOUND:", slug); continue
        h = io.open(p, encoding="utf-8").read()
        if TOOL in h: print("SKIP:", slug); continue
        m = re.search(r'<div class="related">', h) or re.search(r'<h2[^>]*>\s*関連記事', h)
        if not m: print("NO related:", slug); continue
        i = m.start()
        io.open(p, "w", encoding="utf-8").write(h[:i] + (BLOCK % (head, body)) + h[i:]); n += 1
    print("added:", n)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8"); main()
