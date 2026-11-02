"""結果画面の2部品（30日計画W2・T-132）。

1. 有料レポートの関心ボタン（準備中・課金なし）: 押すと GA4 `paid_report_interest` を1結果につき1回送る。
   決済・申込の導線は持たない。関心率 = paid_report_interest ÷ 結果表示（uranai_complete / tool_result）。
2. 「次の1本」: 関連する診断かゲームへのリンクを1つだけ。押すと GA4 `next_pick_click`。

対象は aisho-uranai・suhi-kekkon-uranai・konkatsu-type-shindan の3本だけ（計画 5章A）。
build_uranai_tools.py（aisho・suhi）と apply_paid_report_blocks.py（3本の既存HTMLへの挿入）から使う。
"""

LINE_URL = 'https://lin.ee/unbDsCR'
MARK = 'data-t132="1"'  # 挿入済みの目印（二重挿入を防ぐ）

CONFIG = {
    'aisho-uranai': {
        'what': '二人の相性タイプの詳しい説明と、二人で話すための問いのリスト',
        'pick': ('/tools/en-to-un/', 'en-to-un', '縁と運｜7代の結婚相手を選ぶ家系ゲーム',
                 '相性を見たあとは、息抜きにゲームを。結婚相手を選んで家系をつなぎ、最後に「自分で決めた回数」と「運が決めた回数」が出ます。無料・登録不要。'),
    },
    'suhi-kekkon-uranai': {
        'what': 'あなたの結婚観の詳しい説明と、パートナーと話すための問いのリスト',
        'pick': ('/tools/aisho-uranai/', 'aisho-uranai', '生年月日でみる二人の相性占い',
                 'お相手の生年月日がわかれば、二人の相性タイプと、すれ違いやすい点・話し方のヒントも見られます。無料・入力は送信しません。'),
    },
    'konkatsu-type-shindan': {
        'what': '結果に合わせた進め方の詳しい説明と、サービスを選ぶときに確かめたい問いのリスト',
        'pick': ('/tools/renai-type-shindan/', 'renai-type-shindan', '16タイプ恋愛診断',
                 '進め方の次は、自分の恋愛の傾向を。12問に答えると、恋の強みと気をつけたいことがわかります。無料・入力は送信しません。'),
    },
}

CSS = """<style>
.rpt{border:1px dashed #cdbfae;background:#fff;padding:16px 18px;margin:22px 0 0;text-align:center}
.rpt .rpt-h{font-weight:700;font-size:.95rem;margin:0 0 6px;color:#1d242b;text-align:left}
.rpt .rpt-p{font-size:.86rem;color:#5a6068;margin:0 0 12px;text-align:left;line-height:1.8}
.rpt .rpt-btn{background:#fff;color:#7c2e42;border:1.5px solid #7c2e42;font-weight:700;padding:11px 22px;font-size:.92rem;cursor:pointer;max-width:100%;font-family:inherit}
.rpt .rpt-btn:disabled{color:#8a8f95;border-color:#c9c4bc;cursor:default}
.rpt .rpt-done{font-size:.86rem;color:#1d242b;background:#f7f5f2;padding:10px 12px;margin:12px 0 0;text-align:left;line-height:1.8}
.rpt .rpt-done a{color:#7c2e42;font-weight:700}
a.npick{display:block;border:1px solid #e3ddd3;border-left:4px solid #7c2e42;background:#fff;padding:14px 16px;margin:22px 0 0;text-decoration:none;color:inherit}
a.npick:hover{background:#faf8f5}
.npick .npick-l{font-size:11.5px;letter-spacing:.12em;color:#7c2e42;margin:0 0 4px}
.npick .npick-t{font-weight:700;font-size:.98rem;margin:0 0 4px;color:#1d242b}
.npick .npick-d{font-size:.85rem;color:#5a6068;margin:0;line-height:1.7}
</style>"""


def rpt_html(slug):
    c = CONFIG[slug]
    return f"""<div class="rpt" id="rpt" {MARK}>
<p class="rpt-h">この結果を、もっと詳しく読みたい方へ</p>
<p class="rpt-p">{c['what']}をまとめた有料のレポートを準備しています（価格は未定・まだ購入できません）。</p>
<button type="button" class="rpt-btn" id="rptBtn">もっと詳しいレポート（準備中）</button>
<p class="rpt-done" id="rptDone" hidden>準備中です。押しても料金はかかりません。できあがったら LINE でお知らせする予定です。受け取りたい方だけ、下から友だち追加してください（任意）。<br><a href="{LINE_URL}" id="rptLine" rel="noopener" target="_blank">LINE で知らせてもらう（任意）</a></p>
</div>"""


def npick_html(slug):
    href, to, title, desc = CONFIG[slug]['pick']
    return f"""<a class="npick" id="nextPick" href="{href}" data-to="{to}" {MARK}>
<p class="npick-l">次の1本</p>
<p class="npick-t">{title}</p>
<p class="npick-d">{desc}</p>
</a>"""


def js(slug):
    # window.__rptReset(結果名, 隠すか) を結果表示のたびに呼ぶ。押下は1結果につき1回だけ送る。
    return ("<script>(function(){var T='" + slug + "',R='';"
            "function g(n,p){try{if(typeof gtag==='function')gtag('event',n,p);}catch(e){}}"
            "function $(i){return document.getElementById(i);}"
            "var b=$('rptBtn'),d=$('rptDone'),box=$('rpt'),l=$('rptLine'),nx=$('nextPick');"
            "window.__rptReset=function(r,hide){R=String(r||'');if(box){box.hidden=!!hide;box.style.display=hide?'none':'';}"
            "if(b){b.disabled=false;b.textContent='もっと詳しいレポート（準備中）';}if(d)d.hidden=true;};"
            "if(b)b.addEventListener('click',function(){if(b.disabled)return;b.disabled=true;b.textContent='準備中です';"
            "if(d)d.hidden=false;g('paid_report_interest',{tool:T,result:R});});"
            "if(l)l.addEventListener('click',function(){g('line_add_click',{tool:T,from:'paid_report'});});"
            "if(nx)nx.addEventListener('click',function(){g('next_pick_click',{tool:T,to:nx.getAttribute('data-to'),result:R});});"
            "})();</script>")


# 占い（aisho・suhi）の showRes に足す呼び出し。18歳未満は広告と同じくレポート枠も隠す。
URANAI_RESET_CALL = "if(window.__rptReset)window.__rptReset(lastResult,box&&box.hidden);"
