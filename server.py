#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マッチングアプリ情報サイト - Flask サーバー
スラッグベースのURL構造に対応
"""

from flask import Flask, send_from_directory, redirect, url_for
from pathlib import Path
import json
import re

app = Flask(__name__,
    static_folder=str(Path(__file__).parent),
    static_url_path='')

# 記事ディレクトリ
ARTICLES_DIR = Path(__file__).parent / "articles"
SLUG_MAPPING_FILE = Path(__file__).parent / "article_slugs.json"

# スラッグマッピングをメモリにロード
SLUG_TO_FILE = {}
if SLUG_MAPPING_FILE.exists():
    with open(SLUG_MAPPING_FILE, 'r', encoding='utf-8') as f:
        articles = json.load(f)
        for article in articles:
            slug = article['slug']
            html_file = article['slug'] + '.html'
            SLUG_TO_FILE[slug] = html_file

@app.route('/')
def index():
    """トップページ"""
    return send_from_directory(str(Path(__file__).parent), 'index.html')

@app.route('/articles/<slug>/')
@app.route('/articles/<slug>')
def serve_article(slug):
    """
    スラッグベースの記事ページを提供
    URL: /articles/matching-app-ranking-2026-1/
    """
    # スラッグからファイル名を検索
    html_file = SLUG_TO_FILE.get(slug)

    if html_file and (ARTICLES_DIR / html_file).exists():
        return send_from_directory(str(ARTICLES_DIR), html_file)

    # 見つからない場合は404
    return "記事が見つかりません", 404

@app.route('/articles/article_<int:article_id>.html')
@app.route('/articles/article_<int:article_id>')
def serve_legacy_article(article_id):
    """
    旧形式のURLをサポート（リダイレクト）
    /articles/article_001.html → /articles/2026top15-1/
    """
    # 旧形式のファイル名
    old_file = f"article_{article_id:03d}.html"

    # slugMapを探す
    for slug, html_file in SLUG_TO_FILE.items():
        if html_file == old_file:
            return redirect(f"/articles/{slug}/", code=301)

    # ファイルが見つからない場合、直接提供を試みる
    old_html_path = ARTICLES_DIR / old_file
    if old_html_path.exists():
        return send_from_directory(str(ARTICLES_DIR), old_file)

    return "記事が見つかりません", 404

@app.route('/<path:filename>')
def serve_static(filename):
    """静的ファイルを提供"""
    return send_from_directory(str(Path(__file__).parent), filename)

if __name__ == '__main__':
    print("=" * 70)
    print("[INFO] マッチングアプリサイト - Flask サーバー起動（スラッグ対応）")
    print("=" * 70)
    print(f"[INFO] ルートディレクトリ: {Path(__file__).parent}")
    print(f"[INFO] 記事ディレクトリ: {ARTICLES_DIR}")
    print(f"[INFO] スラッグマッピング: {len(SLUG_TO_FILE)}個")
    print("")
    print("[OK] サーバー起動 http://127.0.0.1:8080/")
    print("")
    print("URL形式:")
    print("  - スラッグベース: /articles/matching-app-ranking-2026-1/")
    print("  - 旧形式: /articles/article_001.html (301リダイレクト)")
    print("=" * 70)
    print("")

    app.run(host='127.0.0.1', port=8080, debug=False)
