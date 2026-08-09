"""
auto_parser.py — 汎用Webデータパーサー

Webページから read_page / get_page_text / javascript_tool で取得したテキストを
自動判定してパースする。

フォーマット:
  at     - Accessibility Tree形式 (link "...", generic "...")
  plain  - プレーンテキスト形式 (値が1行ずつ)
  csv    - CSV形式 (カンマ区切り)

Usage:
  python auto_parser.py input.txt --record-start "2024/" --fields date,name,value
  python auto_parser.py input_dir/ --record-start "2024/" --output all.json
"""

import json, re, sys, os, argparse
from typing import Optional


def detect_format(text: str) -> str:
    """テキストのフォーマットを自動判定する。"""
    first = text[:500]
    if 'link "' in first or 'generic "' in first:
        return 'at'
    for line in text.strip().split('\n')[:10]:
        if line.count(',') >= 4 and re.match(r'\d{4}', line):
            return 'csv'
    return 'plain'


def extract_at_values(block: str) -> list[str]:
    """ATブロックからlink/genericの値を順番通りに抽出する。"""
    values = []
    for m in re.finditer(r'(?:link|generic) "([^"]*)"', block):
        values.append(m.group(1))
    return values


def parse_at(text: str, record_start_pattern: str, max_records: int = 100) -> list[dict]:
    """
    AT形式をパースする。
    record_start_pattern: レコード開始を示すlink/genericの値パターン（正規表現）
    """
    records = []
    lines = text.strip().split('\n')

    i = 0
    while i < len(lines) and len(records) < max_records:
        line = lines[i].strip()
        # レコード開始行を探す
        start_match = re.search(r'(?:link|generic) "([^"]*)"', line)
        if not start_match or not re.search(record_start_pattern, start_match.group(1)):
            i += 1
            continue

        # 次のレコード開始まで収集
        block_lines = [line]
        j = i + 1
        while j < len(lines):
            next_line = lines[j].strip()
            next_match = re.search(r'(?:link|generic) "([^"]*)"', next_line)
            if next_match and re.search(record_start_pattern, next_match.group(1)):
                break
            block_lines.append(next_line)
            j += 1

        block = '\n'.join(block_lines)
        values = extract_at_values(block)
        if values:
            records.append({'_raw_values': values, '_raw_block': block})
        i = j

    return records


def parse_plain(text: str, record_start_pattern: str, max_records: int = 100) -> list[dict]:
    """プレーンテキスト形式をパースする。"""
    records = []
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]

    i = 0
    while i < len(lines) and len(records) < max_records:
        if not re.search(record_start_pattern, lines[i]):
            i += 1
            continue

        record_lines = [lines[i]]
        j = i + 1
        while j < len(lines):
            if re.search(record_start_pattern, lines[j]):
                break
            record_lines.append(lines[j])
            j += 1

        if len(record_lines) >= 1:
            records.append({'_raw_values': record_lines})
        i = j

    return records


def parse_csv(text: str, max_records: int = 100) -> list[dict]:
    """CSV形式をパースする。"""
    records = []
    for line in text.strip().split('\n'):
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) >= 2:
            records.append({'_raw_values': parts})
        if len(records) >= max_records:
            break
    return records


def parse_file(filepath: str, record_start_pattern: str = r'\d{4}', max_records: int = 100) -> dict:
    """
    ファイルを自動判定してパースする。

    Args:
        filepath: 入力ファイルパス
        record_start_pattern: レコード開始を示すパターン（正規表現）
        max_records: 最大レコード数

    Returns:
        {'format': str, 'record_count': int, 'records': list[dict]}
    """
    with open(filepath, encoding='utf-8') as f:
        text = f.read()

    if not text.strip():
        return {'format': 'empty', 'record_count': 0, 'records': []}

    fmt = detect_format(text)

    if fmt == 'at':
        records = parse_at(text, record_start_pattern, max_records)
    elif fmt == 'csv':
        records = parse_csv(text, max_records)
    else:
        records = parse_plain(text, record_start_pattern, max_records)

    return {
        'format': fmt,
        'record_count': len(records),
        'records': records
    }


def parse_directory(dirpath: str, record_start_pattern: str = r'\d{4}',
                    max_records: int = 100) -> dict:
    """ディレクトリ内の全.txtファイルをパースする。"""
    results = {}
    for fname in sorted(os.listdir(dirpath)):
        if not fname.endswith('.txt'):
            continue
        item_id = fname.replace('.txt', '')
        fpath = os.path.join(dirpath, fname)
        results[item_id] = parse_file(fpath, record_start_pattern, max_records)

    return {
        'total_files': len(results),
        'total_records': sum(r['record_count'] for r in results.values()),
        'items': results
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Auto-detect and parse web data files')
    parser.add_argument('input', help='Input .txt file or directory of .txt files')
    parser.add_argument('--record-start', default=r'\d{4}',
                        help='Regex pattern marking the start of a record (default: \\d{4})')
    parser.add_argument('--max-records', type=int, default=100,
                        help='Max records per file (default: 100)')
    parser.add_argument('--output', '-o', help='Output JSON file (default: stdout)')
    args = parser.parse_args()

    if os.path.isdir(args.input):
        result = parse_directory(args.input, args.record_start, args.max_records)
    else:
        result = parse_file(args.input, args.record_start, args.max_records)

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(out)
        print(f"Saved: {args.output}")
    else:
        print(out)
