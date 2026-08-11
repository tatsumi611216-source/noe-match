#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docs/childcare-wbs-pregnancy-to-1year.md から、チェックボックス付きのHTML版WBSを生成する。

usage: python3 scripts/build_childcare_wbs.py
out:   docs/childcare-wbs.html
"""

import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "childcare-wbs-pregnancy-to-1year.md")
OUT = os.path.join(ROOT, "docs", "childcare-wbs.html")

DEADLINE_KEYS = ("目安時期", "期限", "目安", "いつ", "時期")


# --------------------------------------------------------------------------
# markdown parsing
# --------------------------------------------------------------------------

def split_row(line):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def is_sep(line):
    return bool(re.match(r"^\s*\|[\s:|-]+\|\s*$", line))


def parse(md):
    lines = md.split("\n")
    nodes = []
    i = 0
    para = []

    def flush_para():
        if para:
            nodes.append({"t": "p", "text": " ".join(para)})
            para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_para()
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            flush_para()
            nodes.append({"t": "h", "level": len(m.group(1)), "text": m.group(2)})
            i += 1
            continue

        if stripped in ("---", "***", "___"):
            flush_para()
            nodes.append({"t": "hr"})
            i += 1
            continue

        if stripped.startswith(">"):
            flush_para()
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            nodes.append({"t": "quote", "text": " ".join(x for x in buf if x)})
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and is_sep(lines[i + 1]):
            flush_para()
            head = split_row(lines[i])
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            nodes.append({"t": "table", "head": head, "rows": rows})
            continue

        if re.match(r"^[-*]\s+", stripped):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            nodes.append({"t": "ul", "items": items})
            continue

        if re.match(r"^\d+\.\s+", stripped):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            nodes.append({"t": "ol", "items": items})
            continue

        para.append(stripped)
        i += 1

    flush_para()
    return nodes


def inline(text):
    """最低限のインライン記法だけを HTML に変換する。"""
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        out,
    )
    out = out.replace("★", '<span class="star">★</span>')
    return out


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

def phase_kind(title):
    if title.startswith("付録"):
        return "appendix"
    m = re.search(r"Phase\s*(\d+)", title)
    if not m:
        return "meta"
    n = int(m.group(1))
    if n <= 3:
        return "pre"
    if n == 4:
        return "birth"
    return "post"


def slug(title, n):
    return "sec-%d" % n


def render_task_table(node, counter):
    head = node["head"]
    idx = {name: k for k, name in enumerate(head)}
    col_id = idx.get("ID")
    col_cat = idx.get("分類")
    col_task = idx.get("タスク")
    col_due = next((idx[k] for k in DEADLINE_KEYS if k in idx), None)
    col_who = idx.get("担当")
    col_memo = idx.get("メモ")

    parts = ['<div class="tasks">']
    for row in node["rows"]:
        def cell(k):
            return row[k].strip() if k is not None and k < len(row) else ""

        tid = cell(col_id)
        task = cell(col_task)
        if not tid and not task:
            continue
        due = cell(col_due)
        who = cell(col_who)
        memo = cell(col_memo)
        cat = cell(col_cat)
        crit = "**" in task or "★" in task
        counter["total"] += 1

        cls = "task" + (" task--crit" if crit else "")
        parts.append('<div class="%s" data-id="%s">' % (cls, html.escape(tid)))
        parts.append(
            '<input type="checkbox" class="tick" id="t-%s" data-key="%s" aria-label="%s 完了">'
            % (html.escape(tid), html.escape(tid), html.escape(tid))
        )
        parts.append('<label class="task__main" for="t-%s">' % html.escape(tid))
        parts.append('<span class="task__id">%s</span>' % html.escape(tid))
        parts.append('<span class="task__title">%s</span>' % inline(task))
        if memo:
            parts.append('<span class="task__memo">%s</span>' % inline(memo))
        parts.append("</label>")
        parts.append('<div class="task__meta">')
        if due:
            parts.append('<span class="chip chip--due">%s</span>' % inline(due))
        if who:
            parts.append('<span class="chip chip--who">%s</span>' % html.escape(who))
        if cat:
            parts.append('<span class="chip chip--cat">%s</span>' % html.escape(cat))
        parts.append("</div>")
        parts.append("</div>")
    parts.append("</div>")
    return "\n".join(parts)


def render_plain_table(node):
    parts = ['<div class="tablewrap"><table>', "<thead><tr>"]
    for h in node["head"]:
        parts.append("<th>%s</th>" % inline(h))
    parts.append("</tr></thead><tbody>")
    for row in node["rows"]:
        parts.append("<tr>")
        for k, h in enumerate(node["head"]):
            parts.append("<td>%s</td>" % (inline(row[k]) if k < len(row) else ""))
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    return "\n".join(parts)


def render(nodes):
    counter = {"total": 0}
    body = []
    nav = []
    open_section = False
    sec_n = 0
    check_n = 0

    for node in nodes:
        t = node["t"]

        if t == "h" and node["level"] == 1:
            if open_section:
                body.append("</section>")
            sec_n += 1
            title = node["text"]
            kind = phase_kind(title)
            sid = slug(title, sec_n)
            if sec_n == 1:
                nav_label = "はじめに"
            else:
                nav_label = title.replace("Phase ", "P").replace("：", " ")
            nav.append((sid, nav_label, kind))
            lead = " phase--lead" if sec_n == 1 else ""
            body.append('<section class="phase phase--%s%s" id="%s">' % (kind, lead, sid))
            if sec_n > 1:
                # 先頭セクションの見出しはマストヘッドと重複するので出さない
                body.append(
                    '<h2 class="phase__title"><span class="phase__dot" aria-hidden="true"></span>%s</h2>'
                    % inline(title)
                )
            open_section = True
            continue

        if t == "h":
            lvl = min(node["level"] + 1, 5)
            body.append("<h%d>%s</h%d>" % (lvl, inline(node["text"]), lvl))
            continue

        if t == "table":
            if "ID" in node["head"] and "タスク" in node["head"]:
                body.append(render_task_table(node, counter))
            else:
                body.append(render_plain_table(node))
            continue

        if t == "quote":
            body.append('<blockquote>%s</blockquote>' % inline(node["text"]))
            continue

        if t == "ul":
            checkish = all(x.startswith("☐") for x in node["items"])
            if checkish:
                body.append('<ul class="checklist">')
                for item in node["items"]:
                    check_n += 1
                    key = "chk-%d" % check_n
                    counter["total"] += 1
                    body.append(
                        '<li><input type="checkbox" class="tick" id="%s" data-key="%s">'
                        '<label for="%s">%s</label></li>'
                        % (key, key, key, inline(item.lstrip("☐ ").strip()))
                    )
                body.append("</ul>")
            else:
                body.append("<ul>")
                for item in node["items"]:
                    body.append("<li>%s</li>" % inline(item))
                body.append("</ul>")
            continue

        if t == "ol":
            body.append("<ol>")
            for item in node["items"]:
                body.append("<li>%s</li>" % inline(item))
            body.append("</ol>")
            continue

        if t == "hr":
            continue

        if t == "p":
            # マストヘッドと重複する冒頭2段落は出さない
            if sec_n == 1 and (
                node["text"].startswith("**最終更新")
                or node["text"].startswith("妊娠判明から子どもが1歳になるまでに")
            ):
                continue
            body.append("<p>%s</p>" % inline(node["text"]))
            continue

    if open_section:
        body.append("</section>")

    return "\n".join(body), nav, counter["total"]


CSS = """
:root {
  color-scheme: light dark;
  --paper:      #F4F6F1;
  --surface:    #FFFFFF;
  --surface-2:  #EDF0E9;
  --ink:        #15201A;
  --ink-2:      #4B564E;
  --ink-3:      #7B877E;
  --line:       #DCE1D6;
  --line-soft:  #E8EBE3;
  --accent:     #2F6B4F;
  --accent-2:   #E1EBE2;
  --pre:        #966C2E;
  --pre-2:      #F0E8D8;
  --crit:       #A93C27;
  --crit-2:     #F6E3DD;
  --shadow:     0 1px 2px rgba(21,32,26,.05), 0 8px 24px -18px rgba(21,32,26,.35);

  --font-display: "Hiragino Mincho ProN", "Yu Mincho", YuMincho, "Noto Serif JP",
                  "Source Han Serif JP", "MS PMincho", serif;
  --font-body:    "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", YuGothic,
                  "Noto Sans JP", Meiryo, system-ui, sans-serif;
  --font-mono:    ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper:     #0F1310;
    --surface:   #171C18;
    --surface-2: #1D2320;
    --ink:       #E6EAE3;
    --ink-2:     #A5AFA5;
    --ink-3:     #79847B;
    --line:      #2A322C;
    --line-soft: #222926;
    --accent:    #74C296;
    --accent-2:  #1B2A22;
    --pre:       #D2A75F;
    --pre-2:     #2A2418;
    --crit:      #E88E75;
    --crit-2:    #33201B;
    --shadow:    0 1px 2px rgba(0,0,0,.4), 0 10px 30px -20px rgba(0,0,0,.9);
  }
}

:root[data-theme="dark"] {
  --paper:     #0F1310;
  --surface:   #171C18;
  --surface-2: #1D2320;
  --ink:       #E6EAE3;
  --ink-2:     #A5AFA5;
  --ink-3:     #79847B;
  --line:      #2A322C;
  --line-soft: #222926;
  --accent:    #74C296;
  --accent-2:  #1B2A22;
  --pre:       #D2A75F;
  --pre-2:     #2A2418;
  --crit:      #E88E75;
  --crit-2:    #33201B;
  --shadow:    0 1px 2px rgba(0,0,0,.4), 0 10px 30px -20px rgba(0,0,0,.9);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: var(--font-body);
  font-size: 15px;
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
  font-feature-settings: "palt" 1;
}

a { color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 2px; }
a:focus-visible, input:focus-visible, button:focus-visible {
  outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 3px;
}
code {
  font-family: var(--font-mono); font-size: .88em;
  background: var(--surface-2); padding: .1em .35em; border-radius: 3px;
}
strong { font-weight: 700; color: var(--ink); }

/* ---------- masthead ---------- */

.masthead {
  border-bottom: 1px solid var(--line);
  background: var(--surface);
  padding: 40px 0 28px;
}
.wrap { width: min(1080px, calc(100% - 40px)); margin-inline: auto; }

.eyebrow {
  font-family: var(--font-mono);
  font-size: 11px; letter-spacing: .18em; text-transform: uppercase;
  color: var(--ink-3); margin: 0 0 14px;
}
.masthead h1 {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: clamp(28px, 4.6vw, 44px);
  line-height: 1.25;
  letter-spacing: .01em;
  margin: 0 0 14px;
  text-wrap: balance;
}
.masthead h1 .rule {
  display: inline-block; width: 1px; height: .85em; margin: 0 .5em -.08em;
  background: var(--line); vertical-align: baseline;
}
.lede {
  max-width: 62ch; color: var(--ink-2); margin: 0 0 26px; font-size: 14.5px;
}

/* 妊娠期 → 出産 → 産後 のスケール */
.scale { display: flex; align-items: stretch; gap: 0; margin: 0 0 6px; border-radius: 2px; overflow: hidden; }
.scale span {
  font-family: var(--font-mono); font-size: 10.5px; letter-spacing: .1em;
  padding: 6px 10px; white-space: nowrap; color: var(--ink);
}
.scale .s-pre   { background: var(--pre-2);   flex: 10; }
.scale .s-birth { background: var(--crit);    flex: 0 0 auto; color: #fff; font-weight: 700; }
.scale .s-post  { background: var(--accent-2); flex: 12; text-align: right; }
.scale-note { font-family: var(--font-mono); font-size: 10.5px; color: var(--ink-3); margin: 0; }

/* ---------- toolbar ---------- */

.toolbar {
  position: sticky; top: 0; z-index: 30;
  background: color-mix(in srgb, var(--paper) 92%, transparent);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
}
.toolbar__inner {
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  padding: 10px 0;
}
.progress { display: flex; align-items: center; gap: 10px; min-width: 210px; }
.progress__bar {
  flex: 1; height: 5px; background: var(--surface-2); border-radius: 99px; overflow: hidden;
}
.progress__fill { height: 100%; width: 0%; background: var(--accent); transition: width .25s ease; }
.progress__num {
  font-family: var(--font-mono); font-size: 12px; color: var(--ink-2);
  font-variant-numeric: tabular-nums; white-space: nowrap;
}
.tools { display: flex; gap: 8px; margin-left: auto; flex-wrap: wrap; }
.btn {
  font: inherit; font-size: 12px; font-family: var(--font-body);
  border: 1px solid var(--line); background: var(--surface); color: var(--ink-2);
  padding: 5px 12px; border-radius: 99px; cursor: pointer;
}
.btn:hover { border-color: var(--accent); color: var(--accent); }
.btn[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: var(--paper); }

/* ---------- nav ---------- */

.phasenav { padding: 18px 0 4px; }
.phasenav ol {
  list-style: none; margin: 0; padding: 0;
  display: flex; gap: 6px; overflow-x: auto; padding-bottom: 8px;
}
.phasenav a {
  display: block; white-space: nowrap; text-decoration: none;
  font-size: 12px; padding: 5px 11px; border-radius: 99px;
  border: 1px solid var(--line); color: var(--ink-2); background: var(--surface);
}
.phasenav a:hover { border-color: var(--accent); color: var(--accent); }
.phasenav .n-pre a      { border-left: 3px solid var(--pre); }
.phasenav .n-birth a    { border-left: 3px solid var(--crit); }
.phasenav .n-post a     { border-left: 3px solid var(--accent); }
.phasenav .n-appendix a { border-left: 3px solid var(--ink-3); }

/* ---------- phases ---------- */

main { padding: 8px 0 90px; }

.phase {
  position: relative;
  padding: 30px 0 30px 28px;
  border-left: 1px solid var(--line);
  margin-left: 6px;
  scroll-margin-top: 68px;
}
.phase--lead { padding-top: 22px; }
.phase--pre      { --tone: var(--pre);    --tone-2: var(--pre-2); }
.phase--birth    { --tone: var(--crit);   --tone-2: var(--crit-2); }
.phase--post     { --tone: var(--accent); --tone-2: var(--accent-2); }
.phase--appendix { --tone: var(--ink-3);  --tone-2: var(--surface-2); }
.phase--meta     { --tone: var(--ink-3);  --tone-2: var(--surface-2); }

.phase__title {
  font-family: var(--font-display);
  font-weight: 600; font-size: clamp(20px, 2.8vw, 27px); line-height: 1.4;
  margin: 0 0 20px; letter-spacing: .01em; text-wrap: balance;
}
.phase__dot {
  position: absolute; left: -6.5px; top: 40px;
  width: 11px; height: 11px; border-radius: 50%;
  background: var(--tone); box-shadow: 0 0 0 4px var(--paper);
}
.phase--birth { background: linear-gradient(90deg, var(--crit-2), transparent 40%); }

.phase h3 {
  font-family: var(--font-display); font-weight: 600;
  font-size: 18px; margin: 34px 0 12px; letter-spacing: .01em;
  padding-bottom: 6px; border-bottom: 1px solid var(--line-soft);
}
.phase h4 {
  font-size: 13px; font-weight: 700; letter-spacing: .06em; color: var(--tone);
  margin: 26px 0 10px; text-transform: none;
}
.phase h5 { font-size: 13px; margin: 20px 0 8px; }
.phase p  { max-width: 68ch; color: var(--ink-2); }
.phase > p:first-of-type { margin-top: 0; }

blockquote {
  margin: 16px 0; padding: 12px 16px;
  border-left: 3px solid var(--tone);
  background: var(--tone-2);
  color: var(--ink); font-size: 13.5px; border-radius: 0 4px 4px 0;
}
blockquote strong { color: var(--ink); }

/* ---------- task rows ---------- */

.tasks {
  display: flex; flex-direction: column; gap: 1px;
  background: var(--line-soft); border: 1px solid var(--line);
  border-radius: 6px; overflow: hidden; margin: 14px 0 22px;
  box-shadow: var(--shadow);
}
.task {
  display: grid;
  grid-template-columns: 30px minmax(0, 1fr) minmax(0, 250px);
  align-items: start; gap: 4px 10px;
  background: var(--surface); padding: 11px 14px 11px 12px;
  position: relative;
}
.task--crit { box-shadow: inset 3px 0 0 var(--crit); }
.task.is-done { opacity: .45; }
.task.is-done .task__title { text-decoration: line-through; }

.tick {
  appearance: none; -webkit-appearance: none;
  width: 17px; height: 17px; margin: 4px 0 0;
  border: 1.5px solid var(--ink-3); border-radius: 4px;
  background: transparent; cursor: pointer; flex: none;
}
.tick:checked { background: var(--accent); border-color: var(--accent); }
.tick:checked::after {
  content: ""; display: block; width: 4px; height: 8px;
  border: solid #fff; border-width: 0 2px 2px 0;
  transform: rotate(42deg); margin: 1.5px 0 0 5px;
}

.task__main { display: block; cursor: pointer; min-width: 0; }
.task__id {
  font-family: var(--font-mono); font-size: 10px; letter-spacing: .04em;
  color: var(--ink-3); display: block; margin-bottom: 1px;
}
.task__title { display: block; font-size: 14px; line-height: 1.6; }
.task__title strong { color: var(--crit); }
.task__memo {
  display: block; font-size: 12.5px; color: var(--ink-2);
  line-height: 1.65; margin-top: 3px;
}
.task__memo strong { color: var(--ink); }
.task__meta { display: flex; flex-wrap: wrap; gap: 5px; justify-content: flex-end; padding-top: 12px; }

.chip {
  font-family: var(--font-mono); font-size: 10.5px; line-height: 1.5;
  padding: 2px 7px; border-radius: 3px; white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.chip--due { background: var(--tone-2); color: var(--ink); border: 1px solid transparent; }
.task--crit .chip--due { background: var(--crit-2); color: var(--crit); font-weight: 700; }
.chip--who { background: var(--surface-2); color: var(--ink-2); }
.chip--cat { background: transparent; color: var(--ink-3); border: 1px solid var(--line); }
.chip strong { font-weight: 700; }
.star { color: var(--crit); }

/* ---------- plain tables ---------- */

.tablewrap { overflow-x: auto; margin: 14px 0 24px; border: 1px solid var(--line); border-radius: 6px; }
table { border-collapse: collapse; width: 100%; background: var(--surface); font-size: 13px; }
th, td { text-align: left; padding: 9px 13px; border-bottom: 1px solid var(--line-soft); vertical-align: top; }
th {
  background: var(--surface-2); font-size: 11px; letter-spacing: .06em;
  color: var(--ink-2); font-weight: 700; white-space: nowrap;
}
tbody tr:last-child td { border-bottom: 0; }
td { font-variant-numeric: tabular-nums; }

/* ---------- lists ---------- */

.phase ul, .phase ol { max-width: 68ch; padding-left: 1.3em; color: var(--ink-2); }
.phase li { margin-bottom: 5px; }
.phase li strong { color: var(--ink); }

.checklist { list-style: none; padding: 0; max-width: 68ch; }
.checklist li { display: flex; gap: 10px; align-items: flex-start; padding: 5px 0; border-bottom: 1px solid var(--line-soft); }
.checklist label { cursor: pointer; font-size: 13.5px; }
.checklist li.is-done label { opacity: .45; text-decoration: line-through; }

/* ---------- filter state ---------- */

body.hide-done .task.is-done,
body.hide-done .checklist li.is-done { display: none; }

footer {
  border-top: 1px solid var(--line); padding: 26px 0 60px;
  color: var(--ink-3); font-size: 12px;
}

@media (max-width: 720px) {
  .task { grid-template-columns: 26px minmax(0, 1fr); }
  .task__meta { grid-column: 2; justify-content: flex-start; padding-top: 4px; }
  .phase { padding-left: 18px; }
  .wrap { width: calc(100% - 28px); }
}

@media print {
  .toolbar, .phasenav { display: none; }
  body { background: #fff; }
  .task { break-inside: avoid; }
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
"""

JS = """
(function () {
  var KEY = 'childcare-wbs-v1';
  var state = {};
  try { state = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { state = {}; }

  var ticks = Array.prototype.slice.call(document.querySelectorAll('.tick'));
  var fill = document.getElementById('progress-fill');
  var num  = document.getElementById('progress-num');

  function rowOf(el) { return el.closest('.task') || el.closest('li'); }

  function paint(el) {
    var row = rowOf(el);
    if (row) row.classList.toggle('is-done', el.checked);
  }

  function update() {
    var done = ticks.filter(function (t) { return t.checked; }).length;
    var pct = ticks.length ? Math.round(done / ticks.length * 100) : 0;
    fill.style.width = pct + '%';
    num.textContent = done + ' / ' + ticks.length + '  (' + pct + '%)';
  }

  ticks.forEach(function (t) {
    var k = t.dataset.key;
    if (state[k]) t.checked = true;
    paint(t);
    t.addEventListener('change', function () {
      state[k] = t.checked;
      if (!t.checked) delete state[k];
      try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
      paint(t);
      update();
    });
  });
  update();

  var hide = document.getElementById('btn-hide');
  hide.addEventListener('click', function () {
    var on = document.body.classList.toggle('hide-done');
    hide.setAttribute('aria-pressed', on ? 'true' : 'false');
    hide.textContent = on ? '完了も表示' : '未完了だけ表示';
  });

  document.getElementById('btn-reset').addEventListener('click', function () {
    if (!confirm('チェックを全部消します。よろしいですか？')) return;
    ticks.forEach(function (t) { t.checked = false; paint(t); });
    state = {};
    try { localStorage.removeItem(KEY); } catch (e) {}
    update();
  });
})();
"""


def build():
    with open(SRC, encoding="utf-8") as f:
        md = f.read()

    nodes = parse(md)
    # 先頭のタイトル(h1)と使い方見出しはそのまま流し込む
    body, nav, total = render(nodes)

    nav_html = "\n".join(
        '<li class="n-%s"><a href="#%s">%s</a></li>' % (kind, sid, html.escape(re.sub(r"^#\s*", "", title)))
        for sid, title, kind in nav
    )

    doc = """<title>育児WBS｜妊娠判明から1歳まで</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>%s</style>

<header class="masthead">
  <div class="wrap">
    <p class="eyebrow">Work Breakdown Structure &nbsp;/&nbsp; 2026-08 版</p>
    <h1>妊娠判明から1歳まで<span class="rule"></span>やることリスト</h1>
    <p class="lede">
      約21ヶ月分のタスクを月単位に分解した実行用WBS。行政手続き・医療・お金・モノの準備・育児実務・
      イベント・保活を横断し、法定期限のあるものは<strong>朱色</strong>で示している。
      チェックはこの端末のブラウザに保存される。
    </p>
    <div class="scale" aria-hidden="true">
      <span class="s-pre">妊娠 0w ─────────── 39w</span>
      <span class="s-birth">出産</span>
      <span class="s-post">生後 0ヶ月 ─────────── 12ヶ月</span>
    </div>
    <p class="scale-note">全 %d タスク</p>
  </div>
</header>

<div class="toolbar">
  <div class="wrap toolbar__inner">
    <div class="progress">
      <div class="progress__bar"><div class="progress__fill" id="progress-fill"></div></div>
      <span class="progress__num" id="progress-num">0 / %d</span>
    </div>
    <div class="tools">
      <button class="btn" id="btn-hide" type="button" aria-pressed="false">未完了だけ表示</button>
      <button class="btn" id="btn-reset" type="button">チェックを全消去</button>
    </div>
  </div>
</div>

<nav class="phasenav" aria-label="フェーズ">
  <div class="wrap"><ol>%s</ol></div>
</nav>

<main class="wrap">
%s
</main>

<footer>
  <div class="wrap">
    本ページは2026年8月時点の一般的な情報に基づく計画テンプレートであり、医療上の助言ではありません。
    健康・治療・接種の判断は主治医に、制度の適用可否は自治体・健保・勤務先・ハローワークに確認してください。
  </div>
</footer>

<script>%s</script>
""" % (CSS, total, total, nav_html, body, JS)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print("wrote %s (%d tasks, %d KB)" % (OUT, total, len(doc) // 1024))


if __name__ == "__main__":
    build()
