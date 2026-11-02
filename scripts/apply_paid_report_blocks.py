"""T-132: 3本の結果画面に「有料レポートの関心ボタン（準備中）」と「次の1本」を挿入する（何度実行しても二重にならない）。

aisho-uranai・suhi-kekkon-uranai は build_uranai_tools.py でも同じ部品を出す（生成し直しても消えない）。
ただし生成スクリプトは後から足された next-links（renai・mbti）を持たないので、既存HTMLにはこのスクリプトで入れる。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from paid_report_blocks import CSS, MARK, URANAI_RESET_CALL, js, npick_html, rpt_html  # noqa: E402

SHOWRES_OLD = "box.hidden=mn;box.style.display=mn?'none':'';}"


def once(src, old, new, label):
    if src.count(old) != 1:
        raise SystemExit(f'{label}: 挿入位置が1か所に決まらない（{src.count(old)}件）: {old[:60]}')
    return src.replace(old, new)


def patch_uranai(slug):
    p = os.path.join(ROOT, 'tools', slug, 'index.html')
    src = open(p, encoding='utf-8').read()
    if MARK in src:
        print('skip (already)', slug)
        return
    src = once(src, '</head>', CSS + '\n</head>', slug)
    src = once(src, '\n<div class="share-block">', '\n' + rpt_html(slug) + '\n<div class="share-block">', slug)
    src = once(src, '<div class="next-links">', npick_html(slug) + '\n<div class="next-links">', slug)
    src = once(src, SHOWRES_OLD, SHOWRES_OLD + URANAI_RESET_CALL, slug)
    src = once(src, '</body>', js(slug) + '\n</body>', slug)
    open(p, 'w', encoding='utf-8', newline='\n').write(src)
    print('patched', slug)


def patch_konkatsu():
    slug = 'konkatsu-type-shindan'
    p = os.path.join(ROOT, 'tools', slug, 'index.html')
    src = open(p, encoding='utf-8').read()
    if MARK in src:
        print('skip (already)', slug)
        return
    src = once(src, '</head>', CSS + '\n</head>', slug)
    src = once(src, '\n  <h3>次に読むと早いページ</h3>', '\n  ' + rpt_html(slug) + '\n\n  <h3>次に読むと早いページ</h3>', slug)
    src = once(src, '  <div id="prbox"></div>\n', '  <div id="prbox"></div>\n  ' + npick_html(slug) + '\n', slug)
    src = once(src, "  document.getElementById('res').classList.add('show');",
               "  if(window.__rptReset)window.__rptReset(arr[0].k,false);\n  document.getElementById('res').classList.add('show');", slug)
    src = once(src, '</body>', js(slug) + '\n</body>', slug)
    open(p, 'w', encoding='utf-8', newline='\n').write(src)
    print('patched', slug)


def patch_generator():
    p = os.path.join(ROOT, 'scripts', 'build_uranai_tools.py')
    src = open(p, encoding='utf-8').read()
    if 'paid_report_blocks' in src:
        print('skip (already) generator')
        return
    src = once(src, 'from uranai_content import SIGNS, ELEM_DESC, NUMBERS, COMPAT  # noqa: E402\n',
               'from uranai_content import SIGNS, ELEM_DESC, NUMBERS, COMPAT  # noqa: E402\n'
               'import paid_report_blocks as PRB  # noqa: E402  T-132 関心ボタン・次の1本\n', 'gen')
    src = once(src, SHOWRES_OLD, SHOWRES_OLD + URANAI_RESET_CALL, 'gen')
    src = once(src, '\n{share_html()}\n{prbox_html(slug, pr_lead)}\n{other_links(slug)}\n',
               "\n{PRB.rpt_html(slug) if slug in PRB.CONFIG else ''}\n{share_html()}\n{prbox_html(slug, pr_lead)}\n"
               "{PRB.npick_html(slug) if slug in PRB.CONFIG else ''}\n{other_links(slug)}\n", 'gen')
    src = once(src, '\n</head>', "\n{PRB.CSS if slug in PRB.CONFIG else ''}\n</head>", 'gen')
    src = once(src, '}})();\n</script>\n</body>', "}})();\n</script>\n{PRB.js(slug) if slug in PRB.CONFIG else ''}\n</body>", 'gen')
    open(p, 'w', encoding='utf-8', newline='\n').write(src)
    print('patched generator')


if __name__ == '__main__':
    patch_uranai('aisho-uranai')
    patch_uranai('suhi-kekkon-uranai')
    patch_konkatsu()
    patch_generator()
