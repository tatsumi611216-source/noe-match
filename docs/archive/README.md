# アーカイブ

サイト初期構築時（2026年7月以前）の、一回限りの作業レポートとスクリプト。
**現在の運用では参照しない。** 当時の判断の経緯を追うためだけに残している。

現行の運用ドキュメントは `agent/AGENT.md` と `agent/PHILOSOPHY.md`。

## 作業レポート

| ファイル | 内容 |
|---------|------|
| `SEO_EVALUATION_REPORT.md` | 初期のSEO評価 |
| `PHASE1_IMPLEMENTATION_SUMMARY.txt` `PHASE1_COMPLETE_VERIFICATION_REPORT.md` | Phase 1 の実装・検証記録 |
| `FAQ_IMPROVEMENT_PHASE1_REPORT.md` `FAQ_IMPROVEMENT_COMPLETE_SUMMARY.md` | FAQ改善の記録 |
| `GROUP_CF_LINK_IMPLEMENTATION_REPORT.md` `GROUP_CF_FAQ_SUPPLEMENT_REPORT.md` | グループC/Fの内部リンク・FAQ追加記録 |
| `IMPLEMENTATION_COMPLETE_REPORT.txt` | 全体の完了報告 |
| `report_internal_links_summary.txt` | 内部リンク集計 |
| `cleanup.txt` | 整理作業のメモ |

## スクリプト（動作しない）

| ファイル | 内容 |
|---------|------|
| `build_articles.py` | 初期48記事をmarkdownからHTML化した生成器。パスが `C:/Users/tatsu/...` 固定で、この環境では動かない |
| `complete_implementation.py` | 記事#38〜#48の一括実装スクリプト。同じく一回限りの用途 |

現在の記事生成はこれらを使わず、エージェントが
`articles/tokyo-guide/index.html` をテンプレートとして直接HTMLを書く方式。
