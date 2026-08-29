# -*- coding: utf-8 -*-
"""バンクの鮮度監視（2026-08-29 新設）

バンク戦略の堀は「更新が続くこと」。各バンクの CHECKED（一次確認日）の経過日数を
測り、30日を超えたら再確認対象として報告する。確認日を明記する型なので、
元データが古いまま置くとその確認日が嘘になる。

再確認の成果物は2つ:
  1. バンクの CHECKED 更新（変わっていなければ日付のみ、変われば数値ごと）
  2. 差分があれば LINE配信「今月変わった点」の材料にする

実行: python scripts/bank_freshness.py   （報告のみ・変更しない）
運用: 毎週金曜の巡回で実行。30日超が出た週に再確認を行う。
"""
import datetime
import importlib
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

BANKS = ["_seikonritsu_data", "_soudanjo_hiyou_data", "_app_ryokin_data",
         "_byoji_funin_data", "_kodomo_iryo_data", "_daretsu_data", "_sangocare_data"]

WARN_DAYS = 30


def parse_date(s):
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", s or "")
    return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def main():
    today = datetime.date.today()
    stale = []
    print("バンク鮮度（今日: %s / 警告しきい値: %d日）" % (today, WARN_DAYS))
    for name in BANKS:
        mod = importlib.import_module(name)
        d = parse_date(getattr(mod, "CHECKED", ""))
        if not d:
            print("  %-24s CHECKED が読めない ← 要修正" % name); stale.append(name); continue
        age = (today - d).days
        mark = " ← 再確認" if age > WARN_DAYS else ""
        print("  %-24s 確認 %s（%d日前）%s" % (name, d, age, mark))
        if age > WARN_DAYS:
            stale.append(name)
    # data_bank.md の期限も表示
    p = os.path.join(ROOT, "agent", "data_bank.md")
    if os.path.exists(p):
        t = io.open(p, encoding="utf-8").read()
        dl = re.findall(r"(2026-\d{2}-\d{2})[^\n]*", t)
        near = sorted(set(x for x in dl if x >= str(today)))[:4]
        if near:
            print("\n台帳の直近期限:", " / ".join(near))
    print("\n再確認対象: %d本" % len(stale))
    return 1 if stale else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
