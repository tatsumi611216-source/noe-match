# -*- coding: utf-8 -*-
"""A8の提携プログラムCSVを差分して、新規承認された案件を報告する。

A8の管理画面はブラウザ自動化を受け付けない（合成クリックが無反応・a8mat URLの
抽出も拡張のガードで遮断される）ため、CSVの書き出しだけは人手で行う必要がある。
このスクリプトは「書き出されたCSVを比較する」部分だけを自動化する。

使い方:
    python scripts/a8_check.py           # デスクトップの最新2ファイルを比較
    python scripts/a8_check.py --all     # 全件を一覧表示

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
