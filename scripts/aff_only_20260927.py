# -*- coding: utf-8 -*-
"""アフィリ単独での収益化への切替（2026-09-27 CEO決定）で、流入上位ページの広告を組み替える

    python scripts/aff_only_20260927.py --dry-run     何が変わるかだけ出す
    python scripts/aff_only_20260927.py --apply       書き込む
    python scripts/aff_only_20260927.py --check       いまの広告の状態（案件・id・PR表記・台帳照合）を出す

何度流しても同じ結果になる（入れた箱は <!-- AFF27:... --> で管理し、無ければ足す／あれば触らない）。
ツールや記事を生成し直すスクリプト（build_kodomo_iryo.py・build_sangocare_navi.py ほか）を流すと
Oisix が戻り、表示計測も消える。**生成し直したら、このスクリプトを --apply し直すこと。**

やること:
  0. 【既存の不具合の修正】制度ツール4本（子ども医療費・誰でも通園・産後ケア・23区比較）は、結果の枠
     （#result）が CSS で非表示のまま一度も表示されていなかった。中にある LINE と広告も見えていなかった。
     class に show を付けて表示する（詳細は transform() のコメント）
  1. 場面に合わない Oisix（制度ツールの結果直後）を外す。保険ランドリー（YMYL枠・台帳で設置先承認済み）は残す
  2. 婚活の記事の末尾（「著者・監修について」の直前。無ければ </article> の直前）に結婚相談所比較ネットを置く
  3. 入籍日カレンダーのハナユメを、本文中から結果の直後（#res の中）へ移す（台帳の「1記事1箇所」を守る）
  4. id の無い広告リンクに id を付け、PR表記の無い広告枠に PR表記を足す
  5. 広告の表示計測（AFF-VIEW）を差し込む:
       広告枠が画面に50%以上入ったら、GA4 に `affv_<linkIdから aff- を除き - を _ にしたもの>` を1回送る
       （例: id="aff-soudanjo" → affv_soudanjo）。1ページ表示につき広告1つあたり1回。
     クリックは GA4 内蔵の click（linkId に <a> の id が入る）で取る。集計は scripts/aff_funnel.py。
     イベント名に linkId を入れるのは、GA4 のカスタムディメンションが未登録のため
     （パラメータで送っても集計できない。agent/knowledge.md 2026-09-04）。
     自社の検品アクセス（?noe_qa=1 を付けて開いたブラウザ）と本番以外のホストでは送らない
     （feat/product-funnel-20260925 の prod23_cta_view と同じ判定）。
     ローカルでの確認用に、送る・送らないに関わらず window.__affv に積む。

台帳（agent/AGENT.md「アフィリエイトリンク台帳」）に無いURLは一切書かない。--check と --apply の最後に
全対象ページの広告URLを台帳と文字列で突き合わせ、1本でも外れていれば止まる。
"""
import argparse
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OISIX = "https://px.a8.net/svt/ejp?a8mat=4B8B4Q+5CWKMY+3RK+2TBJQA"
SOUDANJO = "https://px.a8.net/svt/ejp?a8mat=4B8B4Q+2VLJWA+1PJA+2BJRBL"
HANAYUME = "https://px.a8.net/svt/ejp?a8mat=4B8B4Q+3K0BP6+3DOK+60OXF"
AFF_RE = re.compile(r'<a\b[^>]*href="(https://(?:px\.a8\.net|t\.afi-b\.com)[^"]+)"[^>]*>')

TOOLS = ["tools/kodomo-iryohi-jichitai", "tools/daredemo-tsuen-jichitai", "tools/sangokea-ryokin",
         "tools/hitorioya-shien-jichitai", "tools/kosodate-shien-23ku", "tools/nyuseki-calendar"]

# 婚活記事の末尾に置く結婚相談所比較ネットの導入文（ページの読者の場面に合わせる）
SOUDANJO_LEAD = {
    "articles/with-seriousness-data": "成婚率を公表しているかどうかは、サービスの良し悪しを示すものではありません。アプリを続けながら、月々の費用や担当者による支援の内容まで含めて別の手段とも比べておきたい人には、結婚相談所の資料をまとめて取り寄せる方法があります。",
    "articles/with-guide": "withは恋活と婚活の中間にあるアプリです。結婚までの期限を決めているなら、アプリ以外の手段も費用とサポートの面から並べておくと、自分に合う方法を選びやすくなります。",
    "articles/pairs-marriage-data": "Pairsの成果を示す公表値は、成婚の数ではありません。結婚を前提に進めたいなら、アプリ以外の手段も費用とサポートの面から並べておくと、自分に合う方法を選びやすくなります。",
    "articles/civil-servant-guide": "公務員の相手を探す方法はアプリだけではありません。勤務の不規則さや身バレが気になる場合は、結婚相談所も費用とサポートの面から並べておくと、自分に合う方法を選びやすくなります。",
    "articles/with-nenreiso-data": "年齢層のデータを見て自分の年齢と合わないと感じたら、アプリ以外の手段も費用とサポートの面から並べておくと、自分に合う方法を選びやすくなります。",
    "articles/hatsushon-nenmei-data": "初婚年齢のデータを自分の予定と照らし合わせたあとは、アプリ以外の手段も費用とサポートの面から並べておくと、自分に合う方法を選びやすくなります。",
    "articles/matching-app-ranking": "アプリを比べたあとは、結婚相談所という別の手段も費用とサポートの面から並べておくと、自分に合う方法を選びやすくなります。",
    "articles/compare-popular": "人気アプリを比べたうえで、月々の費用や担当者による支援の内容まで含めて別の手段とも比べておきたい人には、結婚相談所の資料をまとめて取り寄せる方法があります。",
    "articles/members-data": "会員数は累計の数字で、いま活動している人の数ではありません。アプリ以外の手段も費用とサポートの面から並べておくと、自分に合う方法を選びやすくなります。",
}
ARTICLES = list(SOUDANJO_LEAD) + ["articles/pairs-kaiin-data"]
PAGES = TOOLS + ARTICLES

PR_P = '<p style="font-size:.7rem;color:#999;margin:0 0 6px;text-align:left">PR</p>'


def soudanjo_box(lead):
    return ('<!-- AFF27:soudanjo -->\n'
            '<div style="background:#f7f5f2;border:1px solid #e6e2dc;padding:20px 22px;margin:26px 0;text-align:center">\n'
            + PR_P + '\n'
            '<p style="font-weight:700;margin:0 0 10px">アプリと並べて、結婚相談所の料金とサポートも比べておく</p>\n'
            '<p style="font-size:.88rem;color:#5a6068;margin:0 0 14px;line-height:1.9;text-align:left">' + lead +
            '結婚相談所比較ネットは、複数の相談所の資料をまとめて無料で請求できる一括比較サービスです。</p>\n'
            '<a id="aff-soudanjo" href="' + SOUDANJO + '" rel="nofollow sponsored noopener" target="_blank" '
            'style="display:inline-block;background:#7c5cbf;color:#fff;font-weight:700;padding:13px 32px;text-decoration:none">'
            '結婚相談所の資料を無料で比較する</a>\n'
            '<p style="font-size:.74rem;color:#888;margin:10px 0 0">料金・対応エリア・入会条件は相談所ごとに異なります。詳細は公式サイトでご確認ください</p>\n'
            '</div>\n<!-- /AFF27:soudanjo -->\n')


HANAYUME_BOX = (
    '<!-- AFF27:hanayume -->\n'
    '<div style="background:#f7f5f2;border:1px solid #e6e2dc;padding:20px 22px;margin:22px 0;text-align:center">'
    + PR_P +
    '<p style="font-weight:700;margin:0 0 10px">候補日が出たら、その日に空いている会場を探す</p>'
    '<p style="font-size:.88rem;color:#5a6068;margin:0 0 14px;text-align:left;line-height:1.9">暦の評価が高い日は会場も埋まりやすくなります。入籍日と式や食事会を同じ日にしたい場合は、候補日が決まった段階で空き状況を確認しておくと、日程から選び直す手間を避けられます。</p>'
    '<a id="aff-hanayume" href="' + HANAYUME + '" rel="nofollow sponsored noopener" target="_blank" '
    'style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;padding:13px 22px;text-decoration:none">ハナユメで会場の空きを見る</a>'
    '<p style="font-size:.74rem;color:#888;margin:10px 0 0">特典の金額・適用条件・対象会場は時期により変わります。必ず公式サイトでご確認ください</p></div>\n'
    '<!-- /AFF27:hanayume -->\n')

GATE_JS = ("var h=location.hostname,ok=(h==='www.noe-match.com'||h==='noe-match.com');"
           "try{var m=/[?&]noe_qa=(0|1)/.exec(location.search);if(m)localStorage.setItem('noe_qa',m[1]);"
           "if(localStorage.getItem('noe_qa')==='1')ok=false;}catch(e){}")
VIEW_START, VIEW_END = "<!-- AFF-VIEW -->", "<!-- /AFF-VIEW -->"
VIEW_JS = (VIEW_START + "\n<script>(function(){" + GATE_JS +
           "var as=document.querySelectorAll('a[id^=\"aff-\"][rel~=\"sponsored\"]');"
           "if(!as.length||!('IntersectionObserver' in window))return;"
           "var io=new IntersectionObserver(function(es){es.forEach(function(x){if(!x.isIntersecting)return;"
           "io.unobserve(x.target);var n='affv_'+x.target.getAttribute('data-aff').slice(4).replace(/-/g,'_');"
           "(window.__affv=window.__affv||[]).push(n);if(ok){try{gtag('event',n);}catch(e){}}});},{threshold:[0.5]});"
           "for(var i=0;i<as.length;i++){var a=as[i],b=a.closest('div,section,aside');"
           "if(!b||b.getElementsByTagName('a').length>2)b=a;"
           "b.setAttribute('data-aff',a.id);io.observe(b);}})();</script>\n" + VIEW_END + "\n")
VIEW_RE = re.compile(re.escape(VIEW_START) + r".*?" + re.escape(VIEW_END) + r"\n?", re.S)


def ledger():
    led = {}
    for line in io.open(os.path.join(ROOT, "agent", "AGENT.md"), encoding="utf-8"):
        m = re.match(r'\|\s*([^|]+?)\s*\|\s*(https://(?:px\.a8\.net|t\.afi-b\.com)\S+)\s*\|', line)
        if m:
            led[m.group(2)] = m.group(1)
    return led


def block_around(s, i, opener):
    """位置 i を含む、opener で始まる div を返す（中に div が入れ子になっていないことを確かめる）"""
    a = s.rfind(opener, 0, i)
    b = s.find("</div>", i) + len("</div>")
    seg = s[a:b]
    assert a >= 0 and seg.count("<div") == 1, "広告枠を1つに切り出せない"
    assert "PR" in seg, "PR表記の無い枠を切り出しかけた"
    return a, b


def remove_oisix(s):
    i = s.find(OISIX)
    if i < 0:
        return s, None
    a, b = block_around(s, i, '<div ')
    # 直前の空行も落とす
    a2 = a - 2 if s[a - 2:a] == "\n\n" else a
    return s[:a2] + s[b:], "Oisix を外した"


def add_ids(s, page):
    """id の無い広告リンクに id を付ける（案件名ベース・同一ページで重複しない）"""
    led = ledger()
    base = {"ユーブライド（afb）": "aff-youbride", "ハナユメ（A8）": "aff-hanayume"}
    used = set(re.findall(r'\bid="(aff-[^"]+)"', s))
    notes = []

    def fix(m):
        tag, url = m.group(0), m.group(1).replace("&amp;", "&")
        if re.search(r'\bid="', tag):
            return tag
        stem = base[led[url]]
        n, lid = 1, stem
        while lid in used:
            n += 1
            lid = "%s-%d" % (stem, n)
        used.add(lid)
        notes.append("id=%s を付けた" % lid)
        return re.sub(r"^<a\s+", '<a id="%s" ' % lid, tag)
    return AFF_RE.sub(fix, s), notes


INLINE_PR = '<span style="font-size:.72rem;color:#999">（PR）</span>'


def add_inline_pr(s):
    """本文中のテキストリンク（広告枠の外）で PR 表記が無いものは、リンク直後に（PR）を足す"""
    notes, out, prev, last = [], [], 0, 0
    for m in AFF_RE.finditer(s):
        win = s[max(prev, m.start() - 1200):m.start()]
        end = s.find("</a>", m.end()) + len("</a>")
        prev = end
        if re.search(r">PR<|【PR】", win) or s.startswith(INLINE_PR, end):
            continue
        out.append(s[last:end] + INLINE_PR)
        last = end
        notes.append("本文中リンク %s の直後に（PR）を足した" % (re.search(r'id="([^"]+)"', m.group(0)) or [None, "-"])[1])
    out.append(s[last:])
    return "".join(out), notes


def ensure_view(s):
    base = VIEW_RE.sub("", s)
    assert base.count("</body>") == 1
    return base.replace("</body>", VIEW_JS + "</body>", 1)


def transform(page, s):
    notes = []
    if page in TOOLS[:5]:
        s, n = remove_oisix(s)
        if n:
            notes.append(n)
        # 【既存の不具合】共通シェルの CSS は .result{display:none} / .result.show{display:block} だが、
        # この4本のスクリプトは show を付けないため、結果・LINE・広告の枠が本番で一度も表示されていなかった
        # （2026-09-27 に本番で実機確認。ボタンを押しても #result は display:none のまま）。
        # 結果は読み込み時にも既定値で描かれる作りなので、最初から show を付けて表示する。
        js = "".join(re.findall(r"<script[^>]*>(.*?)</script>", s, re.S))
        tag = '<div class="result" id="result"'
        if tag in s and "show" not in js:
            s = s.replace(tag, '<div class="result show" id="result"', 1)
            notes.append("結果の枠が表示されていなかった不具合を直した（class に show）")
    if page == "tools/nyuseki-calendar" and "<!-- AFF27:hanayume -->" not in s:
        i = s.find(HANAYUME)
        a, b = block_around(s, i, '<div style="background:#f7f5f2;border:1px solid #e6e2dc;padding:20px 22px;margin:26px 0;text-align:center">')
        s = s[:a] + s[b:].lstrip("\n")
        anchor = "\n  <h3>次に読むと早いページ</h3>"
        assert s.count(anchor) == 1
        s = s.replace(anchor, "\n" + HANAYUME_BOX + anchor, 1)
        notes.append("ハナユメを本文中から結果の直後（#res）へ移した")
    if page in SOUDANJO_LEAD and "<!-- AFF27:soudanjo -->" not in s:
        m = re.search(r'<h2[^>]*>著者・監修について</h2>', s)
        pos = m.start() if m else s.find("</article>")
        assert pos > 0
        s = s[:pos] + soudanjo_box(SOUDANJO_LEAD[page]) + s[pos:]
        notes.append("末尾に結婚相談所比較ネットを置いた")
    if page == "articles/compare-popular":
        # 同じ表の直後にユーブライドが2つ続いていた（550字差）。後ろの cta-mid を外す
        m = re.search(r'<div class="cta-mid">\n<span class="cta-mid-pr">PR</span>\n<p class="cta-mid-t">[^<]*</p>\n'
                      r'<a id="aff-youbride-2" [^>]*>[^<]*</a>\n</div>\n', s)
        if m:
            s = s[:m.start()] + s[m.end():]
            notes.append("隣接していたユーブライドの2つ目を外した")
    if page == "articles/pairs-kaiin-data":
        # 当サイトは「成婚率は各社で定義が違い比較に使えない」と結論しているため、広告文から成婚率を外す
        old1, new1 = "結婚相談所の料金・成婚率を一括比較", "結婚相談所の料金・サポートを一括比較"
        old2, new2 = "各社の料金・成婚率・特徴を無料で比較できる。", "各社の料金・サポート内容・特徴を無料で比較できる。"
        if old1 in s:
            s = s.replace(old1, new1, 1).replace(old2, new2, 1)
            notes.append("相談所の広告文から「成婚率」を外した")
    if page == "articles/hatsushon-nenmei-data":
        old = "30代の婚活なら、成婚実績のある婚活特化アプリを選ぶのが近道"
        if old in s:
            s = s.replace(old, "30代の婚活なら、成婚実績を公表している婚活特化アプリも候補に", 1)
            notes.append("ユーブライド枠の見出しから「近道」を外した")
    if page == "articles/with-nenreiso-data":
        old = '<div class="cta-foot">\n<h2>真剣交際・婚活ならユーブライドも検討を</h2>'
        if old in s:
            s = s.replace(old, '<div class="cta-foot">\n' + PR_P + '\n<h2>真剣交際・婚活ならユーブライドも検討を</h2>', 1)
            notes.append("末尾のユーブライド枠にPR表記を足した")
    s, n = add_ids(s, page)
    notes += n
    s, n = add_inline_pr(s)
    notes += n
    s = ensure_view(s)
    return s, notes


def inventory(page, s, led):
    out = []
    prev = 0
    for m in AFF_RE.finditer(s):
        url = m.group(1).replace("&amp;", "&")
        i = re.search(r'\bid="([^"]+)"', m.group(0))
        # 広告枠の中（直前の広告より後・リンクの手前1,200字以内）に PR 表記があるか
        win = s[max(prev, m.start() - 1200):m.start()]
        end = s.find("</a>", m.end()) + len("</a>")
        pr = bool(re.search(r">PR<|【PR】", win)) or s.startswith(INLINE_PR, end)
        prev = end
        out.append((i.group(1) if i else "", led.get(url), pr, round(100.0 * m.start() / len(s))))
    return out


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    g.add_argument("--check", action="store_true")
    a = ap.parse_args()
    led = ledger()
    bad = 0
    for page in PAGES:
        if a.check:
            print(page)
        p = os.path.join(ROOT, page, "index.html")
        s = io.open(p, encoding="utf-8").read()
        if not a.check:
            new, notes = transform(page, s)
            print("%-42s %s" % (page, "／".join(notes) if notes else ("表示計測のみ" if new != s else "変更なし")))
            if a.apply and new != s:
                io.open(p, "w", encoding="utf-8", newline="").write(new)
            s = new
        inv = inventory(page, s, led)
        for lid, name, pr, pct in inv:
            flag = []
            if not name:
                flag.append("台帳外")
            if not lid.startswith("aff-"):
                flag.append("idなし")
            if not pr:
                flag.append("PR表記なし")
            bad += bool(flag)
            print("    %-18s %-28s 位置%3d%% %s" % (lid or "-", name or "!!", pct, " ".join(flag)))
        ids = [x[0] for x in inv]
        if len(ids) != len(set(ids)):
            print("    !! id が重複"); bad += 1
        if len(inv) > 3:
            print("    !! 広告が%d箇所（上限3）" % len(inv)); bad += 1
        if VIEW_START not in s:
            print("    （表示計測なし）")
    if bad:
        raise SystemExit("NG: %d件" % bad)
    print("OK: 全広告が台帳のURLと一致・id付き・PR表記あり・1ページ3箇所以内")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
