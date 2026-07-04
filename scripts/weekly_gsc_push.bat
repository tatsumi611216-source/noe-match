@echo off
rem Phase 2 データ供給：GSC取得→リポジトリへプッシュ（毎週日曜23:00・Windowsタスクスケジューラから実行）
cd /d C:\Users\tatsu\noe-match-local
git pull origin main
set PYTHONIOENCODING=utf-8
python scripts\fetch_gsc.py
if errorlevel 1 exit /b 1
git add agent/gsc_data.json
git -c user.name="Noe" -c user.email="tatsumi611216@gmail.com" commit -m "Update GSC data (weekly fetch)"
git push origin main
