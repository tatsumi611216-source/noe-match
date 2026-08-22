# setup_studio.ps1 — 録画専用のクリーンな作業場を作る
#
#   powershell -ExecutionPolicy Bypass -File work\minsalo-chatgpt-test\tools\setup_studio.ps1
#
# リポジトリから「画面に映してよいファイルだけ」を %USERPROFILE%\daihon-studio に展開する。
# 00(戦略)/04(録画演出)/05(納品段取り)/06(返信文案)/09(マスタープロンプト) は
# 手の内なので絶対にコピーしない。

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Base = Split-Path -Parent $Here                     # work/minsalo-chatgpt-test
$Dst  = Join-Path $env:USERPROFILE "daihon-studio"

New-Item -ItemType Directory -Force -Path $Dst, "$Dst\tools", "$Dst\refs", "$Dst\draft" | Out-Null

# --- 見せてよいものだけ ---
Copy-Item (Join-Path $Base "templates\CLAUDE.md")        (Join-Path $Dst "CLAUDE.md") -Force
Copy-Item (Join-Path $Base "tools\ai_smell.py")          "$Dst\tools\" -Force
Copy-Item (Join-Path $Base "02_構成案.md")               $Dst -Force
Copy-Item (Join-Path $Base "03_ファクトチェック表.md")   $Dst -Force
Copy-Item (Join-Path $Base "08_技法カタログ.md")         $Dst -Force
if (Test-Path (Join-Path $Base "refs\style.md")) {
    Copy-Item (Join-Path $Base "refs\style.md") "$Dst\refs\" -Force
}
if (Test-Path (Join-Path $Base "draft\初稿.md")) {
    Copy-Item (Join-Path $Base "draft\初稿.md") "$Dst\draft\" -Force
}

Write-Host ""
Write-Host "録画用の作業場を作りました: $Dst"
Write-Host ""
Write-Host "中身（これしか映らない）:"
Get-ChildItem -Recurse -File $Dst | ForEach-Object { Write-Host ("  " + $_.FullName.Substring($Dst.Length+1)) }
Write-Host ""
Write-Host "次の手順:"
Write-Host "  1. Claude Code未導入なら:  irm https://claude.ai/install.ps1 | iex"
Write-Host "  2. cd $Dst"
Write-Host "  3. claude   (初回はログインを求められます)"
Write-Host "  4. 録画開始 → cat CLAUDE.md から"
