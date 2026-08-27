# -*- coding: utf-8 -*-
"""GSCの実績を日別に永久保存する（2026-08-28 新設）

なぜ急ぐか:
**GSCは16ヶ月でデータが消える。保存していない期間は永久に取り返せない。**
既存の `fetch_gsc.py` は毎回 `agent/gsc_data.json` を上書きしていた（"w"モード）。
つまり直近28日ぶんしか手元になく、それも次回実行で消えていた。
ドメインが動き出したのが2026年6月なので、**いま全期間を取れば1日も失わずに済む**。

`fetch_gsc.py` の他の問題も直してある:
- rowLimit 500固定 → 25,000（APIの上限）＋ startRow でページネーション
- 集計値のみ → **日別×クエリ×ページ**の粒度で保存（後から何とでも集計できる）
- 上書き → 日ごとに別ファイル。一度書いたら二度と書き換えない

粒度を日別にしておく理由は、9月中旬の判定でも、その先のベイズ判定（Q4-6-14）でも、
**「いつ何が起きたか」が要る**から。月次の集計しか無いと、施策の前後を切り分けられない。

使い方:
  python scripts/gsc_archive.py              # 未取得の日を埋める（差分だけ）
  python scripts/gsc_archive.py --backfill   # 取得可能な全期間をさかのぼる
  python scripts/gsc_archive.py --stats      # 保存状況を表示するだけ
"""
import datetime
import io
import json
import os
import sys
import urllib.parse

KEY_PATH = r"C:\Users\tatsu\matching-app\secrets\noe-gsc-key.json"
SITE = "https://www.noe-match.com/"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(REPO, "agent", "gsc_archive")

# GSCは16ヶ月保持。それより前は取りようがない。
RETENTION_DAYS = 480
# GSCの確定は2〜3日遅れる。直近2日は取りに行っても後から数字が変わるので保存しない。
LAG_DAYS = 3
PAGE_SIZE = 25000


def session():
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    creds = service_account.Credentials.from_service_account_file(
        KEY_PATH, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    return AuthorizedSession(creds)


def _query(s, day, dims):
    """1日ぶんを指定の次元で、ページネーションしながら全部取る"""
    url = ("https://www.googleapis.com/webmasters/v3/sites/%s/searchAnalytics/query"
           % urllib.parse.quote(SITE, safe=""))
    rows, start = [], 0
    while True:
        body = {"startDate": str(day), "endDate": str(day),
                "rowLimit": PAGE_SIZE, "startRow": start}
        if dims:
            body["dimensions"] = dims
        r = s.post(url, json=body)
        if r.status_code != 200:
            raise RuntimeError("GSC %s: %s" % (r.status_code, r.text[:200]))
        got = r.json().get("rows", [])
        rows += got
        if len(got) < PAGE_SIZE:
            break
        start += PAGE_SIZE
        if start > 200000:
            print("  警告: 20万行を超えた。打ち切る")
            break
    return rows


def fetch_day(s, day):
    """3層で取る。

    クエリ次元を入れると**匿名化で表示の半分以上が落ちる**（2026-08-28実測:
    2026-08-20は 次元なし120表示 → query次元55表示）。GSCの仕様であって不具合ではない。
    だから「正しい合計」と「クエリの内訳」は別物として両方保存する。
    - total:        次元なし。サイト全体の正確な合計
    - by_page:      ページ別。ほぼ欠落しない
    - by_query_page: クエリ×ページ。匿名化で落ちるが、語の動きを見るにはこれしかない
    device / country は足しても情報が増えなかった（同実測）ので取らない。
    """
    return {
        "total": _query(s, day, None),
        "by_page": _query(s, day, ["page"]),
        "by_query_page": _query(s, day, ["query", "page"]),
    }


def path_for(day):
    return os.path.join(ARCHIVE, "%s.json" % day)


def save(day, packs):
    os.makedirs(ARCHIVE, exist_ok=True)
    t = packs["total"]
    out = {
        "date": str(day),
        "site": SITE,
        "fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "total": ({"clicks": t[0]["clicks"], "imp": t[0]["impressions"],
                   "ctr": round(t[0]["ctr"], 6), "pos": round(t[0]["position"], 2)}
                  if t else {"clicks": 0, "imp": 0, "ctr": 0, "pos": 0}),
        "by_page": [{"p": r["keys"][0], "clicks": r["clicks"], "imp": r["impressions"],
                     "pos": round(r["position"], 2)} for r in packs["by_page"]],
        "by_query_page": [{"q": r["keys"][0], "p": r["keys"][1], "clicks": r["clicks"],
                           "imp": r["impressions"], "pos": round(r["position"], 2)}
                          for r in packs["by_query_page"]],
    }
    io.open(path_for(day), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    return out


def stats():
    if not os.path.isdir(ARCHIVE):
        print("アーカイブなし")
        return
    fs = sorted(f for f in os.listdir(ARCHIVE) if f.endswith(".json"))
    if not fs:
        print("アーカイブは空")
        return
    tc = ti = qc = qi = npg = 0
    for f in fs:
        d = json.load(io.open(os.path.join(ARCHIVE, f), encoding="utf-8"))
        t = d.get("total") or {}
        tc += t.get("clicks", 0)
        ti += t.get("imp", 0)
        npg += len(d.get("by_page", []))
        for r in d.get("by_query_page", []):
            qc += r["clicks"]
            qi += r["imp"]
    print("保存日数: %d日（%s 〜 %s）" % (len(fs), fs[0][:-5], fs[-1][:-5]))
    print("合計（正確）  click %s / 表示 %s" % ("{:,}".format(tc), "{:,}".format(ti)))
    print("クエリ内訳    click %s / 表示 %s（匿名化で表示の%.0f%%が落ちている）"
          % ("{:,}".format(qc), "{:,}".format(qi), (1 - qi / ti) * 100 if ti else 0))
    print("ページ行の延べ数: %s" % "{:,}".format(npg))
    d0 = datetime.date.fromisoformat(fs[0][:-5])
    d1 = datetime.date.fromisoformat(fs[-1][:-5])
    have = {f[:-5] for f in fs}
    miss = [str(d0 + datetime.timedelta(days=i)) for i in range((d1 - d0).days + 1)
            if str(d0 + datetime.timedelta(days=i)) not in have]
    print("期間内の欠損: %d日 %s" % (len(miss), miss[:5]))


def main():
    if "--stats" in sys.argv:
        stats()
        return
    today = datetime.date.today()
    last = today - datetime.timedelta(days=LAG_DAYS)
    first = (today - datetime.timedelta(days=RETENTION_DAYS)
             if "--backfill" in sys.argv else last - datetime.timedelta(days=45))

    s = session()
    days = [first + datetime.timedelta(days=i) for i in range((last - first).days + 1)]
    todo = [d for d in days if not os.path.exists(path_for(d))]
    # さかのぼりは新しい日から古い日へ走査する。古い側から走ると、サイトが存在しなかった
    # 期間の空データで即座に打ち切ってしまう（2026-08-28にこれをやった）。
    if "--backfill" in sys.argv:
        todo.sort(reverse=True)
    print("対象 %d日 ／ 未取得 %d日（%s 〜 %s）"
          % (len(days), len(todo), first, last))

    empty_streak = 0
    got_any = 0
    for d in todo:
        try:
            packs = fetch_day(s, d)
        except RuntimeError as e:
            print("  %s 取得失敗: %s" % (d, e))
            continue
        out = save(d, packs)
        got_any += 1
        if out["total"]["imp"] == 0:
            empty_streak += 1
        else:
            empty_streak = 0
            print("  %s  click %3d  表示 %5d  ページ %3d  クエリ行 %4d"
                  % (d, out["total"]["clicks"], out["total"]["imp"],
                     len(out["by_page"]), len(out["by_query_page"])))
        # さかのぼりで空が続いたら、それ以前はデータが無いので打ち切る
        if "--backfill" in sys.argv and empty_streak >= 30:
            print("  空が30日続いたので打ち切り（%s より前はデータなし）" % d)
            break
        if got_any % 50 == 0:
            print("  ... %d日 取得済み（現在 %s）" % (got_any, d))
    print("新規保存: %d日" % got_any)
    stats()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
