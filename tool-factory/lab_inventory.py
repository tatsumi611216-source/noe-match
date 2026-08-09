#!/usr/bin/env python3
"""Noeツールラボ — 在庫棚卸し

parts/ と skills/ を走査して、いま何を持っているかを一覧にする。
カタログ（PARTS_CATALOG.md）との突き合わせも行い、
「部品ファイルはあるのにカタログに載っていない」等の抜けを検知する。

使い方:
    python3 tool-factory/lab_inventory.py           # 棚卸し結果を表示
    python3 tool-factory/lab_inventory.py --json    # JSON で出力
"""
import argparse
import json
import os
import re

LAB = os.path.dirname(os.path.abspath(__file__))
PARTS = os.path.join(LAB, 'parts')
SKILLS = os.path.join(LAB, 'skills')
CATALOG = os.path.join(LAB, 'PARTS_CATALOG.md')
INSTALLED = os.path.expanduser('~/.claude/skills')

# 標準装備のスキル。ラボが作ったものではないので取り込み対象外。
STOCK_SKILLS = {
    'docx', 'pdf', 'pptx', 'xlsx', 'morning', 'skill-creator',
    'session-start-hook', 'artifact-design', 'artifact-diagramming',
    'artifact-capabilities', 'dataviz', 'update-config', 'keybindings-help',
    'simplify', 'loop', 'claude-api', 'run', 'init', 'security-review',
    'fewer-permission-prompts', 'code-review',
}

BLOCKS = [
    ('input', '① INPUT', '入力'),
    ('quality', '② QUALITY', '品質'),
    ('process', '③ PROCESS', '中核処理'),
    ('data', '④ DATA', 'データ'),
    ('output', '⑤ OUTPUT', '出力'),
    ('integration', '⑥ INTEGRATION', '連携'),
    ('safety', '⑦ SAFETY', '安全'),
]


def read_part(path):
    """部品ファイルから機能・由来・使用実績を抜き出す"""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    meta = re.search(r'^- カテゴリ:\s*(.+?)\s*／\s*由来:\s*(.+?)\s*／\s*使用実績:\s*(.+?)$',
                     text, re.M)
    desc = re.search(r'## 何をする部品か\s*\n+(.+?)(?:\n\n|\n#)', text, re.S)
    return {
        'category': meta.group(1).strip() if meta else '',
        'origin': meta.group(2).strip() if meta else '',
        'used_by': meta.group(3).strip() if meta else '',
        'summary': ' '.join(desc.group(1).split())[:70] if desc else '',
    }


def scan_parts():
    parts = {}
    for block, _, _ in BLOCKS:
        d = os.path.join(PARTS, block)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith('.md'):
                continue
            pid = f'{block}/{fn[:-3]}'
            parts[pid] = read_part(os.path.join(d, fn))
    return parts


def scan_skills():
    skills = []
    if not os.path.isdir(SKILLS):
        return skills
    for name in sorted(os.listdir(SKILLS)):
        path = os.path.join(SKILLS, name, 'SKILL.md')
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            text = f.read()
        # キャンバス表に書かれた部品IDを拾う（設計の記録として残してある場合）
        used = sorted(set(re.findall(r'\b((?:input|quality|process|data|output|integration|safety)/[a-z-]+)\b', text)))
        skills.append({'name': name, 'parts_referenced': used})
    return skills


def usage_from_parts(parts):
    """部品ファイルの「使用実績」見出しから、部品→ツールの対応を拾う。

    取り込んだツールは SKILL.md 本文に部品IDを書いていないため、
    本文の走査だけでは利用実績を数えられない。**部品ファイルの見出しが正の記録**。
    （PARTS_CATALOG.md の使用実績列はその写し。ズレは check_usage_drift が検知する）
    """
    usage = {}
    for pid, meta in parts.items():
        used = meta.get('used_by', '')
        names = re.findall(r'[a-z][a-z0-9-]{2,}', used)
        usage[pid] = sorted({n for n in names if n not in ('未使用',)})
    return usage


def check_intake():
    """インストール済みだがラボに取り込まれていないツールを検知する。

    ラボの外で作った・もらったツールは、分解して部品化するまで資産にならない。
    黙って増えていくと重複製造が復活するので、棚卸しのたびに炙り出す。
    """
    if not os.path.isdir(INSTALLED):
        return {'untracked': [], 'not_installed': []}
    installed = {d for d in os.listdir(INSTALLED)
                 if os.path.exists(os.path.join(INSTALLED, d, 'SKILL.md'))}
    tracked = {d for d in os.listdir(SKILLS)} if os.path.isdir(SKILLS) else set()
    return {
        'untracked': sorted(installed - tracked - STOCK_SKILLS),
        'not_installed': sorted(tracked - installed),
    }


def check_usage_drift(parts):
    """部品ファイルの使用実績と、カタログ表の使用実績のズレを検知する。

    同じことを2箇所に書いている以上ズレる。片方を直したらもう片方も直す。
    """
    if not os.path.exists(CATALOG):
        return []
    with open(CATALOG, encoding='utf-8') as f:
        catalog = f.read()
    drift = []
    for pid, meta in parts.items():
        row = re.search(r'^\|\s*' + re.escape(pid) + r'\s*\|[^|]*\|[^|]*\|\s*([^|]+?)\s*\|',
                        catalog, re.M)
        if not row:
            continue
        cat_names = set(re.findall(r'[a-z][a-z0-9-]{2,}', row.group(1)))
        file_names = set(re.findall(r'[a-z][a-z0-9-]{2,}', meta.get('used_by', '')))
        if cat_names != file_names:
            drift.append((pid, sorted(file_names), sorted(cat_names)))
    return drift


def check_catalog(parts):
    """カタログに載っていない部品／ファイルのない部品を検知する"""
    if not os.path.exists(CATALOG):
        return {'missing_in_catalog': sorted(parts), 'missing_file': []}
    with open(CATALOG, encoding='utf-8') as f:
        catalog = f.read()
    listed = set(re.findall(r'\|\s*((?:input|quality|process|data|output|integration|safety)/[a-z-]+)\s*\|', catalog))
    return {
        'missing_in_catalog': sorted(set(parts) - listed),
        'missing_file': sorted(listed - set(parts)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    parts = scan_parts()
    skills = scan_skills()
    issues = check_catalog(parts)
    intake = check_intake()
    drift = check_usage_drift(parts)

    # 部品の利用回数。SKILL.md本文の参照とカタログの使用実績を統合して数える
    # （取り込んだツールは本文に部品IDを書いていないため、カタログ側が主な情報源になる）
    cat_usage = usage_from_parts(parts)
    usage = {}
    for pid in parts:
        names = set(cat_usage.get(pid, []))
        for s in skills:
            if pid in s['parts_referenced']:
                names.add(s['name'])
        usage[pid] = len(names)

    if args.json:
        print(json.dumps({'parts': parts, 'skills': skills, 'issues': issues,
                          'intake': intake, 'usage': usage, 'usage_drift': drift},
                         ensure_ascii=False, indent=1))
        return

    print(f'━━━ Noeツールラボ 在庫棚卸し ━━━')
    print(f'部品 {len(parts)}点 ／ ツール {len(skills)}点\n')

    for block, label, ja in BLOCKS:
        ids = [p for p in parts if p.startswith(block + '/')]
        if not ids:
            print(f'{label} {ja}：なし')
            continue
        print(f'{label} {ja}（{len(ids)}点）')
        for pid in sorted(ids):
            mark = '★' * min(3, usage[pid])
            print(f'  {pid:32s} {mark:3s} {parts[pid]["summary"]}')
        print()

    print('ラボ管理下のツール')
    for s in skills:
        n = len({pid for pid, u in cat_usage.items() if s['name'] in u}
                | set(s['parts_referenced']))
        print(f'  {s["name"]:22s} 使用部品 {n}点')

    print()
    if intake['untracked']:
        print('⚠ 未取り込みのツール（ラボの外で作られ、まだ部品化されていない）')
        for name in intake['untracked']:
            print(f'  {name} → 取り込みモードで分解し、部品をライブラリに還元すること')
        print()
    if intake['not_installed']:
        print('⚠ 正本はあるが未インストール')
        for name in intake['not_installed']:
            print(f'  {name} → cp -r tool-factory/skills/{name} ~/.claude/skills/')
        print()

    if drift:
        print('⚠ 使用実績のズレ（部品ファイルが正。カタログ表を合わせること）')
        for pid, f, c in drift:
            print(f'  {pid}: 部品ファイル={f} / カタログ={c}')
        print()

    if issues['missing_in_catalog'] or issues['missing_file']:
        print('⚠ カタログとの不一致')
        for pid in issues['missing_in_catalog']:
            print(f'  カタログ未登録: {pid} → PARTS_CATALOG.md に追記が必要')
        for pid in issues['missing_file']:
            print(f'  ファイル不在  : {pid} → parts/ に実体がない')
    elif not intake['untracked'] and not intake['not_installed'] and not drift:
        print('✓ カタログ・部品・ツールはすべて一致している')
    else:
        print('✓ カタログと部品ファイルは一致している')


if __name__ == '__main__':
    main()
