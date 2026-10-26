# -*- coding: utf-8 -*-
"""制度ツールの結果直後にLINE CTAを置く（2026-09-04）

なぜ:
CTAは本文の最下部にあり、90%スクロール到達は page_view 630に対し70＝**11%**。
一方 tool_calc は押されている。**結果は見られているのに、その直後に何も置いていない。**

計器も同時に直す:
`line_add_click` の位置は `pos` パラメータで送っていたが、**GA4にカスタムディメンションが
1つも登録されていない**ためAPIで切り分けられなかった（9/3のCTA配置判定が読めなかった直接の原因）。
**位置をイベント名に持たせる**（line_add_result / line_add_bottom）ことで、登録なしで測れるようにする。

  python scripts/add_result_cta.py --dry-run
  python scripts/add_result_cta.py --apply
"""
import argparse
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = ["byoji-hoiku-ryokin", "daredemo-tsuen-jichitai", "funin-josei-jichitai",
         "hitorioya-shien-jichitai", "hoikuen-tensu-nerima", "ikukyu-encho-hantei",
         "kekkon-shinseikatsu-jichitai", "kodomo-iryohi-jichitai", "sangokea-ryokin"]

CTA = """  <section id="line-cta-result" style="border:1px solid #e3ddd3;background:#f7f5f2;padding:18px 18px 20px;margin:24px 0 0;text-align:center">
    <p style="margin:0 0 6px;font-size:11px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif">NOE OFFICIAL LINE</p>
    <p style="margin:0 0 10px;font-size:16px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5">{head}</p>
    <p style="margin:0 0 16px;font-size:13px;color:#5a6068;line-height:1.85">{body}</p>
    <a href="{url}" rel="noopener" onclick="try{{gtag('event','line_add_result',{{tool:'{slug}'}});}}catch(e){{}}" style="display:inline-block;background:#7c2e42;color:#ffffff;padding:12px 30px;font-size:14px;font-weight:600;text-decoration:none">友だち追加する</a>
    <p style="margin:10px 0 0;font-size:11px;color:#8a8f95">登録は無料。いつでも解除できます。</p>
  </section>
"""

OBSERVER = """<script>(function(){var r=document.getElementById('out'),c=document.getElementById('line-cta-result');if(!r||!c)return;var sync=function(){c.hidden=(r.innerHTML.trim()==='');};sync();new MutationObserver(sync).observe(r,{childList:true,subtree:true});})();</script>
"""


def close_index(html, start):
    """start は開始タグの '<' の位置。対応する </div> の直前を返す"""
    i = html.index(">", start) + 1
    depth = 1
    for m in re.finditer(r"<(/?)div\b", html[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return i + m.start()
    raise ValueError("閉じタグが見つからない")


def cta_source(html):
    sec = re.search(r'<section id="line-cta".*?</section>', html, re.S)
    if not sec:
        raise ValueError("既存のLINE CTAが無い")
    s = sec.group(0)
    ps = re.findall(r'<p[^>]*>(.*?)</p>', s, re.S)
    head = next((re.sub(r"<[^>]+>", "", p).strip() for p in ps
                 if "line-height:1.5" in s.split(p)[0][-160:]), "")
    body = next((re.sub(r"<[^>]+>", "", p).strip().replace("\n", "") for p in ps
                 if "line-height:1.9" in s.split(p)[0][-160:]), "")
    url = re.search(r'href="(https://lin\.ee/[^"]+)"', s).group(1)
    return head, body, url


def process(slug, apply_):
    path = os.path.join(ROOT, "tools", slug, "index.html")
    html = io.open(path, encoding="utf-8").read()
    if 'id="line-cta-result"' in html:
        return f"{slug}: 既に結果CTAがある（skip）"

    head, body, url = cta_source(html)
    # 結果直後は短くする。最下部CTAの本文の第1文だけを使う
    body = body.split("。")[0].strip() + "。"
    block = CTA.format(head=head, body=body, url=url, slug=slug)

    m = re.search(r'<div[^>]*id="(result|out)"[^>]*>', html)
    if not m:
        return f"{slug}: 結果コンテナが無い（skip）"
    if m.group(1) == "out":
        end = html.index(">", m.start()) + 1
        close = html.index("</div>", end) + len("</div>")
        new = html[:close] + "\n" + block.replace(
            'id="line-cta-result" style', 'id="line-cta-result" hidden style') + html[close:]
        new = new.replace("</body>", OBSERVER + "</body>", 1)
        where = "#out の直後（表示はMutationObserverで同期）"
    else:
        cut = close_index(html, m.start())
        new = html[:cut] + block + html[cut:]
        where = "#result の最後の子（結果と一緒に出る）"

    n_bottom = new.count("'line_add_click'")
    new = new.replace("'line_add_click'", "'line_add_bottom'")
    if apply_:
        io.open(path, "w", encoding="utf-8", newline="").write(new)
    return f"{slug}: 挿入 → {where} ／ 既存イベント {n_bottom}件を line_add_bottom へ改名"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    for slug in TOOLS:
        print(" ", process(slug, a.apply))
    print("\n適用" if a.apply else "\n下見のみ（--apply で書き込む）")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    main()
