"""閲覧上位の恋愛・婚活記事10本に占い・診断ツールへの文中リンクを1文ずつ入れる（P-59 電話占いに絞る・2026-11-03）。
対象は GA4 アーカイブ直近60日の閲覧上位から、占いツールへのリンクが無く、判定待ちのロック（improvement-log.json の locks）と
LINE導線の判定中（success-rate-data）を除いたもの。既存の文面には触らず、見出しの節の末尾に1段落足すだけ。
使い方: python scripts/fortune_links_20261103.py [--dry|--apply|--check]
"""
import re, sys
MARK = 'data-fl="20261103"'
T = {
 'renai': ('/tools/renai-type-shindan/', '16タイプ恋愛診断'),
 'suhi': ('/tools/suhi-kekkon-uranai/', '数秘術でみる結婚観占い'),
 'aisho': ('/tools/aisho-uranai/', '二人の相性占い'),
 'mbti': ('/tools/mbti-aisho-uranai/', '16タイプ×星座の恋愛相性占い'),
 'seiza': ('/tools/seiza-renai-uranai/', '星座でみる恋愛傾向占い'),
 'enun': ('/tools/en-to-un/', '縁と運'),
}
def a(k):
    u, n = T[k]; return f'<a href="{u}">{n}</a>'
ITEMS = [
 ('articles/bachelor-date-guide', '向いている人・向いていない人', f'向き不向きを判断するときは、自分が恋愛で何を大事にするタイプかを知っておくと決めやすい。12問・登録なしで終わる{a("renai")}で確かめられる。'),
 ('articles/members-data', '会員数より先に見るべき「男女比率」', f'数字とは別に、自分が恋愛で何を大事にするかを先に知っておくと、アプリを選ぶ基準が決まりやすい（{a("renai")}）。'),
 ('articles/matching-app-ranking', '【年代別】 最適なアプリ選択ガイド', f'アプリを選ぶ前に、自分の恋愛タイプと相性のいいタイプを知っておきたいなら{a("renai")}も使える（12問・登録なし）。'),
 ('articles/appkon-wariai-data', 'アプリ婚が増加した背景', f'出会い方が変わっても、誰と出会えるかには巡り合わせが残ります。7代ぶんの結婚相手を選ぶ家系ゲーム{a("enun")}では、自分で決めたことと運が決めたことの回数を数えられます。'),
 ('articles/pair-ring-guide', 'ペアリングの次に来る意思決定', f'指輪の先に結婚を考えはじめたら、ふたりの結婚観を話すきっかけとして{a("suhi")}を一緒に見てみるのもいい。'),
 ('articles/nashikon-data', 'どちらを選んでも成立させるための整理', f'式をするかどうかを話し合う前に、お互いの結婚観の違いを話題にする入口として{a("suhi")}も使える。'),
 ('articles/age-data', '【年代別攻略戦略】', f'相手のプロフィールに16タイプ（MBTI）が書いてあれば、{a("mbti")}で相性の傾向を見てからいいねを返すのも楽しみ方のひとつだ。'),
 ('articles/propose-guide', '交際期間の目安', f'時期の話を切り出しにくいときは、ふたりの生年月日から関係の傾向と話し方のヒントを見られる{a("aisho")}を話題のきっかけにする手もあります。'),
 ('articles/compare-20s', '20代向けプロフィール例文', f'自分の恋愛の傾向をうまく言葉にできないときは、{a("renai")}で出たタイプの説明を手がかりにすると書き出しやすい。'),
 ('articles/profile-text', 'プロフィール文の構成テンプレート', f'性格の欄が書きにくいときは、{a("seiza")}や{a("renai")}の結果を自分の言葉に言い換えて使うと、書き出しが決まりやすい。'),
]
TAIL = re.compile(r'(?:\s|</section>|<section[^>]*>|<hr[^>]*>)*$')
def point(h, head):
    hs = [m for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', h, re.S)]
    idx = [i for i, m in enumerate(hs) if head in re.sub('<.*?>', '', m.group(1))]
    if len(idx) != 1: raise SystemExit(f'見出し一致 {len(idx)}件: {head}')
    i = idx[0]
    if i + 1 >= len(hs): raise SystemExit(f'次のh2なし: {head}')
    seg = h[:hs[i+1].start()]
    return TAIL.search(seg).start()
def main(mode):
    bad = 0
    for p, head, s in ITEMS:
        f = p + '/index.html'
        h = open(f, encoding='utf-8').read()
        if mode == '--check':
            n = h.count(MARK); ok = n == 1
            print(('OK ' if ok else 'NG ') + p, n); bad += (not ok); continue
        if MARK in h: print('済 ' + p); continue
        pos = point(h, head)
        ins = f'\n<p {MARK}>{s}</p>'
        if mode == '--dry':
            print('=== ' + p); print(h[pos-120:pos].replace('\n', '⏎') + ' ▼INS▼ ' + h[pos:pos+60].replace('\n', '⏎'))
        else:
            open(f, 'w', encoding='utf-8', newline='').write(h[:pos] + ins + h[pos:]); print('入れた ' + p)
    sys.exit(1 if bad else 0)
if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '--dry')
