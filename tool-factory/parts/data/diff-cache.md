# 部品: diff-cache（差分キャッシュ）

- カテゴリ: data ／ 由来: web-data-pipeline ／ 使用実績: web-data-pipeline, keiba-yoso

## 何をする部品か

定期実行タスクで前回取得データを再利用し、取得量を大幅に削減する。

## 組み込みブロック

```markdown
### 差分キャッシュ

**適用判断：**
- データの鮮度要件を決める（例：[3日]以内なら再利用可）
- 前回キャッシュから同じIDのレコードを抽出して再利用
- 更新が確実なものだけ再取得（例：[当日更新があった対象]）

**実装パターン：**
- キャッシュは {日付}_cache.json に保存し、各レコードに cached_at を持たせる
- needs_refresh(item, max_age_days=[3]) で鮮度判定してから取得リストを作る
```

```python
def load_cache(cache_path):
    if not os.path.exists(cache_path):
        return {}
    with open(cache_path) as f:
        cache = json.load(f)
    return {item['id']: item for item in cache.get('items', [])}

def needs_refresh(cached_item, max_age_days=3):
    from datetime import datetime, timezone
    if not cached_item.get('cached_at'):
        return True
    cached_at = datetime.fromisoformat(cached_item['cached_at'])
    return (datetime.now(timezone.utc) - cached_at).days > max_age_days
```

## カスタマイズポイント

- 鮮度要件（max_age_days）は案件で必ず明示する
- 「必ず再取得する条件」（当日イベントがあった対象など）を案件ごとに定義する
