# -*- coding: utf-8 -*-
"""ツール新設ゲート（2026-08-26 新設）

なぜ必要か: 8/13に公開したツール5本のうち4本は語の選定ミスで沈んだ
（saigenbyo 4表示・kekkon-shikin 0表示 vs garugaru 42表示・9位）。
勝敗を分けたのはツールという形式ではなく「SERP1ページ目に器具が
まだ無い語を選んだか」。この判定が手動のSERP実査に依存していたため、
機械ゲートにして選定ミスを構造的に防ぐ。

判定は3軸:
  A. 需要の広さ  … Googleサジェスト（serp_screen.py と同じ経路・認証不要）
  B. 需要の量    … aramakijake の月間推定検索数（2026-09-01 追加）
  C. 器具の空白  … DDG(Bing系)のSERP上位に計算機・診断・専業ドメインがあるか

Bを足した理由（2026-09-01）:
サジェストの本数は「語がどれだけ枝分かれしているか」であって「何人が検索するか」ではない。
8/31に結婚新生活支援バンクをサジェストだけで条件付きGOにしたが、検索数を測っていなかった。
既存ツールの実測で較正すると、成功と失敗はきれいに分かれた（Google推定・月間）:

  成功（1ページ目を取れている器具）      失敗（沈んだ器具）
    ガルガル期            6,480         婚活 タイプ 診断        8
    保育園 点数           1,920         再現婚               未収録
    子ども医療費 助成       1,040         結婚資金 計算          未収録
    こども誰でも通園制度       208

  → 成功群の下限は208、失敗群は8以下か未収録。しきい値は 200／100 に置く。

出力: GO / NO-GO / CHECK（判定根拠つき）
  GO    = 需要あり × 器具なし → 作ってよい
  NO-GO = 器具が既に居る、または需要ゼロ → 作らない
  CHECK = 判定が割れた → 人がSERPを目視してから決める

使い方:
  python scripts/tool_gate.py "ガルガル期 診断" "結婚式 費用 シミュレーション"

限界（正直に書く）:
- SERPはDDG(Bing系)のみ。Googleの1ページ目とはズレることがある。
  GOでも公開判断の前にGoogleを1回目視するのが安全（CHECKなら必須）。
- タイトル文字列での器具検出なので、タイトルに器具語を含まない器具は見逃す。
"""
import io
import re
import sys
import json
import time
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# 器具をタイトルで検出する語
INSTRUMENT_WORDS = (
    "診断", "チェッカー", "チェックリスト", "チェックシート", "シミュレーター",
    "シュミレーター", "シミュレーション", "計算機", "計算ツール", "自動計算",
    "早見表", "カレンダー", "判定ツール", "テスト",
)

# 計算・診断の専業ドメイン（実測で確認したら追記する）
INSTRUMENT_DOMAINS = {
    # 2026-08-24〜26 のSERP実査で確認
    "kurasim.com", "calclife.net", "keisan-navi.jp", "jptools.jp",
    "www.simraku.com", "seikatsuhi.com", "life-cost-simulation.com",
    "keisan.casio.jp", "kakeibo-line.com", "cards-life.com",
    "kurashicostlab.com", "tools.arealme.com", "shindanmaker.com",
}

# 事業者の本丸ドメイン（ここが上位に並ぶ語も NO-GO 寄り）
VENDOR_HINTS = (
    "zexy", "hana-yume", "mwed", "weddingpark", "niwaka",
    "en-konkatsu", "naresome", "goodcoming",
)


def suggests(q):
    url = ("https://suggestqueries.google.com/complete/search?client=firefox&hl=ja&q="
           + urllib.parse.quote(q))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=15))
        return d[1] if len(d) > 1 else []
    except Exception:
        return None  # 取得失敗は None（0件と区別する）


MIN_VOLUME_GO = 200      # 実績のある器具の下限（こども誰でも通園制度 208）
MIN_VOLUME_CHECK = 100   # これ未満は失敗群と同じ帯


def volume(q):
    """aramakijake の月間推定検索数。(yahoo, google) / "unlisted" / None を返す。

    None は取得失敗（判定に使わない）、"unlisted" は掲載はされたが数値が無い＝
    計測下限未満。POSTは通らないのでGETで叩く。1つ目がYahoo・2つ目がGoogleで、
    比は常に1:4（aramakijakeの推定モデル）。
    """
    url = ("https://aramakijake.jp/keyword/index.php?keyword="
           + urllib.parse.quote(q))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        html_ = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    except Exception:
        return None
    i = html_.find("月間推定検索数")
    if i < 0:
        return "unlisted"
    nums = re.findall(r">\s*([\d,]+)\s*<", html_[i:i + 1200])[:2]
    if len(nums) < 2:
        return "unlisted"
    return (int(nums[0].replace(",", "")), int(nums[1].replace(",", "")))


def serp_titles(q):
    """DDG lite のSERPから (domain, title) を上位から返す"""
    req = urllib.request.Request(
        "https://lite.duckduckgo.com/lite/",
        data=urllib.parse.urlencode({"q": q, "kl": "jp-jp"}).encode(),
        headers={"User-Agent": UA})
    try:
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    except Exception:
        return None
    rows = []
    for m in re.finditer(
            r'<a[^>]+href="(?:/l/\?uddg=)?(https?[^"&]+)[^"]*"[^>]*class="result-link"[^>]*>(.*?)</a>',
            html, re.S):
        url = urllib.parse.unquote(m.group(1))
        dom = urllib.parse.urlparse(url).netloc
        title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if dom and "duckduckgo" not in dom:
            rows.append((dom, title))
    if not rows:  # 別マークアップのフォールバック
        for m in re.finditer(r"<a[^>]+href=\"(https?://[^\"]+)\"[^>]*>([^<]{10,120})</a>", html):
            dom = urllib.parse.urlparse(m.group(1)).netloc
            if dom and "duckduckgo" not in dom and "w3.org" not in dom:
                rows.append((dom, m.group(2).strip()))
    return rows[:10]


def judge(q):
    sug = suggests(q)
    time.sleep(1.0)
    vol = volume(q)
    time.sleep(1.0)
    serp = serp_titles(q)

    demand = None if sug is None else len(sug)
    gvol = vol[1] if isinstance(vol, tuple) else None
    instr_hits, vendor_hits = [], []
    if serp:
        for dom, title in serp:
            if dom in INSTRUMENT_DOMAINS or any(w in title for w in INSTRUMENT_WORDS):
                # 自サイトは器具占有に数えない
                if "noe-match.com" not in dom:
                    instr_hits.append((dom, title[:40]))
            if any(v in dom for v in VENDOR_HINTS):
                vendor_hits.append(dom)

    if demand == 0:
        verdict, why = "NO-GO", "サジェスト0件＝検索されていない"
    elif vol == "unlisted":
        verdict, why = ("NO-GO",
                        "月間検索数が計測下限未満（aramakijake未収録）。"
                        "沈んだ器具3本はすべてこの帯だった")
    elif gvol is not None and gvol < MIN_VOLUME_CHECK:
        verdict, why = "NO-GO", f"月間検索数 約{gvol}（Google推定）＝小さすぎる"
    elif gvol is not None and gvol < MIN_VOLUME_GO:
        verdict, why = ("CHECK",
                        f"月間検索数 約{gvol}（Google推定）。実績のある器具の下限208に届かない")
    elif instr_hits and len(instr_hits) >= 2:
        verdict, why = "NO-GO", f"SERP上位に器具{len(instr_hits)}件（{instr_hits[0][0]}等）＝空白ではない"
    elif instr_hits:
        verdict, why = "CHECK", f"SERPに器具1件（{instr_hits[0][0]}）。競合の強さを目視で確認"
    elif len(vendor_hits) >= 3:
        verdict, why = "CHECK", f"事業者本丸{len(vendor_hits)}件が上位。商材直撃語の可能性"
    elif serp is None or demand is None:
        verdict, why = "CHECK", "SERPまたはサジェストの取得に失敗。手動確認"
    elif demand <= 1:
        verdict, why = "CHECK", f"需要が薄い（サジェスト{demand}件）。空白でも人が来ない可能性"
    else:
        verdict, why = "GO", (f"需要あり（サジェスト{demand}件"
                              + (f"・月間約{gvol}" if gvol else "") + "）× SERP上位に器具なし")

    return {"q": q, "verdict": verdict, "why": why, "volume": vol,
            "suggests": (sug or [])[:6], "serp": (serp or [])[:6],
            "instruments": instr_hits, "vendors": vendor_hits}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    for q in sys.argv[1:]:
        r = judge(q)
        print(f"\n[{r['verdict']}] {r['q']}")
        print(f"  理由: {r['why']}")
        v = r.get("volume")
        if isinstance(v, tuple):
            print(f"  月間推定検索数: Google {v[1]:,} / Yahoo {v[0]:,}")
        elif v == "unlisted":
            print("  月間推定検索数: 未収録（計測下限未満）")
        if r["suggests"]:
            print(f"  サジェスト: {' / '.join(r['suggests'])}")
        for dom, title in r["serp"]:
            mark = "🔧" if (dom, title[:40]) in r["instruments"] else "  "
            print(f"  {mark} {dom:32} {title[:44]}")
        time.sleep(1.0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
