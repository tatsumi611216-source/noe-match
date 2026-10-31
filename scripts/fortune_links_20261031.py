"""占い・診断ツールへの文中リンクを表示上位14ページへ入れる（affiliate-fortune-links・2026-10-31）。
使い方: python scripts/fortune_links_20261031.py [--dry|--apply|--check]
"""
import re, sys
MARK = 'data-fl="20261031"'
T = {
 'renai': ('/tools/renai-type-shindan/', '16タイプ恋愛診断'),
 'suhi': ('/tools/suhi-kekkon-uranai/', '数秘術でみる結婚観占い'),
 'aisho': ('/tools/aisho-uranai/', '二人の相性占い'),
 'mbti': ('/tools/mbti-aisho-uranai/', '16タイプ×星座の恋愛相性占い'),
 'seiza': ('/tools/seiza-renai-uranai/', '星座でみる恋愛傾向占い'),
}
def a(k):
    u, n = T[k]; return f'<a href="{u}">{n}</a>'
ITEMS = [
 ('articles/with-guide', '心理テスト機能', f'withに登録する前に自分の恋愛タイプを知っておきたい人は、12問・登録なしで終わる{a("renai")}も使えます。'),
 ('tools/nyuseki-calendar', '縁起より先に決めたほうがよいこと', f'日取りを決める前に、ふたりの結婚観を話すきっかけとして{a("suhi")}を一緒に見てみるのもひとつです。'),
 ('articles/with-seriousness-data', '心理テスト機能と真剣度の関係', f'心理テストで出る相性の考え方を先に試すなら、{a("renai")}で自分のタイプと相性のいいタイプを確かめられます。'),
 ('tools/koisaihi-simulator', '負担の分け方に正解はありません', f'お金の話を切り出しにくいときは、{a("aisho")}の「話し方のヒント」を会話の入口に使う手もあります。'),
 ('articles/pairs-guide', 'Pairsで成功する人 vs 失敗する人', f'自分がどちらの進め方に近いかは、{a("renai")}の「恋の主導」「距離感」の結果も参考になります。'),
 ('articles/hatsushon-nenmei-data', '年齢別の婚活戦略', f'年齢の数字とは別に、自分が結婚に何を求めるかを整理したいときは{a("suhi")}も手がかりになります。'),
 ('articles/pairs-women', 'いいね選別の3段階フィルタリング', f'プロフィールに16タイプ（MBTI）を書いている相手なら、{a("mbti")}で相性の傾向を見てからいいねを返すのも楽しみ方のひとつです。'),
 ('articles/with-women', '相性診断の活用法', f'アプリの外でも相性を見てみたいときは、{a("mbti")}で二人の相性度と距離が縮まる話し方を確かめられます。'),
 ('articles/omiai-guide', 'Omiaiで成功するためのステップ', f'動き出す前に自分の恋愛タイプを把握しておくと、相手選びの軸が決めやすくなります（{a("renai")}）。'),
 ('articles/kekkon-madeno-kikan-data', '期間の長さより重要なこと', f'期間より大事な「結婚観のすり合わせ」の話題づくりに、{a("suhi")}をふたりで試すこともできます。'),
 ('articles/tapple-guide', 'Tappleで成功する20代向けガイド', f'自分の恋愛の傾向をつかむ入口として、{a("seiza")}も気軽に使えます。'),
 ('articles/nyuseki-2027-guide', '吉日にこだわるべきか', f'暦と一緒にふたりの生年月日の相性も見ておきたいなら、{a("aisho")}が使えます。'),
 ('articles/first-date-spot', '当日の進め方', f'会話のネタに困ったら、お互いの星座の恋愛傾向（{a("seiza")}）を話題にするのも定番です。'),
 ('articles/konkatsu-roadmap', 'STEP 5', f'結婚観を直接聞きにくいときは、{a("suhi")}を話のきっかけに使えます。'),
]
TAIL = re.compile(r'(?:\s|</section>|<section[^>]*>|<hr[^>]*>)*$')
BEFORE = {'tools/koisaihi-simulator': chr(10)*2 + '<p class="hint">本ツールは一般的なレンジ'}
def point(h, head, p=None):
    if p in BEFORE:
        i = h.find(head); j = h.find(BEFORE[p], i)
        if i < 0 or j < 0 or h.count(BEFORE[p]) != 1: raise SystemExit('BEFORE不一致: ' + p)
        return j
    hs = [m for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', h, re.S)]
    idx = [i for i, m in enumerate(hs) if head in re.sub('<.*?>', '', m.group(1))]
    if len(idx) != 1: raise SystemExit(f'見出し一致 {len(idx)}件: {head}')
    i = idx[0]
    end = hs[i+1].start() if i+1 < len(hs) else None
    if end is None: raise SystemExit(f'次のh2なし: {head}')
    seg = h[:end]
    m = TAIL.search(seg)
    return m.start()
def main(mode):
    bad = 0
    for p, head, s in ITEMS:
        f = p + '/index.html'
        h = open(f, encoding='utf-8').read()
        if mode == '--check':
            n = h.count(MARK); ok = n == 1
            print(('OK ' if ok else 'NG ') + p, n); bad += (not ok); continue
        if MARK in h: print('済 ' + p); continue
        pos = point(h, head, p)
        ins = f'\n<p {MARK}>{s}</p>'
        if mode == '--dry':
            print('=== ' + p); print(h[pos-120:pos].replace('\n', '⏎') + ' ▼INS▼ ' + h[pos:pos+60].replace('\n', '⏎'))
        else:
            open(f, 'w', encoding='utf-8', newline='').write(h[:pos] + ins + h[pos:]); print('入れた ' + p)
    sys.exit(1 if bad else 0)
if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '--dry')
