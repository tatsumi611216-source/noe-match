#!/usr/bin/env bash
# fetch_transcripts.sh — 参考チャンネルの字幕とタイトル一覧をまとめて取得する。
#
# ※ このスクリプトは「YouTubeが見える環境」で実行すること。
#    クラウドセッションからは youtube.com が遮断されているため動かない。
#
#   bash tools/fetch_transcripts.sh                       # 既定の3チャンネル
#   bash tools/fetch_transcripts.sh <URL> [<URL> ...]     # 任意の動画/チャンネル
#   COUNT=30 bash tools/fetch_transcripts.sh              # 取得本数を変える
#
# 取得後、refs/ に置いてコミットまで行う。

set -uo pipefail

BRANCH="claude/chatgpt-mastery-test-order-bf485z"
COUNT="${COUNT:-15}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REFS="$HERE/refs"

# 既定のターゲット。テスト発注で指定された3本＋チャンネル一覧
DEFAULT_TARGETS=(
  "https://youtu.be/9v2_Znxjw4s"
  "https://youtu.be/nLwBLbySqUc"
  "https://youtu.be/nh22clwOA9U"
  "https://www.youtube.com/@ひかりのAI大学/videos"
  "https://www.youtube.com/@cocona_ai_school/videos"
)

if [ "$#" -gt 0 ]; then
  TARGETS=("$@")
else
  TARGETS=("${DEFAULT_TARGETS[@]}")
fi

# ---------------------------------------------------------------- 事前確認

if ! command -v yt-dlp >/dev/null 2>&1; then
  echo "yt-dlp が見つかりません。先に入れてください："
  echo "  pip install -U yt-dlp     （または brew install yt-dlp）"
  exit 1
fi

echo "yt-dlp $(yt-dlp --version)"
echo "保存先: $REFS"
echo "取得本数（チャンネル指定時）: $COUNT"
echo

mkdir -p "$REFS"
cd "$REFS" || exit 1

fail=0

# ---------------------------------------------------------------- 字幕

for url in "${TARGETS[@]}"; do
  echo "--- $url"

  # チャンネル/再生リストなら本数を絞る
  extra=()
  case "$url" in
    *"/videos"*|*"list="*|*"/@"*) extra=(--playlist-end "$COUNT") ;;
  esac

  if ! yt-dlp \
      --skip-download \
      --write-subs --write-auto-subs \
      --sub-langs "ja,ja-orig" \
      --sub-format vtt \
      --ignore-errors \
      --no-warnings \
      "${extra[@]}" \
      -o "%(channel)s_%(upload_date)s_%(title).60s.%(ext)s" \
      "$url"; then
    echo "  ! 取得に失敗しました: $url"
    fail=$((fail + 1))
  fi
  echo
done

# ---------------------------------------------------------------- タイトル一覧

echo "--- タイトルと再生数を取得"
for url in "${TARGETS[@]}"; do
  case "$url" in
    *"/videos"*|*"/@"*) ;;
    *) continue ;;
  esac
  name=$(echo "$url" | sed 's|.*@||; s|/.*||')
  yt-dlp --flat-playlist --ignore-errors --no-warnings \
    --print "%(view_count)s\t%(upload_date)s\t%(title)s" \
    --playlist-end 50 \
    "$url" > "titles_${name}.tsv" 2>/dev/null \
    && echo "  titles_${name}.tsv ($(wc -l < "titles_${name}.tsv") 本)"
done

# ---------------------------------------------------------------- 結果

echo
echo "================================================"
# _sample_* は動作確認用の同梱ファイル。実際の収穫と混ぜない。
n=$(find "$REFS" -maxdepth 1 -name '*.vtt' ! -name '_sample_*' 2>/dev/null | wc -l | tr -d ' ')
t=$(find "$REFS" -maxdepth 1 -name '*.tsv' ! -name '_sample_*' 2>/dev/null | wc -l | tr -d ' ')
echo " 字幕 ${n}件 / タイトル一覧 ${t}件"
[ "$fail" -gt 0 ] && echo " 失敗 ${fail}件（--ignore-errors で継続済み）"
echo "================================================"

if [ "$n" -eq 0 ] && [ "$t" -eq 0 ]; then
  echo
  echo "何も取得できませんでした。YouTubeに到達できているか確認してください。"
  exit 1
fi

# ---------------------------------------------------------------- コミット

cd "$HERE/../.." || exit 0
if [ -d .git ]; then
  echo
  echo "リポジトリにコミットします（refs/ は .gitignore 対象なので -f）"
  find work/minsalo-chatgpt-test/refs -maxdepth 1 \
    \( -name '*.vtt' -o -name '*.tsv' \) ! -name '_sample_*' \
    -exec git add -f {} +
  if git diff --cached --quiet; then
    echo "コミットする新規ファイルがありませんでした。"
  else
    git commit -q -m "参考チャンネルの字幕とタイトル一覧を追加（${n}本）" \
      && git push -u origin "$BRANCH" \
      && echo "プッシュしました。セッションで解析できます。"
  fi
fi

echo
echo "次にやること："
echo "  python3 tools/style_extract.py refs/ --out refs/style.md"
