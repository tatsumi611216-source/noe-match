# -*- coding: utf-8 -*-
"""A8の提携プログラムCSVと台帳を突合し、未使用案件を「結婚軸の接続先」付きで一覧化する。

なぜ必要か（2026-08-09）:

軸展開モデルは「結婚の周辺からテーマを探す」のではなく、
**儲かる案件を先に決めて、結婚という入り口を後から付ける**という順序で動く。
そのため提携済みで未使用の案件リストが、そのまま記事テーマの候補リストになる。

2026-08-09時点で提携182件に対し、台帳 AGENT.md に載っているのは73件。
残り109件は受け皿が無く、1円も生んでいない。

**CSVには報酬（単価）列が無い**（プログラムID/名称/広告主/カテゴリ/開始日/終了日/提携日の7列）。
単価はA8の個別ページにしかないため、そこは人手かブラウザ操作で取る必要がある。

使い方:
    python scripts/program_queue.py          # 最新CSVで agent/program_queue.md を再生成
"""
import csv
import collections
import glob
import io
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "agent", "program_queue.md")
SEARCH_DIRS = [
    os.path.expanduser(r"~\Downloads"),
    os.path.expanduser(r"~\OneDrive\デスクトップ"),
    os.path.expanduser(r"~\Desktop"),
]

# カテゴリ → (結婚軸のどこに接続するか, 受け皿にする記事)
# 「接続が弱い」と書いたものは、無理に繋ぐと記事の質が落ちるので保留扱い。
MAP = {
    "就職・転職": ("結婚を機の転職・共働きの働き方", "kekkon-tenshoku-guide / tenshoku-riyu-honne の下層"),
    "在宅ワーク": ("育児と両立する働き方", "kosodate-zaitaku-guide の下層"),
    "その他（仕事情報）": ("結婚後の働き方", "同上"),
    "資格取得": ("結婚後のキャリア形成・産休中の学習", "新規クラスタ"),
    "総合（学び・資格）": ("同上", "新規クラスタ"),
    "保険": ("結婚後の保険見直し", "kekkon-hoken-minaoshi の2社目。YMYL枠・1記事1箇所"),
    "金融": ("新婚の家計・カード", "fuufu-credit-kanri / kekkon-chokin-mokuhyou"),
    "引越": ("新生活の引越し", "shinkon-seikatsu-guide / dousei-hajimekata"),
    "インテリア": ("新居の家具", "shinkyo-kagu-yosan"),
    "家電": ("新生活の家電", "kaden-rental-vs-kounyu"),
    "リサイクル": ("同居で家財が2倍になる問題", "新規"),
    "生鮮食品": ("共働きの食事", "tomobataraki-shokuji-data"),
    "加工食品": ("季節行事・おせち", "shinkon-osechi"),
    "その他（グルメ・食品）": ("同上", "shinkon-osechi"),
    "総合（グルメ・食品）": ("同上", "shinkon-osechi"),
    "スキンケア": ("婚活・式前の身だしなみ", "bridal-esthe-guide / mens-make-konkatsu"),
    "コスメ・メイク": ("同上", "同上"),
    "ファッション小物": ("婚活・式の服装", "新規"),
    "服": ("同上", "新規"),
    "占い": ("婚活で行き詰まったときの相談先", "konkatsu-soudan-saki。景表法・効果の断定厳禁"),
    "動画": ("おうちデート", "ouchi-date-sakuhin"),
    "総合（インターネット接続）": ("新生活の回線", "futari-hikari-kaisen"),
    "その他（暮らし）": ("新生活の暮らし", "要個別判断"),
    "起業・会社設立": ("配偶者の独立・自営", "接続が弱い。保留"),
    "サーバー": ("夫婦の副業", "接続が弱い。保留"),
    "ショッピングモール": ("新生活の買い物", "接続が弱い。保留"),
    "ASP": ("対象外（自社向け）", "使わない"),
}


def latest_csv():
    files = []
    for d in SEARCH_DIRS:
        files += glob.glob(os.path.join(d, "programs_*.csv"))
    if not files:
        raise SystemExit("programs_*.csv が見つからない。A8管理画面 → プログラム管理 → 提携中プログラム → CSVダウンロード")
    return max(files, key=os.path.getmtime)


def ledger_names():
    """AGENT.md の表から案件名を拾う。括弧書き（ASP名・登録日）は落として本体だけ使う。"""
    out = []
    for line in io.open(os.path.join(BASE, "agent", "AGENT.md"), encoding="utf-8"):
        if not line.startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) < 3:
            continue
        name = re.sub(r"（.*", "", cells[1].strip()).strip()
        if len(name) > 1:
            out.append(name)
    return out


def main():
    path = latest_csv()
    rows = list(csv.reader(io.open(path, encoding="cp932", errors="replace")))[1:]
    known = ledger_names()
    unused = [r for r in rows
              if len(r) >= 4 and not any(k in r[1] or k in r[2] for k in known)]

    by_cat = collections.defaultdict(list)
    for r in unused:
        by_cat[r[3]].append(r)

    L = []
    L.append("# 未使用案件 × 結婚軸の接続先（記事キュー）")
    L.append("")
    L.append("**自動生成: `scripts/program_queue.py`。手で編集しない。**")
    L.append("")
    L.append("元データ: `{}`".format(os.path.basename(path)))
    L.append("")
    L.append("提携 {} 件のうち、台帳 `AGENT.md` に記載が無い **{} 件**。".format(len(rows), len(unused)))
    L.append("軸展開モデルは「儲かる案件を先に決めて、結婚という入り口を後から付ける」順序で動くため、")
    L.append("このリストがそのまま記事テーマの候補になる（テーマ探索が不要になる）。")
    L.append("")
    L.append("## 使い方（3ステップ）")
    L.append("")
    L.append("1. 下表から案件を選ぶ")
    L.append("2. **単価をA8の個別ページで確認する**（CSVに報酬列が無いため、ここは自動化できていない）")
    L.append("3. **想定クエリのSERPを実測する** ← ここが勝負を決める")
    L.append("")
    L.append("**3を飛ばして書かないこと。** 2026-08-09に14テーマを実測して、生き残ったのは1つだけだった。")
    L.append("別セッションの実測でも、狙うクエリの型によって表示到達率が 23.5 パーセント 〜 68.8 パーセントと3倍違う。")
    L.append("")
    L.append("## 優先度")
    L.append("")
    L.append("**「結婚と仕事・働き方」は3記事しかないのに、未使用案件の最多が就職・転職。**")
    L.append("資格取得・在宅ワークも同じ「結婚後のキャリア」クラスタに乗るので、ここが最大の空白。")
    L.append("")

    for cat, items in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        dest, note = MAP.get(cat, ("要個別判断", "—"))
        L.append("## {}（{}件）".format(cat, len(items)))
        L.append("")
        L.append("- **接続先**: {}".format(dest))
        L.append("- **受け皿**: {}".format(note))
        L.append("")
        for r in items:
            L.append("- `{}` {}".format(r[0], r[1][:70]))
        L.append("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(L) + "\n")
    print("生成: agent/program_queue.md")
    print("提携 {} / 未使用 {} / カテゴリ {}".format(len(rows), len(unused), len(by_cat)))


if __name__ == "__main__":
    main()
