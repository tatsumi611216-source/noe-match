#!/usr/bin/env python3
"""条件付きGET（ETag / Last-Modified）で差分取得を行う軽量HTTPクライアント。

採用ページは日々は変わらないため、前回の ETag/Last-Modified を送って
304（未更新）なら本文取得をスキップし、収集量を大幅に削減する。
キャッシュは data/http_cache.json に保持。file:// はテスト用に直読み対応。
"""
import gzip
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlparse, urlsplit, urlunsplit

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CACHE = BASE_DIR / "data" / "http_cache.json"
USER_AGENT = "NoeSourcingBot/0.1 (+contact: sales-tool; respects robots.txt)"


def to_ascii_url(url: str) -> str:
    """日本語を含むURL（IRI）を送信可能なASCII URLへ変換する。

    採用ページには /採用/ のような非ASCIIパスが実在し、そのまま urllib に渡すと
    UnicodeEncodeError で落ちる。既存の %xx は safe に '%' を含めて二重符号化を防ぐ。
    """
    parts = urlsplit(url)
    netloc = parts.netloc
    if any(ord(ch) > 127 for ch in netloc):  # 国際化ドメイン
        try:
            host = parts.hostname or ""
            netloc = netloc.replace(host, host.encode("idna").decode("ascii"))
        except (UnicodeError, AttributeError):
            pass
    path = quote(parts.path, safe="/%:@&=+$,~!*'()")
    query = quote(parts.query, safe="%:@&=+$,/?~!*'()")
    fragment = quote(parts.fragment, safe="%:@&=+$,/?~!*'()")
    return urlunsplit((parts.scheme, netloc, path, query, fragment))


class HttpCache:
    def __init__(self, path: Path = DEFAULT_CACHE):
        self.path = Path(path)
        self.data: dict = {}
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.data = {}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def fetch(self, url: str, timeout: int = 20, force: bool = False,
              max_bytes: int = 8_000_000) -> tuple[str | None, str]:
        """(本文, 状態) を返す。状態: 'fetched' / 'not_modified' / 'error:xxx'。

        304 のときは本文 None・状態 'not_modified'（呼び出し側で再取り込み不要と判断）。
        force=True で条件付きヘッダを送らず必ず本文を取得する
        （求人0件の企業はキャッシュに関わらず再探索したい場合に使う）。
        """
        parsed = urlparse(url)
        if parsed.scheme == "file":
            try:
                return Path(parsed.path).read_text(encoding="utf-8"), "fetched"
            except OSError as e:
                return None, f"error:{e}"

        prev = {} if force else self.data.get(url, {})
        headers = {"User-Agent": USER_AGENT}
        if prev.get("etag"):
            headers["If-None-Match"] = prev["etag"]
        if prev.get("last_modified"):
            headers["If-Modified-Since"] = prev["last_modified"]

        req = urllib.request.Request(to_ascii_url(url), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read(max_bytes)
                if raw[:2] == b"\x1f\x8b":  # sitemap.xml.gz など
                    try:
                        raw = gzip.decompress(raw)
                    except (OSError, EOFError):
                        pass
                body = raw.decode(resp.headers.get_content_charset() or "utf-8", "replace")
                self.data[url] = {
                    "etag": resp.headers.get("ETag"),
                    "last_modified": resp.headers.get("Last-Modified"),
                    "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                }
                return body, "fetched"
        except urllib.error.HTTPError as e:
            if e.code == 304:
                return None, "not_modified"
            return None, f"error:http{e.code}"
        except (urllib.error.URLError, TimeoutError) as e:
            return None, f"error:{e}"
