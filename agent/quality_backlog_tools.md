# ツールの是正バックログ（2026-09-19 新設）

`scripts/factory_audit.py` の tools/ 検査（新ツールの出荷基準・`agent/AGENT.md` 2026-09-19）で、
**検査を入れた時点で既に違反していた既存ツール**を積むファイル。ここに載っているツールは
「既知バックログ」扱いになり、CIを赤にしない。**新しく作ったツールは載せない**（基準を満たしてから出す）。
是正したら行を削除する。判定ロック中（`agent/seo/improvement-log.json` の locks[]）のツールは、ロック明けまで触らない。

検査項目: title 32字以内（末尾の【…】とサイト名を除く）／`id="result…"` の領域内に LINE CTA（lin.ee）／
広告アンカーに `id="aff-..."`／広告アンカーの `rel` に `sponsored`／PR表記。

## 一覧（2026-09-19 実測・23本／全27本）

| ツール | 違反 |
|---|---|
| tools/app-kakin-hikaku | title 35字（サフィックス除く・32字以内） ／ #result 内に LINE CTA が無い |
| tools/app-kekkonritsu-data | title 42字（サフィックス除く・32字以内） ／ 結果領域（id="result…"）が見つからない |
| tools/daredemo-tsuen-jichitai | title 45字（サフィックス除く・32字以内） |
| tools/fugenbyo-check | title 33字（サフィックス除く・32字以内） ／ #result 内に LINE CTA が無い |
| tools/funin-josei-jichitai | title 40字（サフィックス除く・32字以内） |
| tools/garugaru-check | title 36字（サフィックス除く・32字以内） |
| tools/hitorioya-shien-jichitai | title 39字（サフィックス除く・32字以内） |
| tools/kekkon-shikin-keisanki | title 46字（サフィックス除く・32字以内） ／ #result 内に LINE CTA が無い |
| tools/kekkon-shinseikatsu-jichitai | 結果領域（id="result…"）が見つからない |
| tools/kekkon-yarukoto | title 35字（サフィックス除く・32字以内） ／ 結果領域（id="result…"）が見つからない |
| tools/kodomo-iryohi-jichitai | title 47字（サフィックス除く・32字以内） |
| tools/koisaihi-simulator | title 34字（サフィックス除く・32字以内） ／ 結果領域（id="result…"）が見つからない |
| tools/konkatsu-type-shindan | 結果領域（id="result…"）が見つからない |
| tools/kosodate-shien-23ku | title 50字（サフィックス除く・32字以内） ／ #result 内に LINE CTA が無い |
| tools/nyuseki-calendar | title 48字（サフィックス除く・32字以内） ／ 結果領域（id="result…"）が見つからない |
| tools/rikongo-seikatsuhi | title 35字（サフィックス除く・32字以内） ／ 結果領域（id="result…"）が見つからない |
| tools/saigenbyo-check | title 34字（サフィックス除く・32字以内） ／ #result 内に LINE CTA が無い |
| tools/sango-recovery-check | title 48字（サフィックス除く・32字以内） ／ #result 内に LINE CTA が無い |
| tools/sangokea-ryokin | title 39字（サフィックス除く・32字以内） |
| tools/seikatsuhi-simulator | title 33字（サフィックス除く・32字以内） ／ #result 内に LINE CTA が無い |
| tools/seikonritsu-hikaku | title 41字（サフィックス除く・32字以内） ／ #result 内に LINE CTA が無い |
| tools/soudanjo-hiyou-sim | title 34字（サフィックス除く・32字以内） ／ #result 内に LINE CTA が無い |
| tools/soudanjo-simulator | title 37字（サフィックス除く・32字以内） ／ #result 内に LINE CTA が無い |
