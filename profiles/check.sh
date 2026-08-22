#!/usr/bin/env bash
# profiles/ に個人特定情報が混ざっていないかを機械的に確認する。
#
# このリポジトリは public なので、profiles/ に書いたものは誰でも読める。
# 各PFへ貼り付ける前と、コミットする前に必ず実行すること。
#
#   bash profiles/check.sh
#
# 検査の対象を2段に分けている。
#   1. 個人特定語（profiles/.ngwords）… profiles/ 配下の全文。説明文にも書いてはいけない
#   2. 組み込みパターン            … 各PFへ貼り付ける本文（``` で囲んだブロック）のみ。
#                                     匿名化ルールを説明する地の文まで拾うと誤検知になるため
#
# .ngwords（実名など、ファイルに書けない語）は1行1語で置く。.gitignore 済み。
# 無ければ組み込みパターンのみで検査する。

set -u
cd "$(dirname "$0")/.."

fail=0
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

hit()  { printf '  \033[31mNG\033[0m %s\n' "$1"; fail=1; }
ok()   { printf '  \033[32mok\033[0m %s\n' "$1"; }
note() { printf '  \033[33m--\033[0m %s\n' "$1"; }

# 貼り付け本文（``` で囲まれた部分）だけを file:line 付きで抜き出す
paste_blocks="$work/paste.txt"
: > "$paste_blocks"
for f in profiles/*.md; do
  awk -v f="$f" '
    /^```/ { inblk = !inblk; next }
    inblk  { printf "%s:%d:%s\n", f, NR, $0 }
  ' "$f" >> "$paste_blocks"
done

scan_paste() { # $1=正規表現 $2=説明
  if grep -nE -- "$1" "$paste_blocks" >/dev/null; then
    hit "$2"
    grep -E -- "$1" "$paste_blocks" | sed 's/^/       /'
  else
    ok "$2 — なし"
  fi
}

echo "== 1. 個人特定語（profiles/ 全文を検査）=="
if [ -f profiles/.ngwords ]; then
  found=0
  while IFS= read -r w; do
    case "$w" in ''|'#'*) continue ;; esac
    if grep -rqF -- "$w" profiles --exclude=.ngwords --exclude=check.sh; then
      hit "'$w' が profiles/ に含まれている"
      grep -rnF -- "$w" profiles --exclude=.ngwords --exclude=check.sh | sed 's/^/       /'
      found=1
    fi
  done < profiles/.ngwords
  [ "$found" -eq 0 ] && ok "登録語の混入なし"
else
  note "profiles/.ngwords が無い。profiles/.ngwords.example を複製して実名等を登録すると、この検査が効く"
fi

echo "== 2. 組み込みパターン（貼り付け本文のみ検査）=="
scan_paste '株式会社|有限会社|合同会社' '法人格つきの社名'
scan_paste '大学|大学院|高等学校' '学校名（学歴欄は省略する方針）'
scan_paste 'https?://|[a-z0-9-]+\.(com|net|jp|io|dev|app|me)([/ ]|$)' 'URL・ドメイン（自主開発サイトは伏せる）'
scan_paste 'RFP|提案書|PoC先' '提案先を特定しうる記述'
scan_paste '@[A-Za-z0-9_-]{3,}' 'アカウントID・メールアドレス'

echo "== 3. 埋め忘れ =="
if grep -n '【要記入】' "$paste_blocks" >/dev/null; then
  note "貼り付け本文に未記入が残っている（コミットは可・貼り付け前に埋める）"
  grep '【要記入】' "$paste_blocks" | sed 's/^/       /'
else
  ok "貼り付け本文の未記入なし"
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "OK: 貼り付け本文に個人特定情報の混入は検出されなかった"
else
  echo "NG: 上記を修正してからコミット・貼り付けを行うこと"
fi
exit "$fail"
