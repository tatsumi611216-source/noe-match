# -*- coding: utf-8 -*-
"""ツールページの看板（title / og / twitter / h1 / JSON-LD name）を掛け替える。

なぜ必要か（2026-08-21の実測・agent/tools_audit.md）:

ツール11本のうち流入があるのは実質1本だけだった。原因を1本ずつ見ると、
**タイトルの先頭が「自作の商品名」になっていて、実際に検索される語と一致していない**
ものが多かった。GSCに残っている実クエリが、それを直接示している。

  「ガルガル期 診断」   13表示・11.2位  ← titleの先頭は「潜在ガルガル度チェック診断」
  「夫源病チェックシート」 1表示・53.0位  ← titleは「夫源病危険度チェック診断」
  「熟年離婚後 生活費 シュミレーション」 ← titleは「シミュレーター」

掛け替えの原則（この順に優先する）:

1. **実測クエリの語を先頭に置く。**GSCに出ている語 > 推測した語
2. **勝てない一般語を狙わない。**大手が固めている語は、改題しても順位は動かない。
   固有修飾（「分担」「向き不向き」「段取り」）へ寄せる
3. **URLは変えない。**リダイレクトはSEO最大のリスクで、得るものが無い
4. **内容が伴わない語を入れない。**（例: rikongo に熟年離婚の記述は0件だったので
   「熟年離婚対応」とは書かない）

やらないこと:

記事側のアンカーテキストは変えない。凍結40本のうち33本がツール名を本文に含むため、
PDCA凍結（判定 2026-09-09）に抵触する。**アンカーテキストの同期は9/9以降**に、
`agent/tools_rename.md` の残タスクとして実施する。

使い方:
    python3 scripts/rename_tools.py --dry-run   # 置換件数だけ表示
    python3 scripts/rename_tools.py             # 実行
"""
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slug -> (自ファイルだけに適用する置換, 全ツール+トップに適用する商品名の置換)
# 前者を先に当てる（後者の旧文字列を含むため）。
RENAMES = {
    'garugaru-check': (
        [
            ('<title>潜在ガルガル度チェック診断｜産後の「ガルガル期」危険度を53問で事前診断【無料】</title>',
             '<title>ガルガル期診断｜産後どれくらい出そうかを53問で事前チェック【無料・登録なし】</title>'),
            ('og:title" content="潜在ガルガル度チェック診断｜産後のガルガル期危険度を53問で事前診断"',
             'og:title" content="ガルガル期診断｜産後のガルガル度を53問で事前チェック"'),
            ('twitter:title" content="潜在ガルガル度チェック診断【無料53問】"',
             'twitter:title" content="ガルガル期診断【無料53問】"'),
            ('<h1>潜在ガルガル度チェック診断</h1>',
             '<h1>ガルガル期診断｜産後どれくらい出そうかを事前に見積もる</h1>'),
        ],
        ('潜在ガルガル度チェック診断', 'ガルガル期診断'),
    ),
    'fugenbyo-check': (
        [
            ('<title>夫源病危険度チェック診断｜その不調、夫が原因かも【無料45問・2分の簡易版あり】</title>',
             '<title>夫源病チェックシート｜45問で危険度をセルフ診断【無料・2分の簡易版あり】</title>'),
            ('og:title" content="夫源病危険度チェック診断｜その不調、夫が原因かも【無料45問】"',
             'og:title" content="夫源病チェックシート｜その不調、夫が原因かも【無料45問】"'),
            ('twitter:title" content="夫源病危険度チェック診断【無料45問】"',
             'twitter:title" content="夫源病チェックシート【無料45問】"'),
            ('<h1>夫源病危険度チェック診断</h1>',
             '<h1>夫源病チェックシート｜45問で危険度をセルフ診断</h1>'),
        ],
        ('夫源病危険度チェック診断', '夫源病チェックシート'),
    ),
    'saigenbyo-check': (
        [
            ('<title>妻源病危険度チェック診断｜帰宅が憂うつなあなたへ【無料45問・2分の簡易版あり】</title>',
             '<title>帰宅恐怖症・妻源病チェックシート｜45問で危険度をセルフ診断【無料・2分の簡易版あり】</title>'),
            ('og:title" content="妻源病危険度チェック診断｜帰宅が憂うつなあなたへ【無料45問】"',
             'og:title" content="帰宅恐怖症・妻源病チェックシート｜帰宅が憂うつなあなたへ【無料45問】"'),
            ('twitter:title" content="妻源病危険度チェック診断【無料45問】"',
             'twitter:title" content="帰宅恐怖症・妻源病チェックシート【無料45問】"'),
            ('<h1>妻源病危険度チェック診断</h1>',
             '<h1>帰宅恐怖症・妻源病チェックシート｜45問で危険度をセルフ診断</h1>'),
        ],
        ('妻源病危険度チェック診断', '妻源病チェックシート'),
    ),
    'kekkon-shikin-keisanki': (
        [
            ('<title>結婚資金計算機｜挙式スタイル・指輪・新生活から総額と自己負担を試算【2026年版】</title>',
             '<title>結婚費用シミュレーション｜挙式・指輪・新生活の総額と「実質自己負担」を試算【2026年版】</title>'),
            ('og:title" content="結婚資金計算機｜挙式スタイル・指輪・新生活から総額と自己負担を試算【2026年版】"',
             'og:title" content="結婚費用シミュレーション｜挙式・指輪・新生活の総額と「実質自己負担」を試算【2026年版】"'),
            ('twitter:title" content="結婚資金計算機｜総額と実質自己負担を試算【2026年版】"',
             'twitter:title" content="結婚費用シミュレーション｜総額と実質自己負担を試算【2026年版】"'),
        ],
        ('結婚資金計算機', '結婚費用シミュレーション'),
    ),
    'seikatsuhi-simulator': (
        [
            ('<title>ふたりの生活費シミュレーター｜月額の内訳と「収入比でいくらずつ」を試算【2026年版】</title>',
             '<title>二人暮らしの生活費 分担シミュレーション｜どちらがいくら出すかを収入比で計算【2026年版】</title>'),
            ('og:title" content="ふたりの生活費シミュレーター｜月額の内訳と「収入比でいくらずつ」を試算【2026年版】"',
             'og:title" content="二人暮らしの生活費 分担シミュレーション｜どちらがいくら出すかを収入比で計算【2026年版】"'),
        ],
        ('ふたりの生活費シミュレーター', '二人暮らしの生活費 分担シミュレーション'),
    ),
    'koisaihi-simulator': (
        [
            ('<title>デート代・交際費シミュレーター｜年代別の目安と年間総額を無料で試算【2026年版】</title>',
             '<title>デート代・交際費の平均と年間総額｜付き合う前と後で分けて試算【割り勘・収入比も】</title>'),
            ('og:title" content="デート代・交際費シミュレーター｜年代別の目安と年間総額を無料で試算【2026年版】"',
             'og:title" content="デート代・交際費の平均と年間総額｜付き合う前と後で分けて試算【2026年版】"'),
        ],
        ('デート代・交際費シミュレーター', 'デート代・交際費シミュレーション'),
    ),
    'soudanjo-simulator': (
        [
            ('<title>結婚相談所 料金シミュレーター｜活動期間×タイプ別の総額を試算【2026年版】</title>',
             '<title>結婚相談所の費用シミュレーション｜総額いくらかを期間×タイプ別に試算【2026年版】</title>'),
            ('og:title" content="結婚相談所 料金シミュレーター｜活動期間×タイプ別の総額を試算【2026年版】"',
             'og:title" content="結婚相談所の費用シミュレーション｜総額いくらかを期間×タイプ別に試算【2026年版】"'),
            ('twitter:title" content="結婚相談所 料金シミュレーター【2026年版】"',
             'twitter:title" content="結婚相談所の費用シミュレーション【2026年版】"'),
        ],
        ('結婚相談所 料金シミュレーター', '結婚相談所の費用シミュレーション'),
    ),
    'rikongo-seikatsuhi': (
        [],
        ('離婚後の生活費シミュレーター', '離婚後の生活費シミュレーション'),
    ),
    'kekkon-yarukoto': (
        [],
        ('結婚のやることリスト', '結婚の段取り・やることリスト'),
    ),
    # 商品名は据え置き。titleとh1だけ、実測クエリ「婚活 アプリ 相談所 どっち」の形へ寄せる。
    'konkatsu-type-shindan': (
        [
            ('<title>婚活タイプ診断｜自分に合った婚活はどれか無料で診断【登録なし・2026年版】</title>',
             '<title>婚活はアプリ・相談所・パーティーのどれ？向き不向きを60秒で診断【無料・登録なし】</title>'),
            ('og:title" content="婚活タイプ診断｜自分に合った婚活はどれか無料で診断【登録なし・2026年版】"',
             'og:title" content="婚活はアプリ・相談所・パーティーのどれ？向き不向きを60秒で診断【無料・登録なし】"'),
            ('<h1>婚活タイプ診断｜自分に向いている婚活はどれかを60秒で</h1>',
             '<h1>婚活はアプリ・相談所・パーティーのどれ？向き不向きを60秒で診断</h1>'),
        ],
        None,
    ),
    # 15.5位で既に機能しているので最小変更。差別化（絞り込み）を前に出すだけ。
    'nyuseki-calendar': (
        [
            ('<title>入籍日カレンダー2026〜2030｜大安・天赦日・一粒万倍日から縁起のいい日を無料で絞り込む</title>',
             '<title>入籍日カレンダー2026〜2030｜大安・天赦日・一粒万倍日の縁起のいい日を土日/平日で絞り込む</title>'),
            ('og:title" content="入籍日カレンダー2026〜2030｜大安・天赦日・一粒万倍日から縁起のいい日を無料で絞り込む"',
             'og:title" content="入籍日カレンダー2026〜2030｜大安・天赦日・一粒万倍日の縁起のいい日を土日/平日で絞り込む"'),
            ('<h1>入籍日カレンダー｜2026〜2030年の大安・天赦日から条件で絞り込む</h1>',
             '<h1>入籍日カレンダー｜2026〜2030年の大安・天赦日から縁起のいい日を絞り込む</h1>'),
        ],
        None,
    ),
}


def targets():
    """商品名の置換を当てる範囲。記事は凍結中なので含めない。"""
    return sorted(glob.glob(os.path.join(ROOT, 'tools', '*', 'index.html'))) \
        + [os.path.join(ROOT, 'index.html')]


def main():
    dry = '--dry-run' in sys.argv
    files = {p: io.open(p, encoding='utf-8').read() for p in targets()}
    missing, applied = [], []

    for slug, (specific, rename) in RENAMES.items():
        own = os.path.join(ROOT, 'tools', slug, 'index.html')
        if own not in files:
            missing.append('%s: ページが無い' % slug)
            continue
        for old, new in specific:
            if old not in files[own]:
                missing.append('%s: 旧文字列が見つからない -> %s' % (slug, old[:60]))
                continue
            files[own] = files[own].replace(old, new)
            applied.append('%s  個別置換  %s' % (slug, new[:70]))
        if rename:
            old, new = rename
            hits = sum(s.count(old) for s in files.values())
            if not hits:
                missing.append('%s: 商品名が見つからない -> %s' % (slug, old))
                continue
            for p in files:
                files[p] = files[p].replace(old, new)
            applied.append('%s  商品名 %s -> %s（%d箇所）' % (slug, old, new, hits))

    for line in applied:
        print('  ' + line)
    if missing:
        print('\n⚠ 未適用:')
        for m in missing:
            print('  ' + m)

    if dry:
        print('\n--dry-run のため書き込みなし')
        return 1 if missing else 0

    for p, s in files.items():
        io.open(p, 'w', encoding='utf-8').write(s)
    print('\n%d ファイルを更新した。scripts/tools_audit.py を回して台帳を再生成すること。' % len(files))
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
