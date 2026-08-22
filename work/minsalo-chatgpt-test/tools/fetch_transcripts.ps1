# fetch_transcripts.ps1 — Windows PowerShell用（bash不要）
#
#   powershell -ExecutionPolicy Bypass -File work\minsalo-chatgpt-test\tools\fetch_transcripts.ps1
#
# 字幕とタイトル一覧を取得し、refs/ に置いてコミット・プッシュまで行う。
# 対象を変える場合は引数にURLを渡す。取得本数は環境変数 COUNT で変更（既定15）。

$ErrorActionPreference = "Continue"
$Branch = "claude/chatgpt-mastery-test-order-bf485z"
$Count = if ($env:COUNT) { $env:COUNT } else { "15" }

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Base = Split-Path -Parent $Here
$Refs = Join-Path $Base "refs"
$Root = Split-Path -Parent (Split-Path -Parent $Base)
New-Item -ItemType Directory -Force -Path $Refs | Out-Null

# yt-dlp は PATH に依存しないよう python -m で呼ぶ
python -m yt_dlp --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "yt-dlp が見つかりません。先に実行してください:  pip install -U yt-dlp"
    exit 1
}

$Targets = @(
    "https://youtu.be/9v2_Znxjw4s",
    "https://youtu.be/nLwBLbySqUc",
    "https://youtu.be/nh22clwOA9U",
    "https://www.youtube.com/@ひかりのAI大学/videos",
    "https://www.youtube.com/@cocona_ai_school/videos"
)
if ($args.Count -gt 0) { $Targets = $args }

Write-Host "保存先: $Refs"
Write-Host "取得本数(チャンネル指定時): $Count"
Write-Host ""

Push-Location $Refs

# ---- 字幕 ----
foreach ($url in $Targets) {
    Write-Host "--- $url"
    $extra = @()
    if ($url -match "/videos|list=|/@") { $extra = @("--playlist-end", "$Count") }
    python -m yt_dlp --skip-download --write-subs --write-auto-subs `
        --sub-langs "ja,ja-orig" --sub-format vtt `
        --ignore-errors --no-warnings @extra `
        -o "%(channel)s_%(upload_date)s_%(title).60s.%(ext)s" $url
    Write-Host ""
}

# ---- タイトルと再生数 ----
Write-Host "--- タイトルと再生数を取得"
foreach ($url in $Targets) {
    if ($url -notmatch "/videos|/@") { continue }
    $name = (($url -split "@")[-1] -split "/")[0]
    python -m yt_dlp --flat-playlist --ignore-errors --no-warnings `
        --print "%(view_count)s`t%(upload_date)s`t%(title)s" `
        --playlist-end 50 $url | Out-File -Encoding utf8 ("titles_" + $name + ".tsv")
    Write-Host ("  titles_" + $name + ".tsv")
}

Pop-Location

# ---- 集計（_sample_* は同梱の動作確認用なので除外）----
$vtt = @(Get-ChildItem $Refs -Filter *.vtt | Where-Object { $_.Name -notlike "_sample_*" })
$tsv = @(Get-ChildItem $Refs -Filter *.tsv | Where-Object { $_.Name -notlike "_sample_*" })
Write-Host "================================================"
Write-Host ("  字幕 " + $vtt.Count + "件 / タイトル一覧 " + $tsv.Count + "件")
Write-Host "================================================"

if ($vtt.Count -eq 0 -and $tsv.Count -eq 0) {
    Write-Host "何も取得できませんでした。YouTubeに到達できているか確認してください。"
    exit 1
}

# ---- コミットしてプッシュ ----
Push-Location $Root
foreach ($f in ($vtt + $tsv)) { git add -f $f.FullName }
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m ("参考チャンネルの字幕とタイトル一覧を追加（" + $vtt.Count + "本）")
    git push -u origin $Branch
    Write-Host "プッシュしました。あとはセッション側が自動で解析します。"
} else {
    Write-Host "コミットする新規ファイルがありませんでした。"
}
Pop-Location
