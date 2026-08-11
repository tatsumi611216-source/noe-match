#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wbs_data.py から、公開・共有できるHTML版（①②③）を生成する。

各タブに「スプレッドシート用にコピー」ボタンを付けてあるので、
Googleスプレッドシートの A1 に貼るだけで表になる。

usage: python3 scripts/build_life_wbs_html.py
out:   docs/life-wbs.html
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wbs_data import PHASE_AGE, PHASES, RISKS, TASKS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "life-wbs.html")

GANTT_MONTHS = 187


def build_data():
    phases = [{
        "id": p[0], "name": p[1], "age": PHASE_AGE.get(p[0], ""),
        "goal": p[2], "dur": p[3], "start": p[4],
        "ms": p[5], "decide": p[6], "lo": p[7], "hi": p[8], "risk": p[9],
    } for p in PHASES]

    tasks = []
    major, minor, cur = {}, 0, ""
    for (ph, cat, lv, task, dod, m, kind, who, eff, cost, dep,
         ronten, opts, axis) in TASKS:
        if lv == 2:
            major[ph] = major.get(ph, 0) + 1
            minor = 0
            cur = "%s-%02d" % (ph, major[ph])
            wid = cur
        else:
            minor += 1
            wid = "%s-%02d" % (cur, minor)
        tasks.append({
            "id": wid, "ph": ph, "cat": cat, "lv": lv, "task": task, "dod": dod,
            "m": m, "kind": kind, "who": who, "eff": eff, "cost": cost,
            "dep": dep, "ronten": ronten, "opts": opts, "axis": axis,
        })

    risks = [{
        "id": "R%03d" % i, "ph": r[0], "cat": r[1], "ev": r[2], "scene": r[3],
        "sign": r[4], "view": r[5], "p": r[6], "imp": r[7], "score": r[6] * r[7],
        "prev": r[8], "first": r[9], "fix": r[10], "owner": r[11],
    } for i, r in enumerate(RISKS, start=1)]

    return {"phases": phases, "tasks": tasks, "risks": risks,
            "gantt": GANTT_MONTHS}


CSS = """
:root{
  color-scheme: light dark;
  --paper:#F4F6F1; --surface:#FFFFFF; --surface2:#EDF0E9;
  --ink:#15201A; --ink2:#4B564E; --ink3:#7B877E;
  --line:#DCE1D6; --line2:#E8EBE3;
  --accent:#2F6B4F; --accent2:#E1EBE2;
  --pre:#966C2E; --pre2:#F0E8D8;
  --crit:#A93C27; --crit2:#F6E3DD; --barexam:#8FBBA1;
  --shadow:0 1px 2px rgba(21,32,26,.05),0 8px 24px -18px rgba(21,32,26,.35);
  --fd:"Hiragino Mincho ProN","Yu Mincho",YuMincho,"Noto Serif JP","MS PMincho",serif;
  --fb:"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic",YuGothic,"Noto Sans JP",Meiryo,system-ui,sans-serif;
  --fm:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#0F1310; --surface:#171C18; --surface2:#1D2320;
  --ink:#E6EAE3; --ink2:#A5AFA5; --ink3:#79847B;
  --line:#2A322C; --line2:#222926;
  --accent:#74C296; --accent2:#1B2A22;
  --pre:#D2A75F; --pre2:#2A2418;
  --crit:#E88E75; --crit2:#33201B; --barexam:#2E5140;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px -20px rgba(0,0,0,.9);
}}
:root[data-theme="dark"]{
  --paper:#0F1310; --surface:#171C18; --surface2:#1D2320;
  --ink:#E6EAE3; --ink2:#A5AFA5; --ink3:#79847B;
  --line:#2A322C; --line2:#222926;
  --accent:#74C296; --accent2:#1B2A22;
  --pre:#D2A75F; --pre2:#2A2418;
  --crit:#E88E75; --crit2:#33201B; --barexam:#2E5140;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px -20px rgba(0,0,0,.9);
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--fb);
  font-size:14px;line-height:1.7;-webkit-font-smoothing:antialiased;font-feature-settings:"palt" 1}
.wrap{width:min(1400px,calc(100% - 32px));margin-inline:auto}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
strong{font-weight:700}

header.mast{background:var(--surface);border-bottom:1px solid var(--line);padding:34px 0 24px}
.eyebrow{font-family:var(--fm);font-size:11px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--ink3);margin:0 0 12px}
h1{font-family:var(--fd);font-weight:600;font-size:clamp(24px,3.6vw,38px);line-height:1.3;
  margin:0 0 12px;text-wrap:balance}
.lede{max-width:70ch;color:var(--ink2);margin:0 0 20px;font-size:14px}
.scale{display:flex;border-radius:2px;overflow:hidden;margin:0 0 6px;max-width:900px}
.scale span{font-family:var(--fm);font-size:10px;letter-spacing:.08em;padding:6px 9px;white-space:nowrap;color:var(--ink)}
.s-pre{background:var(--pre2);flex:22} .s-b{background:var(--crit);color:#fff;font-weight:700;flex:0 0 auto}
.s-post{background:var(--accent2);flex:12;text-align:right}
.counts{font-family:var(--fm);font-size:10.5px;color:var(--ink3);margin:0}

nav.tabs{position:sticky;top:0;z-index:40;background:color-mix(in srgb,var(--paper) 93%,transparent);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.tabs__in{display:flex;gap:6px;align-items:center;flex-wrap:wrap;padding:9px 0}
.tab{font:inherit;font-size:13px;border:1px solid var(--line);background:var(--surface);
  color:var(--ink2);padding:6px 14px;border-radius:99px;cursor:pointer}
.tab[aria-selected="true"]{background:var(--accent);border-color:var(--accent);color:var(--paper);font-weight:700}
.spacer{margin-left:auto}
.btn{font:inherit;font-size:12px;border:1px solid var(--line);background:var(--surface);
  color:var(--ink2);padding:5px 12px;border-radius:99px;cursor:pointer}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--paper)}
.btn--go{border-color:var(--accent);color:var(--accent);font-weight:700}

.panel{display:none;padding:22px 0 80px}
.panel.is-on{display:block}
h2.sec{font-family:var(--fd);font-weight:600;font-size:20px;margin:0 0 4px}
.sub{color:var(--ink2);font-size:13px;margin:0 0 16px;max-width:78ch}

.filters{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:0 0 14px;
  padding:10px 12px;background:var(--surface);border:1px solid var(--line);border-radius:8px}
select,input[type=search],input[type=date]{font:inherit;font-size:12.5px;padding:5px 8px;
  border:1px solid var(--line);border-radius:6px;background:var(--surface);color:var(--ink)}
input[type=search]{min-width:200px;flex:1}
.pbar{display:flex;align-items:center;gap:9px;min-width:190px}
.pbar__t{flex:1;height:5px;background:var(--surface2);border-radius:99px;overflow:hidden}
.pbar__f{height:100%;width:0;background:var(--accent);transition:width .2s}
.pnum{font-family:var(--fm);font-size:11.5px;color:var(--ink2);font-variant-numeric:tabular-nums;white-space:nowrap}

/* ---- roadmap ---- */
#p-rm .wrap{width:min(2450px,calc(100% - 32px))}
.rmwrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--surface);box-shadow:var(--shadow)}
table.rm{border-collapse:collapse;font-size:12.5px;table-layout:fixed;width:2390px}
table.rm td:nth-child(3){text-align:center}
.yrlab{font-family:var(--fm);font-size:9px;text-align:center;background:var(--accent);
  color:#fff;padding:2px 0!important;white-space:nowrap;overflow:hidden;
  border-left:1px solid rgba(255,255,255,.4)}
.yrgap{background:var(--accent)}
table.rm th,table.rm td{border-bottom:1px solid var(--line2);padding:8px 10px;vertical-align:top;text-align:left}
table.rm thead th{background:var(--accent);color:#fff;font-size:11px;letter-spacing:.05em}
table.rm td{word-break:break-word}
table.rm td.num{font-variant-numeric:tabular-nums;text-align:center;white-space:nowrap;font-family:var(--fm);font-size:11.5px}
.gcell{padding:0!important;border-left:0;overflow:hidden}
.sticky1{position:sticky;left:0;z-index:5}
.sticky2{position:sticky;left:38px;z-index:5;box-shadow:1px 0 0 var(--line)}
table.rm tbody .sticky1,table.rm tbody .sticky2{background:var(--surface);z-index:4}
.lgd{display:inline-flex;align-items:center;gap:5px;font-family:var(--fm);font-size:10.5px;color:var(--ink2)}
.lgd i{display:inline-block;width:14px;height:10px;border-radius:2px}
.lgd .i-pre{background:var(--pre2)} .lgd .i-post{background:var(--accent2)}
.lgd .i-exam{background:var(--barexam)} .lgd .i-birth{width:2px;height:12px;background:var(--crit)}
.gcell.yr{border-left:1px solid var(--line)}
.gcell.birth{border-left:2px solid var(--crit)}
.gbar{display:block;height:16px}
.gbar.pre{background:var(--pre2)} .gbar.post{background:var(--accent2)}
.gbar.exam{background:var(--barexam)}
.ghead{writing-mode:vertical-rl;font-family:var(--fm);font-size:8px;color:#fff;padding:3px 0!important;text-align:center;letter-spacing:.02em}

/* ---- wbs rows ---- */
.rows{display:flex;flex-direction:column;gap:1px;background:var(--line2);
  border:1px solid var(--line);border-radius:8px;overflow:hidden;box-shadow:var(--shadow)}
.row{background:var(--surface);padding:9px 13px;display:grid;
  grid-template-columns:24px 1fr auto;gap:2px 10px;align-items:start}
.row--task{background:var(--accent2)}
.row--step{padding-left:34px}
.row.is-done{opacity:.42}
.row.is-done .rt{text-decoration:line-through}
.row.hidden{display:none}
.tick{appearance:none;-webkit-appearance:none;width:16px;height:16px;margin:4px 0 0;
  border:1.5px solid var(--ink3);border-radius:4px;background:transparent;cursor:pointer;flex:none}
.tick:checked{background:var(--accent);border-color:var(--accent)}
.tick:checked::after{content:"";display:block;width:4px;height:8px;border:solid #fff;
  border-width:0 2px 2px 0;transform:rotate(42deg);margin:1px 0 0 4.5px}
.rmain{min-width:0;cursor:pointer}
.rid{font-family:var(--fm);font-size:9.5px;color:var(--ink3);display:block}
.rt{font-size:13.5px;line-height:1.55}
.row--task .rt{font-weight:700}
.rdod{display:block;font-size:12px;color:var(--ink2);margin-top:2px}
.rdod::before{content:"完了の定義：";color:var(--ink3)}
.meta{display:flex;gap:4px;flex-wrap:wrap;justify-content:flex-end;padding-top:11px}
.chip{font-family:var(--fm);font-size:10px;padding:2px 6px;border-radius:3px;white-space:nowrap}
.c-when{background:var(--surface2);color:var(--ink2)}
.c-who{background:var(--surface2);color:var(--ink2)}
.c-eff{background:transparent;border:1px solid var(--line);color:var(--ink3)}
.c-cost{background:var(--pre2);color:var(--ink)}
.c-law{background:var(--crit);color:#fff;font-weight:700}
.detail{grid-column:2/-1;margin-top:7px;border-left:2px solid var(--accent);padding-left:11px;
  display:flex;flex-direction:column;gap:6px}
.dblk{font-size:12.5px;line-height:1.65}
.dlab{font-family:var(--fm);font-size:9.5px;letter-spacing:.06em;color:var(--accent);display:block}
.dep{font-size:11.5px;color:var(--ink3)}

/* ---- risks ---- */
.rgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(430px,1fr));gap:12px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:14px;
  box-shadow:var(--shadow);border-left:3px solid var(--ink3)}
.card.hidden{display:none}
.card.p-max{border-left-color:var(--crit)} .card.p-hi{border-left-color:var(--pre)}
.chead{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
.rid2{font-family:var(--fm);font-size:10px;color:var(--ink3)}
.badge{font-family:var(--fm);font-size:10px;padding:2px 7px;border-radius:3px;font-weight:700}
.b-max{background:var(--crit);color:#fff} .b-hi{background:var(--crit2);color:var(--crit)}
.b-mid{background:var(--pre2);color:var(--pre)} .b-low{background:var(--surface2);color:var(--ink3)}
.cev{font-size:14px;font-weight:700;line-height:1.5;margin:0 0 8px}
.crow{font-size:12.5px;line-height:1.6;margin:0 0 5px}
.clab{font-family:var(--fm);font-size:9.5px;letter-spacing:.05em;color:var(--ink3);display:block}
.cfix{margin-top:9px;padding-top:9px;border-top:1px solid var(--line2);display:flex;flex-direction:column;gap:7px}
.cfix .clab{color:var(--accent)}

dialog{border:1px solid var(--line);border-radius:10px;background:var(--surface);color:var(--ink);
  padding:16px;max-width:min(760px,92vw);width:100%;box-shadow:var(--shadow)}
dialog::backdrop{background:rgba(0,0,0,.45)}
dialog h3{font-family:var(--fd);margin:0 0 6px;font-size:17px}
dialog p{font-size:12.5px;color:var(--ink2);margin:0 0 10px}
dialog textarea{width:100%;height:220px;font-family:var(--fm);font-size:10.5px;
  border:1px solid var(--line);border-radius:6px;background:var(--paper);color:var(--ink);padding:8px}
.dlgbtns{display:flex;gap:8px;justify-content:flex-end;margin-top:10px}
ol.steps{font-size:12.5px;color:var(--ink2);margin:0 0 10px;padding-left:1.3em}
ol.steps li{margin-bottom:3px}

footer{border-top:1px solid var(--line);padding:22px 0 60px;color:var(--ink3);font-size:11.5px}
@media (max-width:760px){
  .row{grid-template-columns:22px 1fr}
  .meta{grid-column:2;justify-content:flex-start;padding-top:4px}
  .rgrid{grid-template-columns:1fr}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""


JS = r"""
const D = window.__WBS__;
const $ = (s,r=document)=>r.querySelector(s);
const $$ = (s,r=document)=>[...r.querySelectorAll(s)];
const esc = s => String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

/* ---------- tabs ---------- */
$$(".tab").forEach(b=>b.addEventListener("click",()=>{
  $$(".tab").forEach(x=>x.setAttribute("aria-selected", x===b ? "true":"false"));
  $$(".panel").forEach(p=>p.classList.toggle("is-on", p.id==="p-"+b.dataset.tab));
  window.scrollTo({top:0});
}));

/* ---------- base date ---------- */
function ym(base, add){
  const d = new Date(base+"T00:00:00");
  if(isNaN(d)) return "";
  d.setMonth(d.getMonth()+add);
  return d.getFullYear()+"/"+(d.getMonth()+1);
}
let BASE = localStorage.getItem("lifewbs-base") || "2026-10-01";

/* ---------- ① roadmap ---------- */
function renderRoadmap(){
  const G = D.gantt;
  const BIRTH = (D.phases.find(p=>p.id==="P11")||{start:37}).start;
  const EXAM = D.phases.findIndex(p=>p.id==="P17");
  const cols = [];
  for(let k=0;k<G;k++){
    const d = new Date(BASE+"T00:00:00"); d.setMonth(d.getMonth()+k);
    cols.push({y:d.getFullYear(), jan:d.getMonth()===0, birth:k===BIRTH});
  }
  const gcls = k => "gcell"+(cols[k].jan?" yr":"")+(cols[k].birth?" birth":"");
  const W = [38,100,56,210,96,200,280,78,210];
  let h = "<table class='rm'><colgroup>";
  W.forEach(w=>h+="<col style='width:"+w+"px'>");
  for(let k=0;k<G;k++) h+="<col style='width:6px'>";
  h += "</colgroup><thead>";
  h += "<tr><th colspan='9' class='yrgap sticky1'></th>";
  let k=0;
  while(k<G){
    const y=cols[k].y; let n=0;
    while(k+n<G && cols[k+n].y===y) n++;
    h += "<th colspan='"+n+"' class='yrlab'>"+(n>=4?y:"")+"</th>";
    k+=n;
  }
  h += "</tr><tr>";
  h += "<th class='sticky1'>ID</th><th class='sticky2'>フェーズ</th><th>子の年齢</th><th>ゴール（完了条件）</th><th>予定</th>"
     + "<th>マイルストーン</th><th>決めること</th><th>費用(万円)</th><th>最大リスク</th>";
  for(let j=0;j<G;j++)
    h += "<th class='"+gcls(j)+"'"+(cols[j].birth?" title='出産'":"")+"></th>";
  h += "</tr></thead><tbody>";
  let lo=0, hi=0;
  D.phases.forEach((p,i)=>{
    const end = p.start + p.dur - 1;
    lo += p.lo; hi += p.hi;
    const tone = i>=EXAM ? "exam" : (i<8 ? "pre" : "post");
    h += "<tr><td class='num sticky1'>"+p.id+"</td><td class='sticky2'><strong>"+esc(p.name)+"</strong></td>"
      + "<td class='num'>"+esc(p.age)+"</td>"
      + "<td>"+esc(p.goal)+"</td>"
      + "<td class='num'>"+ym(BASE,p.start)+"<br>〜"+ym(BASE,end)+"</td>"
      + "<td>"+esc(p.ms)+"</td><td>"+esc(p.decide)+"</td>"
      + "<td class='num'>"+p.lo+"〜"+p.hi+"</td><td>"+esc(p.risk)+"</td>";
    for(let k=0;k<G;k++){
      const on = k>=p.start && k<=end;
      h += "<td class='"+gcls(k)+"'>"+(on?"<span class='gbar "+tone+"'></span>":"")+"</td>";
    }
    h += "</tr>";
  });
  h += "<tr><td class='sticky1'></td><td class='sticky2'><strong>合計</strong></td><td colspan='5'></td>"
     + "<td class='num'><strong>"+lo+"〜"+hi+"</strong></td>"
     + "<td>※ 同棲開始から子ども12歳までの総額。ご祝儀・親の援助・給付金は差し引く前</td>";
  for(let k=0;k<G;k++) h += "<td class='"+gcls(k)+"'></td>";
  h += "</tr></tbody></table>";
  $("#rm").innerHTML = h;
}

/* ---------- ② wbs ---------- */
const KEY = "lifewbs-done-v1";
let done = {};
try{ done = JSON.parse(localStorage.getItem(KEY)||"{}"); }catch(e){ done={}; }

function renderWbs(){
  const frag = D.tasks.map(t=>{
    const law = t.kind==="法定";
    let d = "";
    if(t.ronten||t.opts||t.axis||t.dep){
      d = "<div class='detail'>"
        + (t.ronten?"<div class='dblk'><span class='dlab'>論点・決めること</span>"+esc(t.ronten)+"</div>":"")
        + (t.opts?"<div class='dblk'><span class='dlab'>選択肢・候補</span>"+esc(t.opts)+"</div>":"")
        + (t.axis?"<div class='dblk'><span class='dlab'>判断軸・注意点</span>"+esc(t.axis)+"</div>":"")
        + (t.dep?"<div class='dep'>先行："+esc(t.dep)+"</div>":"")
        + "</div>";
    }
    return "<div class='row row--"+(t.lv===2?"task":"step")+"' data-id='"+t.id+"' data-ph='"+t.ph
      + "' data-cat='"+esc(t.cat)+"' data-kind='"+esc(t.kind)+"' data-lv='"+t.lv+"'>"
      + "<input type='checkbox' class='tick' data-k='"+t.id+"' aria-label='"+t.id+" 完了'>"
      + "<label class='rmain' for-id='"+t.id+"'><span class='rid'>"+t.id+"</span>"
      + "<span class='rt'>"+esc(t.task)+"</span>"
      + (t.dod?"<span class='rdod'>"+esc(t.dod)+"</span>":"")
      + "</label><div class='meta'>"
      + (law?"<span class='chip c-law'>法定</span>":"")
      + "<span class='chip c-when'>"+ym(BASE,t.m)+"</span>"
      + "<span class='chip c-who'>"+esc(t.who)+"</span>"
      + (t.eff?"<span class='chip c-eff'>"+esc(t.eff)+"</span>":"")
      + (t.cost&&t.cost!=="-"?"<span class='chip c-cost'>"+esc(t.cost)+"</span>":"")
      + "</div>"+d+"</div>";
  }).join("");
  $("#wbs").innerHTML = frag;
  $$("#wbs .tick").forEach(cb=>{
    cb.checked = !!done[cb.dataset.k];
    paint(cb);
    cb.addEventListener("change",()=>{
      if(cb.checked) done[cb.dataset.k]=1; else delete done[cb.dataset.k];
      try{ localStorage.setItem(KEY, JSON.stringify(done)); }catch(e){}
      paint(cb); progress();
    });
  });
  $$("#wbs .rmain").forEach(l=>l.addEventListener("click",e=>{
    const cb = l.parentElement.querySelector(".tick");
    cb.checked = !cb.checked; cb.dispatchEvent(new Event("change"));
  }));
}
function paint(cb){ cb.closest(".row").classList.toggle("is-done", cb.checked); }
function progress(){
  const all = $$("#wbs .tick"), n = all.filter(c=>c.checked).length;
  const pct = all.length? Math.round(n/all.length*100):0;
  $("#pf").style.width = pct+"%";
  $("#pn").textContent = n+" / "+all.length+"  ("+pct+"%)";
}
function filterWbs(){
  const ph=$("#f-ph").value, cat=$("#f-cat").value, kind=$("#f-kind").value,
        q=$("#f-q").value.trim().toLowerCase(),
        hideStep=$("#f-step").getAttribute("aria-pressed")==="true",
        hideDone=$("#f-done").getAttribute("aria-pressed")==="true";
  let shown=0;
  $$("#wbs .row").forEach(r=>{
    let ok = (!ph||r.dataset.ph===ph) && (!cat||r.dataset.cat===cat) && (!kind||r.dataset.kind===kind);
    if(ok && hideStep && r.dataset.lv==="3") ok=false;
    if(ok && hideDone && r.classList.contains("is-done")) ok=false;
    if(ok && q) ok = r.textContent.toLowerCase().includes(q);
    r.classList.toggle("hidden", !ok);
    if(ok) shown++;
  });
  $("#wcount").textContent = shown+"件表示";
}

/* ---------- ③ risks ---------- */
function prio(s){ return s>=16?["最優先","b-max","p-max"]:s>=12?["高","b-hi","p-hi"]:s>=6?["中","b-mid",""]:["低","b-low",""]; }
function renderRisks(){
  const arr = [...D.risks];
  if($("#f-sort").value==="score") arr.sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id));
  $("#risks").innerHTML = arr.map(r=>{
    const [lab,bc,pc] = prio(r.score);
    return "<article class='card "+pc+"' data-ph='"+r.ph+"' data-cat='"+esc(r.cat)+"' data-prio='"+lab+"'>"
      + "<div class='chead'><span class='rid2'>"+r.id+"</span>"
      + "<span class='badge b-low'>"+r.ph+"</span><span class='badge b-low'>"+esc(r.cat)+"</span>"
      + "<span class='badge "+bc+"'>"+lab+" ／ "+r.score+"</span>"
      + "<span class='rid2'>確率"+r.p+"×影響"+r.imp+"</span></div>"
      + "<p class='cev'>"+esc(r.ev)+"</p>"
      + "<p class='crow'><span class='clab'>典型的な場面</span>"+esc(r.scene)+"</p>"
      + "<p class='crow'><span class='clab'>早期サイン（黄信号）</span>"+esc(r.sign)+"</p>"
      + "<p class='crow'><span class='clab'>相手側から見えている景色</span>"+esc(r.view)+"</p>"
      + "<div class='cfix'>"
      + "<p class='crow'><span class='clab'>予防策（起きる前に）</span>"+esc(r.prev)+"</p>"
      + "<p class='crow'><span class='clab'>発生時の初動（24時間以内）</span>"+esc(r.first)+"</p>"
      + "<p class='crow'><span class='clab'>再発防止（構造の変更）</span>"+esc(r.fix)+"</p>"
      + "</div></article>";
  }).join("");
  filterRisks();
}
function filterRisks(){
  const ph=$("#r-ph").value, cat=$("#r-cat").value, pr=$("#r-prio").value,
        q=$("#r-q").value.trim().toLowerCase();
  let n=0;
  $$("#risks .card").forEach(c=>{
    let ok=(!ph||c.dataset.ph===ph)&&(!cat||c.dataset.cat===cat)&&(!pr||c.dataset.prio===pr);
    if(ok&&q) ok=c.textContent.toLowerCase().includes(q);
    c.classList.toggle("hidden",!ok); if(ok) n++;
  });
  $("#rcount").textContent = n+"件表示";
}

/* ---------- export ---------- */
function tsv(rows){ return rows.map(r=>r.map(c=>String(c==null?"":c).replace(/[\t\n\r]/g," ")).join("\t")).join("\n"); }
function tsvRoadmap(){
  const head=["ID","フェーズ","子の年齢","ゴール（完了条件）","期間(月)","開始(経過月)","終了(経過月)",
    "予定開始","予定完了","主要マイルストーン","このフェーズで決めること","費用下限(万円)","費用上限(万円)","想定される最大リスク","状態"];
  const rows=[head];
  D.phases.forEach(p=>{const e=p.start+p.dur-1;
    rows.push([p.id,p.name,p.age,p.goal,p.dur,p.start,e,ym(BASE,p.start),ym(BASE,e),p.ms,p.decide,p.lo,p.hi,p.risk,"未着手"]);});
  return tsv(rows);
}
function tsvWbs(){
  const head=["WBS-ID","フェーズ","中分類","Lv","タスク／実行ステップ","完了の定義","論点・決めること",
    "選択肢・候補","判断軸・注意点","経過月","目安時期","区分","担当","所要目安","費用目安","先行して終わっていること","状態","メモ"];
  const rows=[head];
  D.tasks.forEach(t=>rows.push([t.id,t.ph,t.cat,t.lv,t.task,t.dod,t.ronten,t.opts,t.axis,t.m,
    ym(BASE,t.m),t.kind,t.who,t.eff,t.cost,t.dep,done[t.id]?"完了":"未着手",""]));
  return tsv(rows);
}
function tsvRisks(){
  const head=["リスクID","フェーズ","分類","リスク事象","典型的な場面","早期サイン","相手側から見えている景色",
    "確率","影響","スコア","優先度","予防策","発生時の初動","再発防止","オーナー","見直し","状態"];
  const rows=[head];
  D.risks.forEach(r=>rows.push([r.id,r.ph,r.cat,r.ev,r.scene,r.sign,r.view,r.p,r.imp,r.score,
    prio(r.score)[0],r.prev,r.first,r.fix,r.owner,"月1回","未着手"]));
  return tsv(rows);
}
function openCopy(title, text){
  $("#dlg-title").textContent = title;
  const ta = $("#dlg-ta"); ta.value = text;
  $("#dlg").showModal(); ta.focus(); ta.select();
  $("#dlg-msg").textContent = "";
}
$("#dlg-copy").addEventListener("click",async()=>{
  const ta=$("#dlg-ta"); ta.select();
  try{ await navigator.clipboard.writeText(ta.value); $("#dlg-msg").textContent="コピーしました"; }
  catch(e){
    try{ document.execCommand("copy"); $("#dlg-msg").textContent="コピーしました"; }
    catch(e2){ $("#dlg-msg").textContent="自動コピーができませんでした。Ctrl/Cmd + C を押してください"; }
  }
});
$("#dlg-close").addEventListener("click",()=>$("#dlg").close());
$$("[data-copy]").forEach(b=>b.addEventListener("click",()=>{
  const k=b.dataset.copy;
  if(k==="rm") openCopy("① ロードマップ", tsvRoadmap());
  if(k==="wbs") openCopy("② WBS（"+D.tasks.length+"行）", tsvWbs());
  if(k==="risk") openCopy("③ リスク管理表（"+D.risks.length+"件）", tsvRisks());
}));

/* ---------- init ---------- */
function fillSelect(sel, vals, label){
  sel.innerHTML = "<option value=''>"+label+"</option>" + vals.map(v=>"<option>"+esc(v)+"</option>").join("");
}
fillSelect($("#f-ph"), [...new Set(D.tasks.map(t=>t.ph))], "全フェーズ");
fillSelect($("#f-cat"), [...new Set(D.tasks.map(t=>t.cat))], "全カテゴリ");
fillSelect($("#f-kind"), ["法定","推奨","任意"], "全区分");
fillSelect($("#r-ph"), [...new Set(D.risks.map(r=>r.ph))], "全フェーズ");
fillSelect($("#r-cat"), [...new Set(D.risks.map(r=>r.cat))], "全分類");
fillSelect($("#r-prio"), ["最優先","高","中","低"], "全優先度");

$("#base").value = BASE;
$("#base").addEventListener("change",()=>{
  BASE = $("#base").value || "2026-10-01";
  try{ localStorage.setItem("lifewbs-base", BASE); }catch(e){}
  renderRoadmap(); renderWbs(); progress(); filterWbs();
});
["f-ph","f-cat","f-kind"].forEach(id=>$("#"+id).addEventListener("change",filterWbs));
$("#f-q").addEventListener("input",filterWbs);
["f-step","f-done"].forEach(id=>$("#"+id).addEventListener("click",e=>{
  const on = e.currentTarget.getAttribute("aria-pressed")!=="true";
  e.currentTarget.setAttribute("aria-pressed", on?"true":"false"); filterWbs();
}));
["r-ph","r-cat","r-prio"].forEach(id=>$("#"+id).addEventListener("change",filterRisks));
$("#r-q").addEventListener("input",filterRisks);
$("#f-sort").addEventListener("change",renderRisks);

renderRoadmap(); renderWbs(); progress(); filterWbs(); renderRisks();
"""


def main():
    data = build_data()
    lv2 = sum(1 for t in data["tasks"] if t["lv"] == 2)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    html = """<title>同棲〜結婚〜妊活〜出産〜子ども12歳のWBS</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>%(css)s</style>

<header class="mast"><div class="wrap">
  <p class="eyebrow">Work Breakdown Structure &amp; Risk Register &nbsp;/&nbsp; 2026-08</p>
  <h1>同棲 → 結婚 → 妊活 → 出産 → 子ども12歳（中学受験）</h1>
  <p class="lede">
    ①ロードマップは同棲開始から子ども12歳（中学受験の終了）までの約15年・%(phases)dフェーズ。
    ②WBSと③リスク管理表はそのうち子ども1歳までを詳細化したもので、
    %(tasks)d行のタスク（うち実行ステップ%(steps)d）と%(risks)d件の関係リスクがあります。
    各タブの「スプレッドシートにコピー」から、Googleスプレッドシートに貼り付けてそのまま使えます。
  </p>
  <div class="scale" aria-hidden="true">
    <span class="s-pre">同棲 ─ 結婚 ─ 式 ─ 妊活</span>
    <span class="s-b">出産</span>
    <span class="s-post">0歳 ── 保育園 ── 小学校 ── 中学受験 ── 12歳</span>
  </div>
  <p class="counts">%(phases)dフェーズ ／ %(tasks)dタスク ／ %(risks)dリスク</p>
</div></header>

<nav class="tabs"><div class="wrap tabs__in">
  <button class="tab" data-tab="rm" aria-selected="true">① ロードマップ</button>
  <button class="tab" data-tab="wbs" aria-selected="false">② WBS</button>
  <button class="tab" data-tab="risk" aria-selected="false">③ リスク管理表</button>
  <span class="spacer"></span>
  <label class="pnum" for="base">基準日</label>
  <input type="date" id="base" value="2026-10-01">
</div></nav>

<main>
<section class="panel is-on" id="p-rm"><div class="wrap">
  <h2 class="sec">① ロードマップ</h2>
  <p class="sub">同棲開始から子ども12歳（中学受験の終了）まで。基準日を変えると全フェーズの予定とガントが動きます。
     期間は標準モデルなので、妊活（P8）を中心に実態に合わせて読み替えてください。
     <strong>P14以降はロードマップのみ</strong>のざっくり粒度で、②WBSと③リスク管理表は P1〜P13（子ども1歳まで）が対象です。
     P15以降の境目は「4月の入学・進級」に合わせてあります（基準日2026年10月＝出産2029年11月の場合）。出産月がずれたら学年の境目も読み替えてください。</p>
  <div class="filters">
    <span class="lgd"><i class="i-pre"></i>出産前</span>
    <span class="lgd"><i class="i-post"></i>育児期</span>
    <span class="lgd"><i class="i-exam"></i>中学受験期</span>
    <span class="lgd"><i class="i-birth"></i>出産の月</span>
    <span class="spacer"></span>
    <button class="btn btn--go" data-copy="rm">スプレッドシートにコピー</button>
  </div>
  <div class="rmwrap" id="rm"></div>
</div></section>

<section class="panel" id="p-wbs"><div class="wrap">
  <h2 class="sec">② WBS <span class="pnum">（P1〜P13＝子ども1歳まで）</span></h2>
  <p class="sub">濃い行＝タスク、薄い行＝その中の実行ステップ。行をクリックするとチェックが入り、
     この端末に保存されます。意思決定タスクには論点・選択肢・判断軸が付いています。</p>
  <div class="filters">
    <select id="f-ph"></select><select id="f-cat"></select><select id="f-kind"></select>
    <input type="search" id="f-q" placeholder="キーワード検索（例：ベビーカー、保育園、育休）">
    <button class="btn" id="f-step" aria-pressed="false">ステップを隠す</button>
    <button class="btn" id="f-done" aria-pressed="false">未完了だけ</button>
    <span class="pnum" id="wcount"></span>
    <div class="pbar"><div class="pbar__t"><div class="pbar__f" id="pf"></div></div>
      <span class="pnum" id="pn"></span></div>
    <button class="btn btn--go" data-copy="wbs">スプレッドシートにコピー</button>
  </div>
  <div class="rows" id="wbs"></div>
</div></section>

<section class="panel" id="p-risk"><div class="wrap">
  <h2 class="sec">③ リスク管理表</h2>
  <p class="sub">各フェーズで配偶者との関係が悪化する想定リスク。
     「相手側から見えている景色」は、同じ事象を反対側から書いた欄です。
     確率・影響の初期値は一般的な想定なので、2人の実感に合わせて読み替えてください。</p>
  <div class="filters">
    <select id="r-ph"></select><select id="r-cat"></select><select id="r-prio"></select>
    <select id="f-sort"><option value="score">スコア順</option><option value="id">ID順</option></select>
    <input type="search" id="r-q" placeholder="キーワード検索（例：睡眠、義実家、育休）">
    <span class="pnum" id="rcount"></span>
    <button class="btn btn--go" data-copy="risk">スプレッドシートにコピー</button>
  </div>
  <div class="rgrid" id="risks"></div>
</div></section>
</main>

<dialog id="dlg">
  <h3 id="dlg-title"></h3>
  <p>Googleスプレッドシートへの移し方：</p>
  <ol class="steps">
    <li>下のテキストをコピーする（「コピー」ボタン、または Ctrl/Cmd + C）</li>
    <li>新しいスプレッドシートを開く（ブラウザで <strong>sheets.new</strong> と入力）</li>
    <li>セル <strong>A1</strong> を選んで貼り付ける。タブ区切りなので自動で列に分かれます</li>
  </ol>
  <textarea id="dlg-ta" readonly></textarea>
  <div class="dlgbtns">
    <span class="pnum" id="dlg-msg"></span>
    <button class="btn" id="dlg-close">閉じる</button>
    <button class="btn btn--go" id="dlg-copy">コピー</button>
  </div>
</dialog>

<footer><div class="wrap">
  2026年8月時点の一般的な情報に基づく計画テンプレートであり、医療上の助言ではありません。
  健康・治療・接種の判断は主治医に、制度の適用可否は自治体・健保・勤務先・ハローワークに確認してください。
  助成の金額・回数・申請時期は自治体差が大きいため、必ず住んでいる市区町村の公式情報で確認してください。
  商品・サービス名は選択肢の例であり、特定の推奨ではありません。
</div></footer>

<script>window.__WBS__=%(data)s;</script>
<script>%(js)s</script>
""" % {"css": CSS, "js": JS, "data": payload,
       "phases": len(data["phases"]),
       "tasks": len(data["tasks"]), "steps": len(data["tasks"]) - lv2,
       "risks": len(data["risks"])}

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %s (%d KB)" % (OUT, len(html.encode("utf-8")) // 1024))


if __name__ == "__main__":
    main()
