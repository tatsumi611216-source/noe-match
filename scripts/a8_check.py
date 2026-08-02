# -*- coding: utf-8 -*-
"""A8の提携プログラムCSVを差分して、新規承認された案件を報告する。

A8の管理画面はブラウザ自動化を受け付けない（合成クリックが無反応・a8mat URLの
抽出も拡張のガードで遮断される）ため、CSVの書き出しだけは人手で行う必要がある。
このスクリプトは「書き出されたCSVを比較する」部分だけを自動化する。

使い方:
    python scripts/a8_check.py           # デスクトップの最新2ファイルを比較
    python scripts/a8_check.py --all     # 全件を一覧表示
    python scripts/a8_check.py --gaps    # 収益化できていない記事の受け皿になる提携済み案件を探す

前提: A8管理画面 → プログラム管理 → 提携中プログラム → CSVダウンロード で
      `programs_<ID>_<YYYYMMDDhhmmss>.csv` がデスクトップに保存されていること。
"""
import csv
import glob
import io
import os
import sys

DESKTOP = os.path.expanduser(r"~\OneDrive\デスクトップ")

# CSVの置き場所。ブラウザの既定の保存先はダウンロードフォルダなので、
# デスクトップだけを見ていると「書き出したのに見つからない」が起きる
# （2026-08-01に実際に発生し、8/1分の差分を丸ごと取りこぼしかけた）。
SEARCH_DIRS = [
    DESKTOP,
    os.path.expanduser(r"~\Downloads"),
    os.path.expanduser(r"~\Desktop"),
]

# noe-match にとって価値のあるカテゴリ（ここに入るものだけを「要検討」として強調する）
PRIORITY_CATEGORIES = {"婚活", "恋愛", "ウエディング"}
RELEVANT_CATEGORIES = PRIORITY_CATEGORIES | {
    "引越", "家電", "回線", "インテリア", "リサイクル",
    "ファッション小物", "総合（ギフト）", "生鮮食品",
    "その他（暮らし）", "その他（金融・投資・保険）", "総合（金融・投資・保険）",
}

# サイトの立ち位置と噛み合わないため、承認されても使わないと決めたカテゴリ・広告主
EXCLUDED_CATEGORIES = {"占い", "在宅ワーク", "ASP", "ポイントサービス・懸賞"}

# 収益化できていない記事の受け皿として不足しているジャンル（agent/affiliate_gaps.md）。
#
# 判定は「カテゴリ列 → 除外カテゴリ → 語句」の順に行う。CSVの4列目（カテゴリ）が
# 最も信頼できるので、まずそれを見る。プログラム名への単一キーワード部分一致は
# 誤爆するため使わない（「楽天」だけで拾うと『楽天グルメ大賞受賞のおせち等…
# 【ちこり村本店サイト】』がクレジットカード案件として報告されてしまう）。
# ブランド名は必ずカテゴリ語との共起でのみ該当とする。
#
#   categories      : カテゴリ列がこれなら、プログラム名を見るまでもなく該当
#   deny_categories : カテゴリ名にこの語を含むなら、語句が一致しても該当としない
#   phrases         : 単独で該当と断定できるジャンル固有の複合語
#   brands×qualifiers : ブランド名は「カード」等のカテゴリ語と同時に出た時だけ該当
#
# 目的は2つ:
#   1. 提携済みなのに台帳（AGENT.md）に載っておらず、使われていない案件を発見する
#      （AGENT.mdは「A8提携153件」と記録している一方、台帳の登録は約40件しかない）
#   2. 申請後、承認されたかを確認する
GAP_GENRES = {
    "クレジットカード": {
        # A8の正式カテゴリ名。カードローン・保険等の金融カテゴリは別物なので入れない
        "categories": ("クレジットカード",),
        "deny_categories": ("グルメ", "食品", "ファッション", "服", "コスメ",
                            "スキンケア", "インテリア", "グッズ", "写真"),
        "phrases": ("クレジットカード", "クレジット決済", "ゴールドカード",
                    "カード発行", "年会費無料", "クレカ"),
        "brands": ("JCB", "VISA", "アメックス", "セゾン", "楽天", "三井住友",
                   "エポス", "オリコ", "ジャックス", "ダイナース", "イオン", "ライフ"),
        "qualifiers": ("カード", "card", "クレジット"),
        "articles": ("fuufu-credit-kanri", "gosyugi-shiharai-houhou",
                     "shinkon-ryokou-credit", "futari-kouza-kanri"),
    },
    "妊活サプリ": {
        # 「サプリメント」カテゴリはダイエット等も含むため、カテゴリ単独では該当にしない
        "categories": (),
        "deny_categories": ("就職", "仕事情報", "婚活", "恋愛"),
        "phrases": ("妊活", "葉酸", "不妊", "プレコンセプション", "マイシード",
                    "ミトコア", "mitas", "ミタス"),
        "brands": ("マカ", "亜鉛", "ルイボス"),
        "qualifiers": ("サプリ", "妊活", "栄養"),
        "articles": ("dansei-ninkatsu-guide", "mitas-formen-kuchikomi",
                     "mitocore-kuchikomi", "myseed-kuchikomi"),
    },
    "ブライダルインナー": {
        # 「下着・インナー」カテゴリは一般下着も含むため、カテゴリ単独では該当にしない
        "categories": (),
        "deny_categories": ("就職", "仕事情報", "グルメ", "食品"),
        "phrases": ("ブライダルインナー", "ウェディングインナー", "ブライダル下着"),
        "brands": ("ブライダル", "ウエディング", "ウェディング", "花嫁", "結婚式"),
        "qualifiers": ("インナー", "下着", "ランジェリー", "補正"),
        "articles": ("bridal-inner-guide",),
    },
    "国際結婚・ビザ": {
        "categories": (),
        "deny_categories": ("就職", "仕事情報", "グルメ", "食品"),
        "phrases": ("国際結婚", "配偶者ビザ", "在留資格", "帰化申請", "入管"),
        "brands": ("行政書士", "弁護士", "司法書士"),
        "qualifiers": ("ビザ", "在留", "国際結婚", "配偶者"),
        "articles": ("kokusai-kekkon-guide",),
    },
}

# 台帳（AGENT.md）に既に登録済みの広告主。ここに無いものが「使われていない提携」。
LEDGER_HINTS = (
    "ユーブライド", "マリッシュ", "ALG", "ビジモ", "ハローストレージ", "原一",
    "結婚相談所比較", "白衣コン", "レバウェル", "エクセレンス", "匠本舗", "NULL",
    "クレカリ", "引越し侍", "家電レンタル", "Oisix", "オイシックス", "シャディ",
    "THE KISS", "PARTY", "ハナユメ", "naco-do", "Photojoy", "挨拶状",
    "リファスタ", "OTOCON", "縁結び", "ヒーローマリッジ", "RIVERET", "L&Co",
    "保険ランドリー", "街角相談所", "ABEMA", "WOWOW", "スカパー", "田舎婚",
    "ピュア婚", "R婚", "フィオーレ", "ベルロード", "バチェラーデート", "ぽちゃ婚",
)


def in_ledger(advertiser, name):
    blob = (advertiser or "") + (name or "")
    return any(h.lower() in blob.lower() for h in LEDGER_HINTS)


def match_genre(cat, adv, name, spec):
    """プログラムがジャンルに該当すれば判定理由を、しなければ None を返す。

    信頼できるカテゴリ列を最優先し、プログラム名は補助にとどめる。
    """
    cat = cat or ""
    if cat in spec["categories"]:
        return "カテゴリ"
    if any(d in cat for d in spec["deny_categories"]):
        return None

    blob = ((adv or "") + (name or "")).lower()
    for phrase in spec["phrases"]:
        if phrase.lower() in blob:
            return "語句:%s" % phrase
    for brand in spec["brands"]:
        if brand.lower() not in blob:
            continue
        for qual in spec["qualifiers"]:
            if qual.lower() in blob:
                return "%s×%s" % (brand, qual)
    return None


def report_gaps(programs):
    """提携中プログラムの中から、空白ジャンルを埋められる案件を探す。"""
    print("=== 収益化できていない記事の受け皿になりうる提携済み案件 ===\n")
    any_hit = False
    for genre, spec in GAP_GENRES.items():
        hits = []
        for pid, (cat, adv, name) in programs.items():
            if cat in EXCLUDED_CATEGORIES:
                continue
            why = match_genre(cat, adv, name, spec)
            if why:
                hits.append((pid, cat, adv, name, in_ledger(adv, name), why))
        print("■ %s（受け皿記事: %s）" % (genre, "・".join(spec["articles"])))
        if not hits:
            print("   提携済み案件なし → A8のプログラム検索で新規申請が必要\n")
            continue
        any_hit = True
        for pid, cat, adv, name, known, why in sorted(hits, key=lambda x: x[4]):
            mark = "台帳済" if known else "★未使用"
            print("   [%s] %s | %s | %s | %s（判定: %s）"
                  % (mark, pid, cat, adv, name[:46], why))
        print()
    if any_hit:
        print("★未使用 の案件は、提携済みなのに AGENT.md の台帳に載っておらず")
        print("記事にも置かれていない。管理画面から a8mat URL をコピーし、")
        print("台帳へ『リンクURL・使用ルール・置いてよい記事・1記事あたりの上限』を追記すること。")
    return 0


def load(path):
    """プログラムID -> (カテゴリ, 広告主, プログラム名) の辞書を返す。"""
    with io.open(path, encoding="cp932", errors="replace") as f:
        rows = list(csv.reader(f))
    return {r[0]: (r[3], r[2], r[1]) for r in rows[1:] if len(r) >= 7 and r[0]}


def find_csvs():
    """置き場所を横断して集め、更新時刻順に並べる。

    同じファイルがデスクトップとダウンロードの両方にある場合は、
    ファイル名（書き出し時刻を含む）で重複を除く。
    """
    found = {}
    for d in SEARCH_DIRS:
        for p in glob.glob(os.path.join(d, "programs_*.csv")):
            name = os.path.basename(p)
            if name not in found or os.path.getmtime(p) > os.path.getmtime(found[name]):
                found[name] = p
    return sorted(found.values(), key=os.path.getmtime)


def classify(category):
    if category in EXCLUDED_CATEGORIES:
        return "除外"
    if category in PRIORITY_CATEGORIES:
        return "最優先"
    if category in RELEVANT_CATEGORIES:
        return "検討"
    return "対象外"


def main():
    files = find_csvs()
    if not files:
        print("CSVが見つかりません。A8管理画面から提携中プログラムを書き出してください。")
        print("  探した場所: %s" % " / ".join(SEARCH_DIRS))
        return 1

    if "--gaps" in sys.argv:
        return report_gaps(load(files[-1]))

    if "--all" in sys.argv:
        latest = load(files[-1])
        print("最新ファイル: %s（%d件）\n" % (os.path.basename(files[-1]), len(latest)))
        for pid, (cat, adv, name) in sorted(latest.items(), key=lambda x: x[1][0]):
            print("%-6s %s | %s | %s" % (classify(cat), pid, cat, name[:60]))
        return 0

    if len(files) < 2:
        print("比較対象が1件しかありません（%s）。" % os.path.basename(files[0]))
        print("次回の書き出し後に再実行してください。")
        return 0

    prev_path, curr_path = files[-2], files[-1]
    prev, curr = load(prev_path), load(curr_path)
    added = [k for k in curr if k not in prev]
    removed = [k for k in prev if k not in curr]

    print("比較: %s → %s" % (os.path.basename(prev_path), os.path.basename(curr_path)))
    print("      %d件 → %d件\n" % (len(prev), len(curr)))

    if not added and not removed:
        print("変化なし。")
        return 0

    if added:
        # 最優先 → 検討 → 対象外 → 除外 の順に並べる
        order = {"最優先": 0, "検討": 1, "対象外": 2, "除外": 3}
        added.sort(key=lambda k: order[classify(curr[k][0])])
        print("=== 新規承認 %d件 ===" % len(added))
        for pid in added:
            cat, adv, name = curr[pid]
            print("[%s] %s | %s | %s" % (classify(cat), pid, cat, name[:70]))
        n_pri = sum(1 for k in added if classify(curr[k][0]) == "最優先")
        if n_pri:
            print("\n→ 最優先が%d件あります。受け皿記事の有無を確認し、"
                  "無ければ keyword_queue.json に積んでください。" % n_pri)
            print("→ 広告リンク（a8mat URL）はブラウザ自動化では取得できないため、"
                  "管理画面から手動でコピーする必要があります。")

    if removed:
        print("\n=== 提携終了・消滅 %d件 ===" % len(removed))
        for pid in removed:
            cat, adv, name = prev[pid]
            print("%s | %s | %s" % (pid, cat, name[:70]))
        print("\n→ サイト内に該当リンクが残っていないか確認してください:")
        print('   grep -rl "a8mat" articles/ | xargs grep -l "<該当の広告主>"')

    return 0


if __name__ == "__main__":
    sys.exit(main())
