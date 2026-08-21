#!/usr/bin/env bash
# netcheck.sh — 新しいセッションで、どのドメインに到達できるかを確認する。
#
#   bash tools/netcheck.sh
#
# 403 = 環境のネットワークポリシーで遮断されている（許可リストに未追加）
# 200 = 到達できている
# それ以外 = 到達はしているが、先方のサーバー側で弾かれている

HOSTS=(
  "https://help.openai.com/en/articles/6825453-chatgpt-release-notes|OpenAI 更新履歴"
  "https://help.openai.com/en/articles/9624314-model-release-notes|OpenAI モデル更新履歴"
  "https://openai.com/chatgpt/pricing/|OpenAI 料金ページ"
  "https://openai.com/products/release-notes/|OpenAI リリースノート"
  "https://www.youtube.com/watch?v=9v2_Znxjw4s|YouTube 動画ページ"
  "https://youtu.be/9v2_Znxjw4s|YouTube 短縮URL"
  "https://www.googleapis.com/|Google APIs"
)

printf "%-6s %-28s %s\n" "CODE" "対象" "判定"
printf -- "------------------------------------------------------------------\n"

for entry in "${HOSTS[@]}"; do
  url="${entry%%|*}"; label="${entry##*|}"
  code=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 25 "$url" 2>/dev/null)
  rc=$?
  if [ "$rc" -ne 0 ] || [ "$code" = "000" ]; then
    verdict="✗ 遮断（CONNECT拒否）"
  elif [ "$code" = "200" ]; then
    verdict="✓ 到達"
  elif [ "$code" = "403" ] || [ "$code" = "429" ]; then
    verdict="△ 到達したが先方が拒否（bot判定の可能性）"
  else
    verdict="△ 到達（HTTP $code）"
  fi
  printf "%-6s %-28s %s\n" "$code" "$label" "$verdict"
done

echo
echo "--- プロキシ側の記録 ---"
curl -sS --max-time 15 "${HTTPS_PROXY}/__agentproxy/status" 2>/dev/null \
  | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    print('  取得できませんでした'); sys.exit()
f = d.get('recentRelayFailures') or []
if not f:
    print('  遮断の記録なし')
for x in f[-8:]:
    print(f\"  {x.get('host','?'):<32} {x.get('detail','')}\")
"
