# -*- coding: utf-8 -*-
"""公開したURLをIndexNowに送る（Bing/Yandexが即時にクロールする）。

使い方: python scripts/indexnow_submit.py <URL> [<URL> ...]
Googleには効かないが、当サイトの流入は非Googleが約7割なのでここが効く。
鍵ファイルは https://www.noe-match.com/<KEY>.txt に配置済み。
"""
import json
import sys
import urllib.request

KEY = "28fb2874520d40719aa81fc0618e863b"
HOST = "www.noe-match.com"


def submit(urls):
    body = json.dumps({
        "host": HOST, "key": KEY,
        "keyLocation": "https://%s/%s.txt" % (HOST, KEY),
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.indexnow.org/IndexNow", data=body,
        headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow: HTTP %d（%d件）" % (r.status, len(urls)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    submit(sys.argv[1:])
