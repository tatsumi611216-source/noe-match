# minsalo テスト案件ワークスペース

「ChatGPT完全攻略」台本（10,000字）＋ Claude Code操作録画。
期限 2026/8/26／自主納品目標 **8/25**。

## ファイル

| ファイル | 中身 |
|---|---|
| `00_案件戦略.md` | 発注元の素性、評価軸の読み替え、勝ち筋と負け筋 |
| `01_参考動画分析.md` | 3チャンネルの素性、型抽出シート、解析プロンプト |
| `02_構成案.md` | 章立て・字数配分・フック文案・実演プロンプト |
| `03_ファクトチェック表.md` | 裏取り台帳。**納品物に添付する** |
| `04_録画用プロンプト集.md` | 録画で実際に打つプロンプト一式（表向き） |
| `05_録画と納品.md` | 撮影段取り、編集、納品パッケージ、提出前チェック |
| `06_返信文案.md` | 受諾返信・追加質問・納品・単価交渉 |
| `07_文字起こし一括取得.md` | yt-dlpで字幕をまとめて落とす手順 |
| `tools/ai_smell.py` | AI臭を機械検出するスクリプト |
| `tools/style_extract.py` | 文字起こしから文体の型を定量抽出する |
| `tools/netcheck.sh` | 到達できるドメインを確認する |

## 使い方

```bash
# AI臭チェック
python3 tools/ai_smell.py draft/script.md
python3 tools/ai_smell.py draft/script.md --verbose   # 全件表示

# 動作確認用サンプル
python3 tools/ai_smell.py draft/_sample_ai.md      # → 判定 D
python3 tools/ai_smell.py draft/_sample_human.md   # → 判定 A

# 文体の型を抽出（refs/ に .vtt / .srt / .txt を置く）
python3 tools/style_extract.py refs/ --out refs/style.md
python3 tools/style_extract.py refs/ --per-file
```

字幕の集め方は `07_文字起こし一括取得.md` を参照。

終了コードは 判定A/B で 0、C以下で 1。

## この環境の制約

`youtube.com` と `openai.com` はネットワークegressポリシーで遮断されている
（CONNECT に 403）。WebFetch・curl・Chromium いずれも同じ。

- **参考動画** … トオルさんのブラウザで視聴し、文字起こしを `refs/` に置く
- **一次ソース確認** … 同じくブラウザで実施し、`03_ファクトチェック表.md` を更新

環境の Network access を **Custom** にして該当ドメインを許可すれば、
以降の新規セッションからは到達可能になる（実行中のセッションには反映されない）。

## 新しいセッションを立てたときの最初の一手

```bash
bash tools/netcheck.sh
```

どのドメインに到達できるかが出る。
`403 / 000` は環境ポリシー側の遮断、`403`で到達している場合は先方サーバーのbot判定。
