# -*- coding: utf-8 -*-
"""2026-11-05 通園バンク再確認の反映。正本の値を置換し、公開ページの同じ文字列も置換する（生成スクリプトは公開後の手入れを消すので使わない）。"""
import sys, json, re
sys.path.insert(0, 'scripts')
import _daretsu_data as d
by = {c['key']: c for c in d.CITIES}

CH = [
 ('hachioji', 'facil', '実施施設一覧に44施設を掲載（表: 名称／所在地／電話番号／対象年齢の4列、五十音順、令和8年10月8日現在）。各施設の対象年齢欄は「0-2歳児」または「1-2歳児」のいずれかで表示。実施施設ごとに開所時間が異なる旨の注記あり（各施設へ要問合せ）。'),
 ('nakano', 'facil', '区の選定施設5施設（うち1施設は12月開設予定）。申込は施設ごとの募集期間に行い、抽選等で利用者を決定（令和8年11月4日〜13日に2施設が募集）。選定を受けずに認可を受けた区内施設は現在なし'),
 ('sendai', 'facil', '実施事業所の一覧表（事業所名・所在地・実施曜日・預かり時間・連絡先）を区ごとに掲載。令和8年11月1日時点の一覧で、青葉区16・宮城野区9・若林区7・太白区4・泉区9＝合計45事業所（本ページ表内の事業所数を数えたもの。原文に合計数の明記はなし）。「実施曜日及び預かり時間は令和8年11月1日時点の情報です。今後変更となる場合があります」との注記あり（2026年11月1日更新）。'),
 ('yokohama', 'facil', '保育所・幼稚園・認定こども園・小規模保育事業・地域子育て支援拠点等。年度当初の36か所に「令和８年10月から新たに30施設で事業を開始しました」（実施施設一覧PDF・令和8年10月時点）'),
 ('himeji', 'facil', '令和8年度実施施設は17施設（公立3施設、私立14施設。うち私立2施設は令和8年10月開始）。施設ごとの実施時期・曜日・定員・募集期間は市サイトに掲載。'),
 ('himeji', 'cap_note', '1日あたりの上限時間・市外利用の扱いについては当該ページ内に記載なし。令和8年度は公立施設3箇所・私立施設14箇所の計17施設（うち2施設は令和8年10月開始）で、施設ごとに実施期間・利用曜日/時間・募集定員が異なる。令和8年度からは居住地以外の施設も利用可能（認定は居住自治体）。なお令和7年度は「モデル事業」として第1期(6/2〜8/29)・第2期(9/1〜11/28)・第3期(12/1〜R8.2/27)の3期制で月10時間上限は同じ。'),
 ('sagamihara', 'facil', '令和8年度ページに実施施設一覧を区ごとに掲載。緑区9施設・中央区14施設・南区12施設の計35施設（表の行数を数えたもの。原文に合計数の明記はなし・最終更新日 令和8年10月26日）。'),
 ('sapporo', 'facil', '令和8年度実施施設一覧（PDF・令和8年10月7日更新）で61施設'),
 ('fukuoka', 'facil', '区ごとに所在地・定員・実施曜日・利用時間・申込受付方法・空き状況・給食費等を掲載（施設数は年度途中で増えている。最新の掲載数は公式ページで確認）'),
 ('saitama', 'facil', '保育所等と幼稚園の2区分で実施施設を公開（保育所等の一覧は2026年10月26日に更新）'),
 ('kobe', 'apply', None),  # 文の追記で処理
 ('sumida', 'apply', '「令和8年度こども誰でも通園制度の利用者 認定申請フォーム」（電子申請のみ）。定期利用枠の利用申請は募集施設がある月に受付（直近は令和8年11月1日〜11月8日で12月開始分・2026年11月5日確認）。'),
 ('nerima', 'apply', 'マイナンバーカードがある場合はスマートフォンアプリ「xID」を使ったオンライン申請、カードがない場合はLoGoフォームから申請（区内に住民登録がある方のみ）。認定後、登録したメールアドレスに総合支援システムのアカウントが届く。'),
 ('funabashi', 'age', '生後6か月から満3歳未満（3歳の誕生日の前日以降は利用できない＝前々日まで利用可）。初回面談があり、健康状態等により安全な通園が困難と判断された場合は利用を断ることがある。'),
 ('shibuya', 'age', '未就園児（0歳6か月〜2歳児クラス）。3歳の誕生日の前日からは上限が月54時間になる'),
 ('shinagawa', 'src', 'https://www.city.shinagawa.tokyo.jp/kodomo/hoikuenyochien/1002036/1002115.html'),
 ('chuo', 'facil', '区内実施施設5施設（京橋2・日本橋1・月島2）。0歳児クラスの受け入れはなし'),
]
KOBE_OLD = '（例：10〜12月利用分は神戸市内在住者9月1日(火)から、市外在住者9月6日(日)から）'
KOBE_NEW = '（例：10〜12月利用分は神戸市内在住者9月1日(火)から、市外在住者9月6日(日)から。1〜3月利用分は市内在住者12月4日(金)から、市外在住者12月9日(水)から）'

pairs = []
for k, f, new in CH:
    if k == 'kobe':
        pairs.append((KOBE_OLD, KOBE_NEW)); continue
    old = by[k][f]
    assert old != new
    pairs.append((old, new))

PAGES = ['tools/daredemo-tsuen-jichitai/index.html', 'articles/daredemo-tsuen-ryokin/index.html', 'articles/daredemo-tsuen-yoyaku/index.html']
files = ['scripts/_daretsu_data.py'] + PAGES
report = {}
for fn in files:
    s = open(fn, encoding='utf-8').read(); orig = s
    for old, new in pairs:
        variants = {old: new, json.dumps(old, ensure_ascii=False)[1:-1]: json.dumps(new, ensure_ascii=False)[1:-1]}
        for o, n in variants.items():
            c = s.count(o)
            if c: s = s.replace(o, n); report.setdefault(fn, []).append((o[:24], c))
    # 確認日
    s = s.replace('2026年10月5日', '2026年11月5日')
    if fn.endswith('.py'):
        s = s.replace('CHECKED = "2026年11月5日"', 'CHECKED = "2026年11月5日"')
    if s != orig:
        open(fn, 'w', encoding='utf-8', newline='').write(s)
for fn in files:
    print(fn, len(report.get(fn, [])), report.get(fn))
# 正本で全件置換できたか
src = open('scripts/_daretsu_data.py', encoding='utf-8').read()
missing = [o[:30] for o, n in pairs if n not in src]
print('正本に未反映:', missing)
