"""
Unified parser for horse past results from db.netkeiba.com read_page output.

Handles 3 formats automatically:
  1. AT (Accessibility Tree): lines with `link "..."`, `generic "..."`
  2. Plain text: one value per line, dates as standalone YYYY/MM/DD
  3. CSV: comma-separated values, one race per line

Usage:
  # Single file
  python parse_horse_results.py past_results/2022107209.txt

  # Directory (all .txt files) → merged JSON
  python parse_horse_results.py past_results/ --output all_past_results.json
"""
import json, re, sys, os


# ── Format detection ──────────────────────────────────────────────

def detect_format(text):
    """Return 'at', 'plain', or 'csv'."""
    first_500 = text[:500]
    if 'link "' in first_500 or 'generic "' in first_500:
        return 'at'
    # CSV: lines with 5+ commas and a date at the start
    for line in text.strip().split('\n')[:10]:
        if re.match(r'\d{4}/\d{2}/\d{2}', line) and line.count(',') >= 5:
            return 'csv'
    return 'plain'


# ── AT format parser ─────────────────────────────────────────────

def parse_at_results(text, max_races=20):
    results = []
    lines = text.strip().split('\n')

    i = 0
    while i < len(lines):
        if re.search(r'link "\d{4}/\d{2}/\d{2}"', lines[i]):
            break
        i += 1

    while i < len(lines) and len(results) < max_races:
        line = lines[i].strip()
        date_match = re.search(r'link "(\d{4}/\d{2}/\d{2})"', line)
        if not date_match:
            i += 1
            continue

        date_str = date_match.group(1)

        race_lines = [line]
        j = i + 1
        while j < len(lines):
            if re.search(r'link "\d{4}/\d{2}/\d{2}"', lines[j]):
                break
            race_lines.append(lines[j].strip())
            j += 1

        block = '\n'.join(race_lines)

        venue_match = re.search(r'link "([^"]+)" \[ref_\d+\] href="https://db\.netkeiba\.com/race/sum/', block)
        venue = venue_match.group(1) if venue_match else ""

        race_match = re.search(r'link "([^"]+)" \[ref_\d+\] href="https://db\.netkeiba\.com/race/\d+/"', block)
        race_name = race_match.group(1) if race_match else ""

        jockey_match = re.search(r'link "([^"]+)" \[ref_\d+\] href="https://db\.netkeiba\.com/jockey/', block)
        jockey = jockey_match.group(1) if jockey_match else ""

        dist_match = re.search(r'generic "(ダ|芝|障)(\d+)"', block)
        track = dist_match.group(1) if dist_match else "ダ"
        distance = int(dist_match.group(2)) if dist_match else 0

        time_match = re.search(r'generic "(\d+:\d+\.\d+)"', block)
        time_str = time_match.group(1) if time_match else ""

        all_generics = re.findall(r'generic "([^"]+)"', block)

        odds = None
        for g in all_generics:
            try:
                v = float(g)
                if 0.1 <= v <= 999.9 and '(' not in g and '-' not in g and ':' not in g:
                    odds = v
                    break
            except:
                continue

        margin = ""
        found_time = False
        for g in all_generics:
            if ':' in g and re.match(r'\d+:\d+\.\d+', g):
                found_time = True
                continue
            if found_time:
                if re.match(r'^-?\d+\.\d+$', g):
                    margin = g
                    break

        finish = 0
        winner_match = re.search(r'link "\(([^)]+)\)" \[ref_\d+\] href="https://db\.netkeiba\.com/horse/', block)
        if winner_match:
            finish = 1
        elif margin:
            try:
                m = float(margin)
                if m <= 0:
                    finish = 1
            except:
                pass

        pass_match = re.search(r'generic "(\d+-\d+(?:-\d+)*)"', block)
        passing = pass_match.group(1) if pass_match else ""

        pace_match = re.search(r'generic "(\d+\.\d+-\d+\.\d+)"', block)
        pace = pace_match.group(1) if pace_match else ""

        last_3f = ""
        found_pace = False
        for g in all_generics:
            if re.match(r'\d+\.\d+-\d+\.\d+', g):
                found_pace = True
                continue
            if found_pace:
                if re.match(r'^\d{2}\.\d$', g):
                    last_3f = g
                    break

        weight = None
        weight_diff = None
        weight_match = re.search(r'generic "(\d{3,4})\(([+-]?\d+)\)"', block)
        if weight_match:
            weight = int(weight_match.group(1))
            weight_diff = int(weight_match.group(2))

        results.append({
            "date": date_str.replace('/', '-'),
            "venue": venue, "race_name": race_name,
            "distance": distance, "track": track,
            "finish": finish, "time": time_str, "margin": margin,
            "last_3f": last_3f, "odds": odds, "jockey": jockey,
            "passing": passing, "weight": weight, "weight_diff": weight_diff
        })
        i = j

    return results[:max_races]


# ── Plain text parser ────────────────────────────────────────────

def parse_plain_results(text, max_races=20):
    results = []
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]

    i = 0
    while i < len(lines) and len(results) < max_races:
        if not re.match(r'\d{4}/\d{2}/\d{2}$', lines[i]):
            i += 1
            continue

        date_str = lines[i]
        j = i + 1
        race_lines = []
        while j < len(lines):
            if re.match(r'\d{4}/\d{2}/\d{2}$', lines[j]):
                break
            race_lines.append(lines[j])
            j += 1

        if len(race_lines) < 5:
            i = j
            continue

        venue = race_lines[0] if len(race_lines) > 0 else ""
        race_name = race_lines[1] if len(race_lines) > 1 else ""

        odds = None; jockey = ""; track = "ダ"; distance = 0
        time_str = ""; margin = ""; passing = ""; pace = ""
        last_3f = ""; weight = None; weight_diff = None; finish = 0

        idx = 2
        while idx < len(race_lines) and "映像" in race_lines[idx]:
            idx += 1

        for k in range(idx, len(race_lines)):
            val = race_lines[k]
            if val == "**":
                continue
            dm = re.match(r'^(ダ|芝|障)(\d+)$', val)
            if dm:
                track = dm.group(1); distance = int(dm.group(2)); continue
            if re.match(r'^\d+:\d+\.\d+$', val):
                time_str = val; continue
            wm = re.match(r'^(\d{3,4})\(([+-]?\d+)\)$', val)
            if wm:
                weight = int(wm.group(1)); weight_diff = int(wm.group(2)); continue
            if re.match(r'^\d+-\d+(-\d+)*$', val):
                passing = val; continue
            if re.match(r'^\d+\.\d+-\d+\.\d+$', val):
                pace = val; continue
            if re.match(r'^-?\d+\.\d+$', val) and not pace and time_str:
                margin = val; continue
            if re.match(r'^\d{2}\.\d$', val) and pace:
                last_3f = val; continue
            if re.match(r'^\d+\.\d+$', val) and odds is None and not time_str:
                odds = float(val); continue
            if re.match(r'^-?\d+$', val):
                continue
            if re.match(r'^\(.+\)$', val):
                finish = 1; continue
            if not jockey and not re.match(r'^[\d.+-]+$', val) and "映像" not in val and distance == 0:
                jockey = val; continue

        if margin:
            try:
                if float(margin) <= 0:
                    finish = 1
            except:
                pass

        results.append({
            "date": date_str.replace('/', '-'),
            "venue": venue, "race_name": race_name,
            "distance": distance, "track": track,
            "finish": finish, "time": time_str, "margin": margin,
            "last_3f": last_3f, "odds": odds, "jockey": jockey,
            "passing": passing, "weight": weight, "weight_diff": weight_diff
        })
        i = j

    return results[:max_races]


# ── CSV parser ───────────────────────────────────────────────────

def parse_csv_results(text, max_races=20):
    results = []
    for line in text.strip().split('\n'):
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 6 or not re.match(r'\d{4}/\d{2}/\d{2}', parts[0]):
            continue

        date_str = parts[0]
        venue = parts[1] if len(parts) > 1 else ""
        race_name = parts[2] if len(parts) > 2 else ""

        odds = None
        try:
            if parts[3] != '**':
                odds = float(parts[3])
        except:
            pass

        jockey = parts[4] if len(parts) > 4 else ""

        track = "ダ"; distance = 0
        if len(parts) > 5:
            dm = re.match(r'(ダ|芝|障)(\d+)', parts[5])
            if dm:
                track = dm.group(1); distance = int(dm.group(2))

        time_str = parts[6] if len(parts) > 6 and parts[6] != '**' else ""
        margin = parts[7] if len(parts) > 7 and parts[7] != '**' else ""

        passing = ""
        if len(parts) > 8 and re.match(r'\d+-\d+', parts[8]):
            passing = parts[8]

        last_3f = ""
        for p in parts[9:]:
            if re.match(r'^\d{2}\.\d$', p):
                last_3f = p; break

        weight = None; weight_diff = None
        for p in parts:
            wm = re.match(r'(\d{3,4})\(([+-]?\d+)\)', p)
            if wm:
                weight = int(wm.group(1)); weight_diff = int(wm.group(2)); break

        finish = 0
        for p in parts:
            if re.match(r'^\(.+\)$', p):
                finish = 1; break
        if margin:
            try:
                if float(margin) <= 0:
                    finish = 1
            except:
                pass

        results.append({
            "date": date_str.replace('/', '-'),
            "venue": venue, "race_name": race_name,
            "distance": distance, "track": track,
            "finish": finish, "time": time_str, "margin": margin,
            "last_3f": last_3f, "odds": odds, "jockey": jockey,
            "passing": passing, "weight": weight, "weight_diff": weight_diff
        })
        if len(results) >= max_races:
            break

    return results


# ── Unified entry point ──────────────────────────────────────────

def parse_horse_file(filepath, max_races=20):
    """Parse a single horse's past results file. Auto-detects format."""
    with open(filepath) as f:
        text = f.read()

    if not text.strip():
        return []

    fmt = detect_format(text)
    if fmt == 'at':
        return parse_at_results(text, max_races)
    elif fmt == 'csv':
        return parse_csv_results(text, max_races)
    else:
        return parse_plain_results(text, max_races)


def parse_directory(dirpath, max_races=20):
    """Parse all .txt files in a directory. Returns dict: horse_id → results."""
    all_results = {}
    for fname in sorted(os.listdir(dirpath)):
        if not fname.endswith('.txt'):
            continue
        horse_id = fname.replace('.txt', '')
        filepath = os.path.join(dirpath, fname)
        results = parse_horse_file(filepath, max_races)
        all_results[horse_id] = results
    return all_results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Parse horse past results')
    parser.add_argument('input', help='Single .txt file or directory of .txt files')
    parser.add_argument('--output', '-o', help='Output JSON file (default: stdout)')
    parser.add_argument('--max-races', type=int, default=20, help='Max races per horse')
    args = parser.parse_args()

    if os.path.isdir(args.input):
        data = parse_directory(args.input, args.max_races)
        output = {
            "horse_count": len(data),
            "total_records": sum(len(v) for v in data.values()),
            "horses": {hid: {"horse_id": hid, "results": res} for hid, res in data.items()}
        }
    else:
        horse_id = os.path.basename(args.input).replace('.txt', '')
        results = parse_horse_file(args.input, args.max_races)
        output = {"horse_id": horse_id, "results": results}

    json_str = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(json_str)
        print(f"Saved: {args.output} ({len(json_str)} bytes)")
    else:
        print(json_str)
