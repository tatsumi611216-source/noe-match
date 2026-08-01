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
# カテゴリ名はA8側の表記揺れがあるため、カテゴリではなく
# プログラム名・広告主名へのキーワード一致で拾う。
#
# 目的は2つ:
#   1. 提携済みなのに台帳（AGENT.md）に載っておらず、使われていない案件を発見する
#      （AGENT.mdは「A8提携153件」と記録している一方、台帳の登録は約40件しかない）
#   2. 申請後、承認されたかを確認する
GAP_GENRES = {
    "クレジットカード": {
        "keywords": ("カード", "card", "クレジット", "JCB", "VISA", "アメックス",
                     "セゾン", "楽天", "三井住友", "エポス", "オリコ", "ジャックス"),
        "articles": ("fuufu-credit-kanri", "gosyugi-shiharai-houhou",
                     "shinkon-ryokou-credit", "futari-kouza-kanri"),
    },
    "妊活サプリ": {
        "keywords": ("妊活", "葉酸", "マカ", "亜鉛", "サプリ", "ミトコ", "マイシード",
                     "mitas", "ミタス", "プレコンセプション"),
        "articles": ("dansei-ninkatsu-guide", "mitas-formen-kuchikomi",
                     "mitocore-kuchikomi", "myseed-kuchikomi"),
    },
    "ブライダルインナー": {
        "keywords": ("インナー", "下着", "ランジェリー", "ブライダルインナー", "補正"),
        "articles": ("bridal-inner-guide",),
    },
    "国際結婚・ビザ": {
        "keywords": ("行政書士", "ビザ", "在留", "国際結婚"),
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


def report_gaps(programs):
    """提携中プログラムの中から、空白ジャンルを埋められる案件を探す。"""
    print("=== 収益化できていない記事の受け皿になりうる提携済み案件 ===\n")
    any_hit = False
    for genre, spec in GAP_GENRES.items():
        hits = []
        for pid, (cat, adv, name) in programs.items():
            if cat in EXCLUDED_CATEGORIES:
                continue
            blob = (adv or "") + (name or "")
            if any(k.lower() in blob.lower() for k in spec["keywords"]):
                hits.append((pid, cat, adv, name, in_ledger(adv, name)))
        print("■ %s（受け皿記事: %s）" % (genre, "・".join(spec["articles"])))
        if not hits:
            print("   提携済み案件なし → A8のプログラム検索で新規申請が必要\n")
            continue
        any_hit = True
        for pid, cat, adv, name, known in sorted(hits, key=lambda x: x[4]):
            mark = "台帳済" if known else "★未使用"
            print("   [%s] %s | %s | %s | %s" % (mark, pid, cat, adv, name[:46]))
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
    pattern = os.path.join(DESKTOP, "programs_*.csv")
    files = sorted(glob.glob(pattern), key=os.path.getmtime)
    return files


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
        print("  保存先の想定: %s" % DESKTOP)
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
