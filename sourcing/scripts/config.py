#!/usr/bin/env python3
"""APIキー等の設定を .env / 環境変数から読み込む。

秘密情報はリポジトリに置かない。sourcing/.env（.gitignore対象）に記載するか、
環境変数で渡す。.env.example を雛形として複製して使う。
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

GBIZINFO_TOKEN_ENV = "GBIZINFO_API_TOKEN"
EDINET_KEY_ENV = "EDINET_API_KEY"


def load_env(path: Path = ENV_PATH) -> None:
    """.env を読み込み os.environ に反映（既存の環境変数は上書きしない）。"""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


def _require(env_name: str, how: str) -> str:
    load_env()
    val = os.environ.get(env_name)
    if not val or val.startswith("YOUR_"):
        raise SystemExit(
            f"[設定エラー] {env_name} が未設定です。\n"
            f"  取得方法: {how}\n"
            f"  設定方法: sourcing/.env に {env_name}=（取得したキー） を記載、"
            f"または環境変数で export {env_name}=..."
        )
    return val


def get_gbizinfo_token() -> str:
    return _require(
        GBIZINFO_TOKEN_ENV,
        "https://info.gbiz.go.jp/api/ で無料登録→Web API利用申請（数日でトークン発行）",
    )


def get_edinet_key() -> str:
    return _require(
        EDINET_KEY_ENV,
        "https://api.edinet-fsa.go.jp/ で無料登録→APIキー(Subscription-Key)を発行",
    )
