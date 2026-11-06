# -*- coding: utf-8 -*-
"""ココナラ電話占いの【PR】枠を恋愛・婚活記事11本に足す（2026-11-04 CEO『ココナラ占いアフィリエイトを記事に貼って』）。
既存の占い記事12本と同じ部品（cta-mid・A8 a8mat=4B8BWW+FJNJQI+2PEO+C28PU・aff_click adv=coconala）。
置き場所: 「著者」の見出しの直前。無ければ「関連」の見出しの直前、それも無ければ </article> の直前（11/6 に app-plus-agency・omiai-guide・pairs-women は関連記事の前、hatsushon-nenmei-data は FAQ の前へ手で移した）。
除外: 11/3 に占いツールへの文中リンクを入れた10本（11/15 初動判定のため）・success-rate-data（12/5 判定まで固定）・compare-popular（ロック）。
二度実行しても重ねない（aff-coconala-art の印で判定）。"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://px.a8.net/svt/ejp?a8mat=4B8BWW+FJNJQI+2PEO+C28PU"
TAIL = "ココナラ電話占いでは、占い師ごとの1分あたりの鑑定料を見比べてから選べます。"
TEXT = {
    "with-guide": "心理テストの結果を、実際にやり取りしている相手との関わり方に当てはめて考えたいときは、占い師と話しながら整理する方法もあります。",
    "with-seriousness-data": "数字だけでは決めきれない「この相手とどう進めるか」を、誰かと話しながら整理したいときは、占い師に相談する方法もあります。",
    "shougai-mikonritsu-data": "統計は社会全体の傾向で、自分の結婚の時期や進め方はまた別の話です。気持ちを誰かと話して整理したいときは、占い師に相談する方法もあります。",
    "hatsushon-nenmei-data": "平均の年齢はあくまで目安で、結婚のタイミングは人それぞれです。自分にとっての時期の考え方を話して整理したいときは、占い師に相談する方法もあります。",
    "kekkon-madeno-kikan-data": "交際期間の長さにかかわらず、今の相手との先のことを誰かと話して整理したいときは、占い師に相談する方法もあります。",
    "omiai-guide": "やり取りしている相手との相性や進め方を、第三者と話しながら整理したいときは、占い師に相談する方法もあります。",
    "pairs-women": "マッチングした相手との相性や、次にどう動くかを誰かと話して整理したいときは、占い師に相談する方法もあります。",
    "civil-servant-guide": "出会いの場が限られるなかで、自分に合う相手像を話しながら整理したいときは、占い師に相談する方法もあります。",
    "over50-guide": "これからのパートナー選びについて、誰かと話しながら考えを整理したいときは、占い師に相談する方法もあります。",
    "app-plus-agency": "アプリにするか相談所にするかで迷う気持ちを、話しながら整理したいときは、占い師に相談する方法もあります。",
    "dousei-kekkon-hikaku": "同棲を始める前に、相手との相性や暮らし方の考え方を話して整理したいときは、占い師に相談する方法もあります。",
}
NOTICE = ('<p class="pr-notice" style="font-size:10px;color:#6f747a;border:none;padding:0;margin:4px 0 0;line-height:1.4">本ページはプロモーションを含みます</p>')
STYLE_INLINE =' style="background:#f7f5f2;border-left:2px solid #7c2e42;padding:20px 24px;margin:30px 0"'
BTN_INLINE = ' style="display:inline-block;background:#7c2e42;color:#fff;font-weight:500;padding:11px 28px;text-decoration:none;font-size:.84rem"'

def block(slug, has_css):
    box = '' if has_css else STYLE_INLINE
    btn = '' if has_css else BTN_INLINE
    t = '' if has_css else ' style="margin:0 0 12px;font-size:.9rem;line-height:1.9"'
    return (f'<div class="cta-mid" id="aff-coconala-art"{box}>\n'
            '<p class="cta-pr" style="font-size:10px;font-weight:400;color:#6f747a;margin:0 0 4px">PR</p>\n'
            f'<p class="cta-mid-t"{t}>{TEXT[slug]}{TAIL}</p>\n'
            f'<a class="cta-mid-b"{btn} href="{URL}" rel="nofollow sponsored noopener" target="_blank" '
            f"onclick=\"try{{gtag('event','aff_click',{{link_domain:'a8',page_slug:'/articles/{slug}/',adv:'coconala',place:'article'}});}}catch(e){{}}\">"
            'ココナラ電話占いの公式サイトを見る</a>\n'
            '<p style="font-size:12px;color:#8a8f95;margin:10px 0 0">1分ごとに料金がかかります。料金と新規登録の特典の条件は公式サイトで確認してください。</p>\n'
            '</div>\n')

def main():
    for slug in TEXT:
        f = os.path.join(ROOT, "articles", slug, "index.html")
        h = open(f, encoding="utf-8").read()
        if "aff-coconala-art" in h:
            print("skip(済)", slug); continue
        if "pr-notice\">" not in h:
            # 広告リンクが無かった記事: 他の記事と同じ表記を h1 の直後に足す
            if h.count("</h1>") != 1:
                print("STOP 広告表記なし・h1不明", slug); sys.exit(1)
            h = h.replace("</h1>", "</h1>\n" + NOTICE, 1)
            print("広告表記を追加", slug)
        has_css = ".cta-mid{" in h
        m = re.search(r'<h2[^>]*>[^<]*著者', h) or re.search(r'<h2 id="related"', h) or re.search(r'</article>', h)
        h = h[:m.start()] + block(slug, has_css) + h[m.start():]
        open(f, "w", encoding="utf-8", newline="").write(h)
        print("ok", slug, "css" if has_css else "inline", h[m.start()+len(block(slug, has_css)):m.start()+len(block(slug, has_css))+40].replace("\n", " "))

if __name__ == "__main__":
    main()
