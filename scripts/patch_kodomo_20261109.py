# -*- coding: utf-8 -*-
"""子ども医療費バンクの11/9再確認を正本とページへ置換で反映する（ビルダーで再生成しない）。"""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
OLD_D, NEW_D = '2026年10月8日', '2026年11月9日'
CHUO_OLD = 'https://www.city.chuo.lg.jp/kosodate/teate/akimoto.html'
CHUO_NEW = 'https://www.city.chuo.lg.jp/a0020/kosodate/kosodate/teatejosei/iryouhijosei/akimoto.html'
SHINA_OLD = 'https://www.city.shinagawa.tokyo.jp/PC/kodomo/kodomo-iryohizyosei/hpg000017744.html'
SHINA_NEW = 'https://www.city.shinagawa.tokyo.jp/kodomo/kodomoteate/1009432/1001889.html'
CHUO_NOTE_OLD = 'ページ掲載日は2026年7月31日。同一内容が ' + CHUO_NEW + ' にも存在（同一ページの別パス）'
CHUO_NOTE_NEW = 'ページ掲載日は2026年10月27日'

COMMON = [
    ('オンライン（ぴったりサービス）のいずれかで申請。日本橋・月島・晴海特別出張所、郵送、ぴったりサービスで申請した場合',
     'オンライン（マイナポータル）のいずれかで申請。日本橋・月島・晴海特別出張所、郵送、マイナポータルで申請した場合', 1),
    ('・郵送・電子申請（ぴったりサービス）の3方式', '・郵送・電子申請（マイナポータル。令和8年10月27日にぴったりサービスから移行）の3方式', 1),
    (CHUO_NOTE_OLD, CHUO_NOTE_NEW, 1),
]

def apply(path, pairs):
    p = ROOT / path
    s = p.read_bytes().decode('utf-8')
    for old, new, n in pairs:
        c = s.count(old)
        if (n is not None and c != n) or c == 0:
            raise SystemExit(f'{path}: 想定外の件数 {c} (期待 {n}): {old[:50]}')
        s = s.replace(old, new)
    p.write_bytes(s.encode('utf-8'))
    print('ok', path)

def main():
    log = json.loads((ROOT / 'agent/seo/improvement-log.json').read_text(encoding='utf-8'))
    for l in log.get('locks', []):
        if l['until'] >= '2026-11-09' and any(t in l['path'] for t in ('kodomo-iryohi-jichitai', 'kodomo-iryohi-data', 'kosodate-shien-23ku')):
            raise SystemExit(f"期限内のロック: {l['path']} {l['until']}")
    apply('scripts/_kodomo_iryo_data.py', COMMON + [
        ('CHECKED = "%s"' % OLD_D, 'CHECKED = "%s"' % NEW_D, 1),
        (CHUO_OLD, CHUO_NEW, 1), (SHINA_OLD, SHINA_NEW, 1)])
    apply('tools/kodomo-iryohi-jichitai/index.html', COMMON + [
        (OLD_D, NEW_D, None),
        ('"dateModified": "2026-10-08"', '"dateModified": "2026-11-09"', 1),
        (CHUO_OLD, CHUO_NEW, None), (SHINA_OLD, SHINA_NEW, None)])
    apply('articles/kodomo-iryohi-data/index.html', [
        (OLD_D, NEW_D, None),
        ('"dateModified": "2026-10-08"', '"dateModified": "2026-11-09"', 1),
        (CHUO_OLD, CHUO_NEW, None), (SHINA_OLD, SHINA_NEW, None)])
    apply('tools/kosodate-shien-23ku/index.html', [
        ('子ども医療費は' + OLD_D, '子ども医療費は' + NEW_D, None),
        (OLD_D + 'に確認した範囲では', NEW_D + 'に確認した範囲では', 2),
        ('"kodomo": "%s"' % OLD_D, '"kodomo": "%s"' % NEW_D, 1)])
    for sm in ('sitemap.xml', 'sitemap-all.xml'):
        p = ROOT / sm
        if not p.exists():
            continue
        s = p.read_bytes().decode('utf-8')
        n = 0
        for u in ('/tools/kodomo-iryohi-jichitai/', '/articles/kodomo-iryohi-data/', '/tools/kosodate-shien-23ku/'):
            s, k = re.subn(r'(<loc>[^<]*%s</loc>\s*<lastmod>)[^<]+' % re.escape(u), r'\g<1>2026-11-09', s)
            n += k
        p.write_bytes(s.encode('utf-8'))
        print(sm, n)

main()
