"""tools/ の「結果の枠」が読者に実際に見えるかを検査する（2026-09-27 追加）。

背景: 共通シェルの CSS は `.result{display:none}` / `.result.show{display:block}` なのに、
スクリプトが `show` を付けないツールがあり、結果・LINE・広告の枠が本番で一度も表示されていなかった
（861a8c7 で4本、同日に残りを修正）。HTML にあることと画面に出ることは別なので、機械で止める。

使い方:
    python scripts/check_result_visible.py            静的検査（ブラウザ不要・factory_audit から呼ばれる）
    python scripts/check_result_visible.py --browser  実ブラウザ検査（playwright。ローカルサーバーを立て、
                                                      入力→ボタン→結果の枠が見えるかを確かめる）
    python scripts/check_result_visible.py --browser --base https://www.noe-match.com   本番を同じ手順で見る（www 付きで指定する）
    python scripts/check_result_visible.py --browser tools/sangokea-ryokin          1本だけ

静的検査の判定: 結果の枠（id="result" / id="res"）が CSS の初期状態で display:none なのに、
  - 枠自身に show が付いていない、かつ
  - スクリプトに表示へ切り替える処理（classList.add/toggle('show')・className に show・
    style.display への代入・hidden の解除）が無い
ときに「結果の枠が表示されない」とする。静的検査は取りこぼしがありうるので、ツールを作った・
直したときは --browser でも必ず確かめる。
"""
import argparse
import functools
import http.server
import os
import re
import socketserver
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESULT_TAG_RE = re.compile(r'<([a-z]+)\b[^>]*\bid="(result|res)"[^>]*>', re.I)
# 表示へ切り替える処理。結果の枠そのもの（変数経由を含む）に向いているものだけを数える。
# 別要素（ページトップボタン・比較表など）の style.display や show は数えない。
REF_RE = r"(?:document\.getElementById|\$|document\.querySelector)\(\s*['\"]#?{rid}['\"]\s*\)"
REVEAL_TAIL = (r"\s*\.\s*(?:classList\.(?:add|toggle)\(\s*['\"]show['\"]"
               r"|className\s*[+]?=\s*[^;]*show"
               r"|style\.display\s*=\s*['\"](?!none)"
               r"|hidden\s*=\s*false"
               r"|removeAttribute\(\s*['\"]hidden['\"])")


def _revealed_by_js(js, rid):
    ref = REF_RE.format(rid=re.escape(rid))
    names = set(re.findall(r"([A-Za-z_$][\w$]*)\s*=\s*" + ref, js))
    targets = [ref] + [r"(?<![\w$.])" + re.escape(n) for n in names]
    return any(re.search(t + REVEAL_TAIL, js) for t in targets)


def tool_slugs():
    base = os.path.join(ROOT, 'tools')
    return sorted(d for d in os.listdir(base)
                  if os.path.exists(os.path.join(base, d, 'index.html')))


def _classes(tag):
    m = re.search(r'\bclass="([^"]*)"', tag)
    return m.group(1).split() if m else []


def static_check(html):
    """問題があればエラー文の list を返す（空なら OK）"""
    m = RESULT_TAG_RE.search(html)
    if not m:
        return []  # 結果の枠の検出は factory_audit の audit_tool が別に見ている
    tag, rid = m.group(0), m.group(2)
    cls = _classes(tag)
    css = ''.join(re.findall(r'<style[^>]*>(.*?)</style>', html, re.S | re.I))
    js = ''.join(re.findall(r'<script(?![^>]*application/ld\+json)[^>]*>(.*?)</script>',
                            html, re.S | re.I))
    hidden = False
    for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        if not re.search(r'display\s*:\s*none', body):
            continue
        for s in (x.strip() for x in sel.split(',')):
            if s == '#' + rid or any(s == '.' + c for c in cls):
                hidden = True
    if re.search(r'\bhidden\b(?!=)', tag) or re.search(r'style="[^"]*display\s*:\s*none', tag):
        hidden = True
    if not hidden or 'show' in cls:
        return []
    if _revealed_by_js(js, rid):
        return []
    return [f'結果の枠（#{rid}）が CSS で非表示のまま、表示に切り替える処理が無い']


# ---------------------------------------------------------------- 実ブラウザ検査
PROBE_JS = r"""() => {
  const el = document.getElementById('result') || document.getElementById('res') || document.getElementById('out');
  if (!el) return {found:false};
  const cs = getComputedStyle(el), r = el.getBoundingClientRect();
  let v = cs.display !== 'none' && cs.visibility !== 'hidden' && r.height > 0;
  for (let p = el.parentElement; p && v; p = p.parentElement)
    if (getComputedStyle(p).display === 'none') v = false;
  const vis = a => { const s = a.getBoundingClientRect(); return s.height > 0 && s.width > 0; };
  const links = [...el.querySelectorAll('a')];
  return {found:true, id:el.id, display:cs.display, height:Math.round(r.height), visible:v,
          line:links.filter(a => a.href.includes('lin.ee')).map(vis),
          ads:links.filter(a => /a8\.net|afi-b|accesstrade|valuecommerce|moshimo|rakuten|amzn|amazon/.test(a.href)).map(vis)};
}"""

FILL_JS = r"""() => {
  const seen = new Set();
  document.querySelectorAll('input[type=radio]').forEach(r => {
    if (!seen.has(r.name)) { seen.add(r.name);
      if (!document.querySelector(`input[type=radio][name="${r.name}"]:checked`)) r.click(); }
  });
  document.querySelectorAll('select').forEach(s => {
    if (!s.value && s.options.length > 1) { s.selectedIndex = 1; s.dispatchEvent(new Event('change', {bubbles:true})); }
  });
  document.querySelectorAll('input[type=number], input[type=text], input:not([type])').forEach(i => {
    if (!i.value && !i.readOnly) { i.value = i.min || '30'; i.dispatchEvent(new Event('input', {bubbles:true})); }
  });
  document.querySelectorAll('input[type=date]').forEach(i => {
    if (!i.value) { i.value = '2026-11-22'; i.dispatchEvent(new Event('change', {bubbles:true})); }
  });
}"""


def _serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=root)
    httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f'http://127.0.0.1:{httpd.server_address[1]}'


def browser_check(slugs, base=None, width=390):
    from playwright.sync_api import sync_playwright
    httpd = None
    if not base:
        httpd, base = _serve(ROOT)
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': width, 'height': 900})
        # 外部（広告・GA・フォント）は読まない。検品アクセスが計測に乗らないようにする意味もある
        host = base.split('/')[2]
        ctx.route('**/*', lambda r: r.continue_() if host in r.request.url else r.abort())
        for slug in slugs:
            url = f'{base}/tools/{slug}/'
            pg = ctx.new_page()
            rec = {'slug': 'tools/' + slug}
            try:
                pg.goto(url, wait_until='load', timeout=20000)
                rec['before'] = pg.evaluate(PROBE_JS)
                for _ in range(3):  # 設問が順に出るツールがあるので数回まわす
                    pg.evaluate(FILL_JS)
                    btns = pg.locator('button:visible, input[type=submit]:visible, input[type=button]:visible')
                    for i in range(btns.count()):
                        bt = btns.nth(i)
                        label = (bt.inner_text() or bt.get_attribute('value') or '') + (bt.get_attribute('id') or '')
                        if re.search(r'やり直|リセット|reset|もう一度|コピー|copy|share|シェア', label, re.I):
                            continue
                        try:
                            bt.click(timeout=1500)
                        except Exception:
                            pass
                        if pg.url.split('#')[0].split('?')[0] != url:
                            pg.goto(url, wait_until='load')
                            break
                    rec['after'] = pg.evaluate(PROBE_JS)
                    if rec['after'].get('visible'):
                        break
            except Exception as e:  # noqa: BLE001
                rec['error'] = str(e)[:200]
            pg.close()
            out.append(rec)
        b.close()
    if httpd:
        httpd.shutdown()
    return out


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('slugs', nargs='*', help='tools/<slug>（省略で全本）')
    ap.add_argument('--browser', action='store_true')
    ap.add_argument('--base', help='--browser で見るサイト（省略でこのリポジトリをローカル配信）')
    ap.add_argument('--width', type=int, default=390)
    a = ap.parse_args()
    slugs = [s.split('/')[-1].strip('/') for s in a.slugs] or tool_slugs()
    bad = 0
    if a.browser:
        for r in browser_check(slugs, a.base, a.width):
            af = r.get('after') or {}
            ok = af.get('visible') and all(af.get('line', [])) and all(af.get('ads', []))
            bad += not ok
            print(f"{'OK  ' if ok else 'NG  '}{r['slug']}: before={r.get('before', {}).get('display')} "
                  f"after={af.get('display')} h={af.get('height')} line={af.get('line')} ads={af.get('ads')}"
                  + (f" error={r['error']}" if 'error' in r else ''))
    else:
        for s in slugs:
            with open(os.path.join(ROOT, 'tools', s, 'index.html'), encoding='utf-8', errors='replace') as f:
                errs = static_check(f.read())
            bad += bool(errs)
            print(f"{'NG  ' if errs else 'OK  '}tools/{s}" + (': ' + ' / '.join(errs) if errs else ''))
    print(f'\n{len(slugs)}本中 NG {bad}本')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
