# -*- coding: utf-8 -*-
"""16タイプ（MBTI）×星座の恋愛相性占いを生成する（2026-10-27）

  python scripts/build_mbti_uranai.py

tools/aisho-uranai/index.html の見た目（CSS・ヘッダー・フッター・PR枠）を流用して
tools/mbti-aisho-uranai/index.html を作る。
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = 'mbti-aisho-uranai'
SITE = 'https://www.noe-match.com'
URL = f'{SITE}/tools/{SLUG}/'
TITLE = '16タイプ（MBTI）×星座でみる恋愛相性占い'
H_TITLE = TITLE + '（無料）'
META_TITLE = H_TITLE + '｜二人の相性度と恋のヒント'
DESC = ('二人の16タイプ（MBTI）と生年月日の星座を組み合わせて、恋愛の相性度・二人の関係タイプ・'
        'すれ違いやすい点・距離が縮まる話し方を表示する無料占いです。入力は送信・保存しません。')
OG_DESC = '二人の16タイプ（MBTI）と星座から、恋愛の相性度と関係タイプ、距離が縮まるヒントを表示します。'

TYPES = {
    'INTJ': ('理想を設計する人', '恋愛にも筋道を求め、相手を「長く一緒に歩ける人か」で見極める傾向があります。好意は言葉より行動で示すタイプ。一度信頼すると、驚くほど一途です。'),
    'INTP': ('考えを分かち合いたい人', '好きな人とは、とことん話し込める関係を求めます。感情表現は控えめでも、相手の考えに本気で興味を持つのがこのタイプの愛情表現です。'),
    'ENTJ': ('二人の未来を引っぱる人', '恋愛でも目標を持ち、二人でどこへ向かうかをはっきりさせたい傾向があります。頼れる反面、相手のペースを待つのは少し苦手です。'),
    'ENTP': ('恋を面白くする人', '刺激と会話のテンポを大切にし、退屈しない関係を好みます。議論も愛情の一部。飽きっぽく見えて、気の合う相手とは長く続きます。'),
    'INFJ': ('心の奥を分かり合いたい人', '表面的なやりとりより、深いところでつながれる相手を求めます。相手の気持ちを先回りして察するぶん、自分の本音は後回しにしがちです。'),
    'INFP': ('理想の愛を信じる人', '恋愛に純粋な理想を持ち、心から通じ合える相手を探します。好きになると想いは深く、ささいな言葉にも敏感に反応します。'),
    'ENFJ': ('相手を輝かせる人', '好きな人の成長や幸せを、自分のことのように喜ぶタイプです。尽くし上手な一方、相手からの反応が少ないと不安になりやすい面もあります。'),
    'ENFP': ('ときめきを運ぶ人', '気持ちが表に出やすく、恋の始まりのドキドキを全力で楽しみます。自由でいたい気持ちと、深くつながりたい気持ちの両方を持っています。'),
    'ISTJ': ('約束を守り抜く人', '誠実さと安定を何より大切にし、関係を一歩ずつ確かに育てます。派手な愛情表現はなくても、約束を守り続けることで想いを伝えます。'),
    'ISFJ': ('そっと支え続ける人', '相手の好みや体調を細やかに覚えていて、さりげなく支えるタイプです。我慢をため込みやすいので、甘えられる相手がいると安心します。'),
    'ESTJ': ('頼れる段取り上手', '関係をきちんと形にしたい気持ちが強く、デートも将来の話も段取りよく進めます。言葉はストレートですが、責任感の強さが魅力です。'),
    'ESFJ': ('二人の時間を大切にする人', '記念日や小さな気づかいを大事にし、相手を喜ばせることに全力を注ぎます。周りとの調和も重視するため、二人の関係が周囲に認められると安心します。'),
    'ISTP': ('自然体でいたい人', '束縛の少ない、気楽で対等な関係を好みます。言葉数は少なめでも、困ったときに黙って手を貸すのがこのタイプのやさしさです。'),
    'ISFP': ('気持ちで寄り添う人', '穏やかで、相手の気持ちに静かに寄り添います。自分の好きなものや感覚を共有できる相手に、ゆっくりと心を開いていきます。'),
    'ESTP': ('一緒に楽しむ行動派', '考えるより先に動き、二人で過ごす時間を全力で楽しみます。重い話は苦手でも、相手が本当に困っているときは真っ先に駆けつけます。'),
    'ESFP': ('その場を明るくする人', '一緒にいる時間を楽しく彩るムードメーカーです。好きな気持ちを素直に表現し、相手にもたっぷり反応を返してほしいタイプです。'),
}

# 中央2文字（S/N＝ものの見方、T/F＝決め方）で4つの関係タイプ
PAIR = {
    'same-same': {
        'name': '心の言葉が通じるふたり',
        'trend': 'ものの見方も、大事なことの決め方も近い組み合わせです。説明しなくても分かってもらえる安心感があり、出会ってすぐに「この人とは話が早い」と感じやすい関係です。',
        'gap': '似ているぶん、苦手なことも同じになりがちです。ふたりとも見落としている点があると、気づかないまま進んでしまうことがあります。',
        'talk': '大事なことを決めるときは「ふたりとも苦手なところはどこか」を一度だけ確認しましょう。そこだけ周りの意見を借りると、この組み合わせの強さがそのまま生きます。',
    },
    'same-diff': {
        'name': '同じ景色を、違う心で見るふたり',
        'trend': 'ものの見方は近いのに、決め方が違う組み合わせです。同じものに惹かれ、同じ話題で盛り上がれる一方で、相手の判断にはっとさせられることも多い関係です。',
        'gap': '一方は筋道で、もう一方は気持ちで決めるため、「冷たい」「感情的」とすれ違いやすくなります。見ているものが同じなので、なおさら分かってほしいと感じがちです。',
        'talk': '意見が分かれたら、まず「どう感じたか」と「どう考えたか」を順番に話すのがおすすめです。理屈と気持ちの両方がそろうと、ふたりの決断はぐっと強くなります。',
    },
    'diff-same': {
        'name': '違う景色を、同じ物差しで測るふたり',
        'trend': 'ものの見方は違っても、大事なことの決め方が近い組み合わせです。目のつけどころが違うので話が尽きず、それでいて最後の判断ではうなずき合える関係です。',
        'gap': '一方は目の前の事実を、もう一方は先の可能性を見るため、話の前提がずれることがあります。「今の話をしているの？」「将来の話をしているの？」がすれ違いの入口です。',
        'talk': '話し始めに「今の話」か「先の話」かをひとこと添えるだけで、ぐっと噛み合います。違う景色を見せ合えるのは、この組み合わせだけの楽しみです。',
    },
    'diff-diff': {
        'name': '正反対に惹かれ合うふたり',
        'trend': 'ものの見方も決め方も違う組み合わせです。自分にないものを持つ相手に強く惹かれやすく、一緒にいると世界が広がる、刺激的な関係です。',
        'gap': '違いが大きいぶん、言葉の受け取り方がずれて、悪気のないひとことで傷つくことがあります。最初の勢いが落ち着いたころが、ひとつの山場になりやすい組み合わせです。',
        'talk': '「さっきの、こういう意味？」と確かめるひとことを遠慮しないことです。違いを直そうとせず、役割分担として生かすと、ほかにない強い絆に育ちます。',
    },
}

EI = {
    'same': 'エネルギーの向き（外向・内向）が同じなので、休日の過ごし方や人付き合いの量で揉めにくい組み合わせです。',
    'diff': '外向と内向の組み合わせです。外に連れ出す役と、落ち着ける場所をつくる役に自然と分かれ、バランスのとれた関係になりやすいです。',
}
JP = {
    'same': '計画の立て方（きっちり・柔軟）が同じなので、デートや旅行の進め方で気疲れしにくい組み合わせです。',
    'diff': 'きっちり派と柔軟派の組み合わせです。予定は大枠だけ決めて、当日の自由時間を残しておくとお互い心地よく過ごせます。',
}
ELEM = {
    'same': '星座のエレメントが同じで、感覚のリズムが合いやすい星回りです。一緒にいるだけで落ち着ける時間が増えていきます。',
    'comp': '星座のエレメントが補い合う組み合わせ（火と風、地と水）です。相手の存在が、あなたの魅力をいちばん引き出してくれる星回りです。',
    'diff': '星座のエレメントが異なる組み合わせです。最初は新鮮さが、時間がたつと「違うからこそ頼れる」安心感が育つ星回りです。',
}

FAQ = [
    ('自分のタイプが分からない場合はどうすればいいですか？',
     '無料の性格診断サイトなどで一度調べてから入力すると、結果をより楽しめます。迷う場合は、近いと思う2つのタイプでそれぞれ試し、当てはまるほうを読んでみてください。'),
    ('相性度はどうやって決まりますか？',
     '二人の16タイプの4つの指標（外向・内向、ものの見方、決め方、計画の立て方）の組み合わせと、生年月日から出した星座のエレメントの相性を合わせて点数にしています。どの組み合わせも80%以上になるように作っており、低い点数で関係を否定するものではありません。'),
    ('相性が悪いタイプはありますか？',
     'この占いでは相性を良し悪しで分けていません。似ている二人には似ているなりの、違う二人には違うなりの強みとすれ違いやすい点があり、それぞれに距離が縮まるヒントを用意しています。'),
    ('入力した内容は保存されますか？',
     '選んだタイプと生年月日はお使いのブラウザの中だけで計算し、当サイトのサーバーや第三者には送信せず、保存もしません。'),
    ('これは公式の性格検査ですか？',
     'いいえ。一般に広く知られている16タイプの考え方と星座占いを組み合わせた、恋愛を楽しむための占いです。公式の検査や診断ではありません。'),
]


def esc(s):
    import html
    return html.escape(s, quote=True)


def type_opts(ph):
    h = f'<option value="">{ph}</option>'
    for t, (nick, _) in TYPES.items():
        h += f'<option value="{t}">{t}（{nick}）</option>'
    return h


def main():
    src = open(os.path.join(ROOT, 'tools', 'aisho-uranai', 'index.html'), encoding='utf-8').read()
    css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
    css += '.calc .type-sel{margin-bottom:8px}\n.score-bar{height:8px;background:var(--hair);border-radius:4px;overflow:hidden;max-width:260px;margin:8px auto 0}\n.score-bar i{display:block;height:100%;background:var(--acc)}\n.tm-note{font-size:.72rem;color:var(--sub);margin-top:22px}\n'
    year_sel = re.search(r'(<select id="ay".*?</select>)\s*(<select id="am".*?</select>)\s*(<select id="ad".*?</select>)', src, re.S)
    ay, am, ad = year_sel.groups()

    def person(prefix, label):
        y = ay.replace('id="ay"', f'id="{prefix}y"').replace('あなたの生年月日', f'{label}の生年月日')
        m = am.replace('id="am"', f'id="{prefix}m"').replace('あなたの生年月日', f'{label}の生年月日')
        d = ad.replace('id="ad"', f'id="{prefix}d"').replace('あなたの生年月日', f'{label}の生年月日')
        return f"""<div class="fld"><span class="person-ttl">{label}</span>
    <select class="type-sel" id="{prefix}t" aria-label="{label}の16タイプ">{type_opts('16タイプを選ぶ')}</select>
    <div class="date-row">
      {y}
      {m}
      {d}
    </div></div>"""

    head_top = src.split('<style>')[0]
    head_top = re.sub(r'<title>.*?</title>', f'<title>{META_TITLE}</title>', head_top)
    head_top = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{esc(DESC)}">', head_top)
    head_top = head_top.replace('/tools/aisho-uranai/', f'/tools/{SLUG}/')
    head_top = re.sub(r'(og:title" content=")[^"]*', r'\g<1>' + H_TITLE, head_top)
    head_top = re.sub(r'(twitter:title" content=")[^"]*', r'\g<1>' + H_TITLE, head_top)
    head_top = re.sub(r'(og:description" content=")[^"]*', r'\g<1>' + OG_DESC, head_top)
    head_top = re.sub(r'(twitter:description" content=")[^"]*', r'\g<1>' + OG_DESC, head_top)

    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": H_TITLE, "url": URL,
              "applicationCategory": "LifestyleApplication", "operatingSystem": "All", "inLanguage": "ja",
              "description": DESC, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
              "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": SITE + "/"}}
    bc_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": SITE + "/#tools"},
        {"@type": "ListItem", "position": 3, "name": H_TITLE}]}
    ld = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in (faq_ld, app_ld, bc_ld))

    header = re.search(r'(<header>.*?</header>)', src, re.S).group(1)
    footer = re.search(r'(<footer>.*?</footer>)', src, re.S).group(1)
    prbox = re.search(r'(<div class="prbox">.*?</div>)', src, re.S).group(1)
    prbox = re.sub(r'<p class="pr-p">.*?</p>', '<p class="pr-p">あの人の本当の気持ちや、二人のこれから。プロの占い師に電話で直接みてもらえます。</p>', prbox)

    type_rows = ''.join(f'<tr><td>{t}</td><td style="text-align:left">{nick}</td></tr>' for t, (nick, _) in TYPES.items())
    pair_list = ''.join(f'<li><strong>{p["name"]}</strong>——{p["trend"].split("。")[0]}。</li>' for p in PAIR.values())
    faq_html = ''.join(f'<h3>Q{i}. {q}</h3><p>{a}</p>\n' for i, (q, a) in enumerate(FAQ, 1))

    body = f"""<body>
{header}
<div class="breadcrumb"><div class="wrap"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ {H_TITLE}</div></div>
<main class="wrap">
<div class="tool-hero" style="background-image:url('../../images/lp/room-light.jpg')"><div class="tool-hero-inner">
<svg class="hero-mark" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><circle cx="32" cy="32" r="31" fill="#f7f5f2"/><image href="../../images/emblems/couple.png" x="9" y="9" width="46" height="46"/></svg>
<h1>{H_TITLE}</h1>
<p>二人の16タイプと生年月日を選ぶだけ。性格の相性と星の巡りから、恋愛の相性度と距離が縮まるヒントを読みます。登録なし。</p>
</div></div>

<article>
<p class="pr-top">【PR】このページには広告（アフィリエイトリンク）が含まれます。</p>
<blockquote>二人の<strong>16タイプ</strong>と<strong>生年月日</strong>を選ぶと、<strong>恋愛の相性度</strong>、<strong>二人の関係タイプ</strong>、<strong>すれ違いやすい点</strong>、<strong>距離が縮まる話し方</strong>を表示します。</blockquote>
<div class="calc">
{person('a', 'あなた')}
{person('b', 'お相手')}
  <button class="calc-btn" id="run" type="button">相性を占う</button>
  <p class="err" id="err">タイプと生年月日をすべて正しく選んでください。</p>
</div>

<div class="result" id="res" aria-live="polite">
<div class="result-head">
<div class="lbl">二人の恋愛相性度</div>
<div class="num" id="rScore">—</div>
<div class="score-bar"><i id="rBar" style="width:0"></i></div>
<div class="type" id="rName"></div>
<div class="pair"><div class="cell">あなた<b id="rA"></b></div><div class="cell">お相手<b id="rB"></b></div></div>
<div class="wm">noe-match.com/tools/{SLUG}/</div>
</div>
<div class="result-body">
<div class="r-block"><h3>二人の関係</h3><p id="rTrend"></p></div>
<div class="r-block"><h3>すれ違いやすい点</h3><p id="rGap"></p></div>
<div class="r-block"><h3>距離が縮まる話し方</h3><p id="rTalk"></p></div>
<div class="r-block"><h3>過ごし方の相性</h3><p id="rLife"></p></div>
<div class="r-block"><h3>星の巡り</h3><p id="rStar"></p></div>
<div class="r-block"><h3>お相手の恋愛傾向</h3><p id="rPartner"></p></div>

<div class="share-block">
<div class="share-title">結果をシェアする</div>
<div class="share-btns">
<a class="share-btn x" id="shareX" href="#" target="_blank" rel="noopener">X でポスト</a>
<button class="share-btn copy" id="shareCopy" type="button">リンクをコピー</button>
</div></div>
{prbox}
<div class="next-links"><h3>あわせて読む・試す</h3><ul><li><a href="/tools/renai-type-shindan/">16タイプ恋愛診断（12問であなたの恋愛タイプがわかる）</a></li><li><a href="/tools/aisho-uranai/">生年月日でみる二人の相性占い</a></li><li><a href="/tools/seiza-renai-uranai/">星座でみる恋愛傾向占い</a></li><li><a href="/tools/suhi-kekkon-uranai/">数秘術でみる結婚観占い</a></li><li><a href="/tools/konkatsu-type-shindan/">婚活タイプ診断（自分に合う婚活の進め方を選ぶ）</a></li></ul></div>
</div>
</div>

<h2>相性の決め方</h2>
<p>この占いは、二人の<strong>16タイプの4つの指標</strong>と、生年月日から出した<strong>星座のエレメント</strong>（火・地・風・水）を組み合わせています。関係タイプは、ものの見方（S/N）と決め方（T/F）が同じか違うかで、次の4つに分かれます。</p>
<ul>{pair_list}</ul>
<p>さらに、外向・内向（E/I）と計画の立て方（J/P）から「過ごし方の相性」を、星座のエレメントから「星の巡り」を読み、すべてを合わせて相性度を出しています。</p>

<h2>16タイプの恋愛での呼び名</h2>
<p>結果に出てくる各タイプの呼び名は、恋愛での傾向をもとに当サイトが独自につけたものです。</p>
<div class="table-wrap"><table>
<thead><tr><th>タイプ</th><th>恋愛での呼び名</th></tr></thead>
<tbody>{type_rows}</tbody>
</table></div>
<p>星座だけで二人の相性を見たい方は<a href="/tools/aisho-uranai/">生年月日でみる二人の相性占い</a>もどうぞ。</p>
<p class="tm-note">MBTIは米国MBTI Trust, Inc.の登録商標です。本ページは同社・日本MBTI協会とは関係がなく、公式の検査や診断ではありません。</p>
</article>

<article><h2>よくある質問</h2>
{faq_html}</article>

<div class="related"><h2>関連する占い・診断・記事</h2><ul><li><a href="/tools/aisho-uranai/">生年月日でみる二人の相性占い｜二人の生年月日から、関係の傾向とすれ違いやすい点、話し方のヒントを読む</a></li><li><a href="/tools/seiza-renai-uranai/">星座でみる恋愛傾向占い｜生年月日から12星座を出し、恋愛の傾向と婚活で生かせるヒントを読む</a></li><li><a href="/tools/suhi-kekkon-uranai/">数秘術でみる結婚観占い｜生年月日からライフパスナンバーを出し、結婚観と話し合うと良いことを読む</a></li><li><a href="/articles/denwa-uranai-konkatsu/">婚活・恋愛の迷いを電話占いで話す前に</a></li></ul></div>
</main>
{footer}
<button id="top" onclick="scrollTo({{top:0,behavior:'smooth'}})">↑</button>
"""

    data = {
        'TYPES': {t: {'nick': n, 'love': l} for t, (n, l) in TYPES.items()},
        'PAIR': PAIR, 'EI': EI, 'JP': JP, 'ELEM': ELEM,
    }
    js = """<script>
(function(){
"use strict";
var SLUG='__SLUG__';
var TITLE='__TITLE__';
var PAGE_URL='__URL__';
var D=__DATA__;
var ELEMS=['火','地','風','水','火','地','風','水','火','地','風','水'];
var SIGN_NAMES=['牡羊座','牡牛座','双子座','蟹座','獅子座','乙女座','天秤座','蠍座','射手座','山羊座','水瓶座','魚座'];
function track(n,p){try{if(typeof gtag==='function')gtag('event',n,p);}catch(e){}}
function $(id){return document.getElementById(id);}
(function(){var max=new Date().getFullYear()-18;['ay','by'].forEach(function(id){var s=$(id);if(!s)return;var h='<option value="">年</option>';for(var y=max;y>=1940;y--)h+='<option value="'+y+'">'+y+'年</option>';s.innerHTML=h;});})();
function readDate(p){
  var y=+$(p+'y').value,m=+$(p+'m').value,d=+$(p+'d').value;
  if(!y||!m||!d)return null;
  var t=new Date(y,m-1,d);
  if(t.getFullYear()!==y||t.getMonth()!==m-1||t.getDate()!==d)return null;
  return {y:y,m:m,d:d};
}
var CUTS=[[1,20,10],[2,19,11],[3,21,0],[4,20,1],[5,21,2],[6,22,3],[7,23,4],[8,23,5],[9,23,6],[10,24,7],[11,23,8],[12,22,9]];
function signOf(m,d){var s=9;for(var i=0;i<CUTS.length;i++){if(m>CUTS[i][0]||(m===CUTS[i][0]&&d>=CUTS[i][1]))s=CUTS[i][2];}return s;}
function relOf(a,b){if(a===b)return 'same';var p=[a,b].sort().join('');if(p===['火','風'].sort().join('')||p===['地','水'].sort().join(''))return 'comp';return 'diff';}
var started=false;
[].forEach.call(document.querySelectorAll('.calc select'),function(el){el.addEventListener('change',function(){if(!started){started=true;track('uranai_start',{tool:SLUG});}});});
var lastResult='';
function setShare(score,name){
  lastResult=name;
  var text=TITLE+'で二人の相性は'+score+'%「'+name+'」でした｜Noe結婚設計室（無料）';
  $('shareX').href='https://x.com/intent/post?text='+encodeURIComponent(text)+'&url='+encodeURIComponent(PAGE_URL);
}
$('shareX').addEventListener('click',function(){track('uranai_share',{tool:SLUG,result:lastResult});});
$('shareCopy').addEventListener('click',function(){var b=$('shareCopy');try{navigator.clipboard.writeText(PAGE_URL).then(function(){b.textContent='コピーしました';setTimeout(function(){b.textContent='リンクをコピー';},1800);});}catch(e){}track('uranai_share',{tool:SLUG,result:lastResult});});
$('prLink').addEventListener('click',function(){track('uranai_pr_click',{tool:SLUG,result:lastResult});});
// 年齢はこのブラウザ内で計算するだけ（送信・保存しない）。18歳未満なら広告枠を出さない
function isMinor(dt){var n=new Date(),age=n.getFullYear()-dt.y;if(n.getMonth()+1<dt.m||(n.getMonth()+1===dt.m&&n.getDate()<dt.d))age--;return age<18;}
function showRes(a,b){var box=document.querySelector('.prbox');if(box){var mn=isMinor(a)||isMinor(b);box.hidden=mn;box.style.display=mn?'none':'';}
  $('err').style.display='none';$('res').classList.add('show');$('res').scrollIntoView({behavior:'smooth',block:'start'});}
onscroll=function(){$('top').classList.toggle('show',scrollY>300);};
$('run').addEventListener('click',function(){
  var ta=$('at').value,tb=$('bt').value,a=readDate('a'),b=readDate('b');
  if(!ta||!tb||!a||!b){$('err').style.display='block';return;}
  var sa=signOf(a.m,a.d),sb=signOf(b.m,b.d);
  var sn=ta[1]===tb[1],tf=ta[2]===tb[2],ei=ta[0]===tb[0],jp=ta[3]===tb[3];
  var rel=relOf(ELEMS[sa],ELEMS[sb]);
  var p=D.PAIR[(sn?'same':'diff')+'-'+(tf?'same':'diff')];
  var score=66+(sn?8:4)+(tf?6:4)+(ei?3:5)+(jp?4:2)+(rel==='comp'?6:rel==='same'?4:2);
  // 同じ組み合わせなら毎回同じ点数。生年月日から±1のゆらぎ（80〜95%に収める）
  score+=((a.d+b.d+a.m+b.m)%3)-1;
  score=Math.max(80,Math.min(95,score));
  $('rScore').innerHTML=score+'<small>%</small>';
  $('rBar').style.width=score+'%';
  $('rName').textContent=p.name;
  $('rA').textContent=ta+'・'+SIGN_NAMES[sa];
  $('rB').textContent=tb+'・'+SIGN_NAMES[sb];
  $('rTrend').textContent=p.trend;
  $('rGap').textContent=p.gap;
  $('rTalk').textContent=p.talk;
  $('rLife').textContent=D.EI[ei?'same':'diff']+D.JP[jp?'same':'diff'];
  $('rStar').textContent=D.ELEM[rel];
  $('rPartner').textContent=tb+'（'+D.TYPES[tb].nick+'）：'+D.TYPES[tb].love;
  setShare(score,p.name);
  showRes(a,b);
  track('uranai_complete',{tool:SLUG,result:p.name});
});
})();
</script>
</body>
</html>
"""
    js = (js.replace('__SLUG__', SLUG).replace('__TITLE__', TITLE).replace('__URL__', URL)
            .replace('__DATA__', json.dumps(data, ensure_ascii=False)))

    out = head_top + '<style>' + css + '</style>\n' + ld + '</head>\n' + body + js
    os.makedirs(os.path.join(ROOT, 'tools', SLUG), exist_ok=True)
    with open(os.path.join(ROOT, 'tools', SLUG, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(out)
    print('wrote', SLUG)


if __name__ == '__main__':
    main()
