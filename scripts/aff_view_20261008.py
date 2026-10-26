# -*- coding: utf-8 -*-
"""広告枠の表示とクリックを同じ枠IDで追えるようにする（2026-10-08）

    python scripts/aff_view_20261008.py --check    対象ページと現状を出す（書き込まない）
    python scripts/aff_view_20261008.py --apply    計測スクリプト（AFF-VIEW2）を差し込む

背景: 9/27 の AFF-VIEW（scripts/aff_only_20260927.py）は、同スクリプトが扱った約15ページにしか入っておらず、
Oisix とバチェラーデートの枠では表示（affv_）が一度も記録されていなかった。また、診断の結果を JS で描く
ツール（婚活タイプ診断・産後回復チェック）の広告は読み込み後に現れるため、読み込み時に1回だけ探す AFF-VIEW
では拾えず、リンクに id も無いのでクリックも枠を特定できなかった。

AFF-VIEW2 がやること（本文・広告の文言・リンク先には触らない。</body> の直前に1つ足すだけ）:
  1. rel に sponsored を含む広告リンク（px.a8.net / t.afi-b.com）に id が無ければ、実行時に付ける
     （Oisix→aff-oisix、バチェラーデート→aff-bachelor、それ以外→aff-<a8matの2番目の値>）。
     GA4 内蔵の click は押した時点の id を linkId に入れるので、表示とクリックが同じ id になる。
  2. 表示: 枠が画面に50%以上入ったら affv_<id> を1回送る（AFF-VIEW と同じ規則）。既に AFF-VIEW が
     見ている枠は二重に数えない。後から描かれた枠も MutationObserver で拾う。
  3. クリック: 押したら affc_<id> を送る。ただし同じセッション（sessionStorage）・同じ枠では1回だけ。
  4. 自社の検品アクセス（?noe_qa=1 で開いたブラウザ）と本番以外のホストでは送らない。
     ローカル確認用に window.__affv / window.__affc に積む。

対象: Oisix かバチェラーデートの広告があるページ＋婚活3ページ（10/8 の試験対象）。
判定待ちのページ（improvement-log.json の locks[] で期限が今日以降のもの、専業主婦の割合、
新生児の面会、ガルガル系）は除く。ロックが明けたら --apply を流し直せば入る（何度流しても同じ結果）。
"""
import datetime, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OISIX = "4B8B4Q+5CWKMY+3RK+2TBJQA"
BACHELOR = "4B88SU+EGYEYI+5SFC+BX3J6"
TRIAL = ["articles/with-seriousness-data", "articles/compare-popular", "tools/app-kekkonritsu-data"]
PROTECT_RE = re.compile(r"(garugaru|sengyoshufu-wariai|shinseiji-menkai)")
START, END = "<!-- AFF-VIEW2 -->", "<!-- /AFF-VIEW2 -->"
GATE = ("var h=location.hostname,ok=(h==='www.noe-match.com'||h==='noe-match.com');"
        "try{var m=/[?&]noe_qa=(0|1)/.exec(location.search);if(m)localStorage.setItem('noe_qa',m[1]);"
        "if(localStorage.getItem('noe_qa')==='1')ok=false;}catch(e){}")
JS = (START + "\n<script>(function(){" + GATE +
      "var MAP={'" + OISIX + "':'aff-oisix','" + BACHELOR + "':'aff-bachelor'};"
      "function nm(id){return id.slice(4).replace(/-/g,'_');}"
      "function send(n,arr){(window[arr]=window[arr]||[]).push(n);if(ok){try{gtag('event',n);}catch(e){}}}"
      "var io=('IntersectionObserver' in window)?new IntersectionObserver(function(es){es.forEach(function(x){"
      "if(!x.isIntersecting)return;io.unobserve(x.target);send('affv_'+nm(x.target.getAttribute('data-aff')),'__affv');});},"
      "{threshold:[0.5]}):null;"
      "function arm(a){if(a.getAttribute('data-affv2'))return;a.setAttribute('data-affv2','1');"
      "if(!a.id){var m=/a8mat=([^&]+)/.exec(a.href)||[],k=m[1]||'',id=MAP[k]||('aff-'+((k.split('+')[1]||'x').toLowerCase())),"
      "base=id,i=2;while(document.getElementById(id))id=base+'-'+(i++);a.id=id;}"
      "var b=a.closest('div,section,aside');if(!b||b.getElementsByTagName('a').length>2)b=a;"
      "if(io&&!a.closest('[data-aff]')){b.setAttribute('data-aff',a.id);io.observe(b);}"
      "a.addEventListener('click',function(){var n='affc_'+nm(a.id),s=false;"
      "try{if(sessionStorage.getItem(n))s=true;else sessionStorage.setItem(n,'1');}catch(e){}"
      "if(!s)send(n,'__affc');},true);}"
      "function scan(r){var as=(r||document).querySelectorAll('a[rel~=\"sponsored\"]');"
      "for(var i=0;i<as.length;i++){if(/(px\.a8\.net|t\.afi-b\.com)/.test(as[i].href))arm(as[i]);}}"
      "scan();if('MutationObserver' in window)new MutationObserver(function(){scan();})"
      ".observe(document.body,{childList:true,subtree:true});})();</script>\n" + END + "\n")
JS_RE = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)


def active_locks():
    today = datetime.date.today().isoformat()
    d = json.load(io.open(os.path.join(ROOT, "agent", "seo", "improvement-log.json"), encoding="utf-8"))
    return {l["path"].strip("/") for l in d.get("locks", []) if l.get("until", "") >= today}


def targets():
    locks = active_locks()
    out, skipped = [], []
    for base in ("articles", "tools"):
        for d in sorted(os.listdir(os.path.join(ROOT, base))):
            slug = base + "/" + d
            p = os.path.join(ROOT, slug, "index.html")
            if not os.path.isfile(p):
                continue
            s = io.open(p, encoding="utf-8").read()
            if not (OISIX in s or BACHELOR in s or slug in TRIAL):
                continue
            if slug in locks or PROTECT_RE.search(slug):
                skipped.append(slug)
            else:
                out.append((slug, p, s))
    return out, skipped


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    apply = "--apply" in sys.argv
    out, skipped = targets()
    n = 0
    for slug, p, s in out:
        base = JS_RE.sub("", s)
        assert base.count("</body>") == 1, slug
        t = base.replace("</body>", JS + "</body>", 1)
        state = "変更なし" if t == s else ("差し込んだ" if apply else "差し込む")
        print("  %-8s %s" % (state, slug))
        if t != s and apply:
            io.open(p, "w", encoding="utf-8", newline="").write(t)
            n += 1
    print("対象 %dページ（書き込み %d）" % (len(out), n))
    print("除外（判定待ち）%dページ: %s" % (len(skipped), ", ".join(skipped)))


if __name__ == "__main__":
    main()
