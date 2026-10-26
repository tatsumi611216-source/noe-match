# -*- coding: utf-8 -*-
"""恋愛タイプ診断（12問・4軸16タイプ／当サイト独自）を生成する（2026-10-27）

  python scripts/build_renai_type.py

tools/aisho-uranai/index.html の見た目（CSS・ヘッダー・フッター・PR枠）を流用して
tools/renai-type-shindan/index.html を作る。タイプ名・軸・設問はすべて当サイト独自。
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = 'renai-type-shindan'
SITE = 'https://www.noe-match.com'
URL = f'{SITE}/tools/{SLUG}/'
TITLE = '16タイプ恋愛診断'
H_TITLE = TITLE + '（無料）'
META_TITLE = H_TITLE + '｜12問であなたの恋愛タイプと相性のいい相手がわかる'
DESC = ('12問に答えるだけで、恋の主導・距離感・恋の温度・愛情表現の4つの軸から、あなたの恋愛タイプを16種類で診断。'
        '恋の強み、気をつけたいこと、相性のいいタイプを表示する無料診断です。入力は送信・保存しません。')
OG_DESC = '12問で、あなたの恋愛タイプを16種類で診断。恋の強みと相性のいいタイプがわかります。'

# 軸：[左の極, 右の極]
AXES = [
    ('L', 'F', '恋の主導', '引っぱる', '寄り添う'),
    ('C', 'I', '距離感', 'べったり', 'ほどよく'),
    ('P', 'S', '恋の温度', '情熱', '安定'),
    ('W', 'A', '愛情表現', '言葉', '行動'),
]

# 各軸3問。a=左の極、b=右の極
QS = [
    (0, '気になる人ができたら？', '自分から誘ってきっかけをつくる', '相手から声がかかるのを待つ'),
    (0, 'デートの行き先は？', '自分でプランを立てて連れていきたい', '相手の行きたいところについていきたい'),
    (0, '付き合うかどうかの話は？', '自分からはっきり切り出す', '相手の言葉を待ちたい'),
    (1, '恋人とのLINEは？', '一日中ちょこちょこやりとりしたい', '用があるときと夜に少しで十分'),
    (1, '休日の理想は？', 'できるだけ恋人と一緒に過ごす', '一人の時間や友達との予定も大事'),
    (1, '恋人の交友関係は？', '誰とどこにいるか、なんとなく知っておきたい', 'お互い自由でいい'),
    (2, '恋に落ちるときは？', '一気に気持ちが燃え上がる', 'じわじわ好きになっていく'),
    (2, '恋人に求めるのは？', 'ドキドキやときめき', '安心感と居心地のよさ'),
    (2, 'ケンカしたら？', '感情をぶつけてでもその場で解決したい', '少し時間を置いて落ち着いて話したい'),
    (3, '好きな気持ちの伝え方は？', '「好き」と言葉にして伝える', '手料理や送り迎えなど行動で示す'),
    (3, 'うれしいのはどっち？', '心のこもったメッセージ', 'さりげなく手を貸してくれること'),
    (3, '記念日には？', '手紙やメッセージを用意する', '一緒に過ごす時間やプレゼントを用意する'),
]

T = {
    'LCPW': ('燃えるラブレター', '好きになったら一直線。気持ちを言葉にして真っすぐ届け、相手をぐいぐい恋の中へ引き込むタイプです。あなたといると、相手は「こんなに想われている」と実感できます。'),
    'LCPA': ('一途なナイト', '好きな人のためなら迷わず動く、行動派のロマンチストです。言葉より先に体が動き、困っているときには誰よりも早く駆けつけます。'),
    'LCSW': ('世話焼きキャプテン', '二人の関係を穏やかにリードしながら、言葉でこまめに気持ちを確かめ合うタイプです。安心できる関係を自分の手でつくっていけます。'),
    'LCSA': ('頼れる大樹', 'どっしり構えて、そばにいる人を守り続けるタイプです。派手さはなくても、一緒にいる時間の長さで愛情を証明していきます。'),
    'LIPW': ('自由な恋の詩人', '恋にときめきを求めながらも、自分の世界も大切にするタイプです。会えない時間も言葉の魅力で相手の心をつかみ続けます。'),
    'LIPA': ('風をまとう冒険家', '新しい場所や体験へ相手を連れ出し、恋を冒険に変えるタイプです。束縛はしないけれど、一緒にいる時間の熱量は人一倍です。'),
    'LISW': ('余裕のある参謀', '落ち着いて関係をリードし、言葉で相手の不安をほどくタイプです。自立した大人の恋を楽しめる、頼もしい存在です。'),
    'LISA': ('背中で語る職人', '口数は少なくても、やるべきことを着実にこなして相手を支えるタイプです。自分の時間を持ちつつ、二人の土台をしっかり固めます。'),
    'FCPW': ('甘えん坊のひだまり', '好きな人にはとことん甘えて、気持ちも素直に言葉にするタイプです。あなたの明るい愛情表現は、相手の心をあたためます。'),
    'FCPA': ('健気なひまわり', '好きな人のことをいつも想い、尽くすことに喜びを感じるタイプです。相手の一言で一日が輝く、まっすぐな心の持ち主です。'),
    'FCSW': ('おっとりティータイム', '穏やかな時間を一緒に過ごすことに幸せを感じるタイプです。小さな「ありがとう」や「好き」を自然に伝え合える関係を育てます。'),
    'FCSA': ('寄り添うクッション', 'そばにいるだけで相手をほっとさせる、包容力のあるタイプです。相手の変化にすぐ気づき、さりげなく支えます。'),
    'FIPW': ('気まぐれな月', '自分のペースを大切にしながらも、心の奥では深いときめきを求めるタイプです。ふとした瞬間の甘い言葉で、相手を夢中にさせます。'),
    'FIPA': ('静かに燃えるキャンドル', '表には出さなくても、心の中では情熱的な想いを灯し続けるタイプです。信じた相手には、行動で深い愛情を示します。'),
    'FISW': ('マイペースな聞き上手', '相手の話に耳を傾け、言葉で寄り添うのが得意なタイプです。お互いに自立した、心地よい距離感の恋を好みます。'),
    'FISA': ('森の木陰', '静かにそばにいて、相手が疲れたときの居場所になるタイプです。急がず焦らず、長く続く関係を育てていきます。'),
}

STRENGTH = {
    'L': '気持ちが決まったら自分から動けるので、恋のチャンスを逃しにくいこと。',
    'F': '相手のペースや気持ちを尊重できるので、一緒にいて居心地がいいと思われやすいこと。',
    'W': '気持ちを言葉にできるので、相手を不安にさせにくいこと。',
    'A': '口先だけでなく行動で示せるので、信頼が深まりやすいこと。',
}
CAUTION = {
    'C': '一緒にいたい気持ちが強いぶん、相手からの連絡が少ないと不安になりがちです。不安なときは「寂しい」と素直に伝えるほうが、確かめるより伝わります。',
    'I': '自分の時間を大切にするぶん、相手に「本当に好きなのかな」と思わせてしまうことがあります。会えない日にひとこと連絡を入れるだけで、印象は大きく変わります。',
    'P': '気持ちが盛り上がるのが早いぶん、落ち着いた時期に「冷めた？」と感じやすいところがあります。ドキドキが安心に変わるのは、関係が深まったサインです。',
    'S': '落ち着いた関係を好むぶん、恋の始まりで気持ちが伝わりにくいことがあります。最初のうちは、少し大げさなくらいに好意を見せると進展しやすくなります。',
}


def best_match(code):
    # 主導と愛情表現が反対、距離感と温度が同じ相手を「相性のいいタイプ」とする
    flip = {'L': 'F', 'F': 'L', 'W': 'A', 'A': 'W'}
    return flip[code[0]] + code[1] + code[2] + flip[code[3]]


def esc(s):
    return html.escape(s, quote=True)


def main():
    src = open(os.path.join(ROOT, 'tools', 'aisho-uranai', 'index.html'), encoding='utf-8').read()
    css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
    css += """.q{background:#fff;border:1px solid var(--hair);border-radius:6px;padding:14px 14px 12px;margin:0 0 12px}
.q .qt{font-weight:700;color:var(--ink);font-size:.92rem;margin:0 0 10px}
.q .qt span{color:var(--acc);margin-right:6px}
.q .opts{display:grid;gap:8px}
.q label{display:block;border:1px solid var(--line-strong);border-radius:4px;padding:10px 12px;font-size:.88rem;cursor:pointer;font-weight:500;margin:0;background:#fff}
.q input{position:absolute;opacity:0;pointer-events:none}
.q input:checked+label{border-color:var(--acc);background:#f3ecee;color:var(--acc);font-weight:700}
.q input:focus-visible+label{outline:2px solid var(--acc)}
.progress{font-size:.8rem;color:var(--sub);text-align:right;margin:4px 0 10px}
.axis-row{display:grid;grid-template-columns:4.5em 1fr 1fr;gap:6px;align-items:center;font-size:.8rem;margin:6px 0}
.axis-row .ax{font-weight:700;color:var(--ink)}
.axis-row .pole{padding:6px 4px;border-radius:4px;text-align:center;background:var(--alt);color:var(--sub)}
.axis-row .pole.on{background:var(--acc);color:#fff;font-weight:700}
.match a{font-weight:700}
.type-table td:first-child{white-space:nowrap}
"""
    ay, am, ad = re.search(r'(<select id="ay".*?</select>)\s*(<select id="am".*?</select>)\s*(<select id="ad".*?</select>)', src, re.S).groups()

    head_top = src.split('<style>')[0]
    head_top = re.sub(r'<title>.*?</title>', f'<title>{META_TITLE}</title>', head_top)
    head_top = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{esc(DESC)}">', head_top)
    head_top = head_top.replace('/tools/aisho-uranai/', f'/tools/{SLUG}/')
    for k in ('og:title', 'twitter:title'):
        head_top = re.sub(rf'({k}" content=")[^"]*', r'\g<1>' + H_TITLE, head_top)
    for k in ('og:description', 'twitter:description'):
        head_top = re.sub(rf'({k}" content=")[^"]*', r'\g<1>' + OG_DESC, head_top)

    FAQ = [
        ('ほかの恋愛タイプ診断と同じものですか？',
         'いいえ。4つの軸・設問・16タイプの名前はすべて当サイト（Noe結婚設計室）が独自に作ったもので、ほかの恋愛診断とは関係ありません。'),
        ('どちらにも当てはまる質問はどう答えればいいですか？',
         '迷ったら「好きな人の前での自分」に近いほうを選んでください。気分で結果が変わることもあるので、時間をおいてもう一度試すのもおすすめです。'),
        ('相性のいいタイプはどうやって決まりますか？',
         '距離感と恋の温度が同じで、恋の主導と愛情表現が反対になるタイプを「相性のいいタイプ」としています。求める関係の形が近く、役割は自然に補い合える組み合わせです。'),
        ('回答や生年月日は保存されますか？',
         '回答と生年月日はお使いのブラウザの中だけで計算し、当サイトのサーバーや第三者には送信せず、保存もしません。'),
    ]
    ld = [
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        {"@context": "https://schema.org", "@type": "WebApplication", "name": H_TITLE, "url": URL,
         "applicationCategory": "LifestyleApplication", "operatingSystem": "All", "inLanguage": "ja",
         "description": DESC, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": SITE + "/"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": SITE + "/#tools"},
            {"@type": "ListItem", "position": 3, "name": H_TITLE}]},
    ]
    ld_html = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)

    header = re.search(r'(<header>.*?</header>)', src, re.S).group(1)
    footer = re.search(r'(<footer>.*?</footer>)', src, re.S).group(1)
    prbox = re.search(r'(<div class="prbox">.*?</div>)', src, re.S).group(1)
    prbox = re.sub(r'<p class="pr-p">.*?</p>', '<p class="pr-p">あの人はあなたのことをどう思っている？ 恋の行方を、プロの占い師に電話で直接みてもらえます。</p>', prbox)

    qs_html = ''
    for i, (ax, qt, a, b) in enumerate(QS):
        qs_html += (f'<div class="q"><p class="qt"><span>Q{i+1}</span>{qt}</p><div class="opts">'
                    f'<input type="radio" name="q{i}" id="q{i}a" value="a"><label for="q{i}a">{a}</label>'
                    f'<input type="radio" name="q{i}" id="q{i}b" value="b"><label for="q{i}b">{b}</label>'
                    f'</div></div>\n')
    axes_table = ''.join(f'<tr><td>{n}</td><td>{l}（{a}）</td><td>{r}（{b}）</td></tr>' for a, b, n, l, r in AXES)
    type_rows = ''.join(f'<tr><td>{n}</td><td style="text-align:left">{d.split("。")[0]}。</td></tr>' for c, (n, d) in T.items())
    faq_html = ''.join(f'<h3>Q{i}. {q}</h3><p>{a}</p>\n' for i, (q, a) in enumerate(FAQ, 1))

    body = f"""<body>
{header}
<div class="breadcrumb"><div class="wrap"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ {H_TITLE}</div></div>
<main class="wrap">
<div class="tool-hero" style="background-image:url('../../images/lp/hero-bouquet.jpg')"><div class="tool-hero-inner">
<svg class="hero-mark" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><circle cx="32" cy="32" r="31" fill="#f7f5f2"/><image href="../../images/emblems/rings.png" x="9" y="9" width="46" height="46"/></svg>
<h1>{H_TITLE}</h1>
<p>12問・約1分。恋の主導・距離感・恋の温度・愛情表現の4つの軸から、あなたの恋愛タイプを16種類で診断します。</p>
</div></div>

<article>
<p class="pr-top">【PR】このページには広告（アフィリエイトリンク）が含まれます。</p>
<blockquote>直感で答えてください。<strong>あなたの恋愛タイプ</strong>、<strong>恋の強み</strong>、<strong>気をつけたいこと</strong>、<strong>相性のいいタイプ</strong>がわかります。</blockquote>
<div class="calc">
<p class="progress" id="prog">0 / 12 問</p>
{qs_html}
<div class="fld"><span class="person-ttl">あなたの生年月日</span>
    <div class="date-row">
      {ay}
      {am}
      {ad}
    </div></div>
  <button class="calc-btn" id="run" type="button">診断する</button>
  <p class="err" id="err">すべての質問に答えて、生年月日を選んでください。</p>
</div>

<div class="result" id="res" aria-live="polite">
<div class="result-head">
<div class="lbl">あなたの恋愛タイプ</div>
<div class="num" id="rName">—</div>
<div class="sub" id="rCode"></div>
<div id="rAxes" style="max-width:340px;margin:12px auto 0"></div>
<div class="wm">noe-match.com/tools/{SLUG}/</div>
</div>
<div class="result-body">
<div class="r-block"><h3>あなたの恋のかたち</h3><p id="rDesc"></p></div>
<div class="r-block"><h3>恋の強み</h3><p id="rStr"></p></div>
<div class="r-block"><h3>気をつけたいこと</h3><p id="rCau"></p></div>
<div class="r-block match"><h3>相性のいいタイプ</h3><p id="rMatch"></p></div>

<div class="share-block">
<div class="share-title">結果をシェアする</div>
<div class="share-btns">
<a class="share-btn x" id="shareX" href="#" target="_blank" rel="noopener">X でポスト</a>
<button class="share-btn copy" id="shareCopy" type="button">リンクをコピー</button>
</div></div>
{prbox}
<div class="next-links"><h3>あわせて読む・試す</h3><ul><li><a href="/tools/mbti-aisho-uranai/">16タイプ（MBTI）×星座でみる恋愛相性占い</a></li><li><a href="/tools/aisho-uranai/">生年月日でみる二人の相性占い</a></li><li><a href="/tools/seiza-renai-uranai/">星座でみる恋愛傾向占い</a></li><li><a href="/tools/konkatsu-type-shindan/">婚活タイプ診断（自分に合う婚活の進め方を選ぶ）</a></li></ul></div>
</div>
</div>

<h2>4つの軸</h2>
<p>この診断は、恋愛での振る舞いを4つの軸で見ています。それぞれどちらに近いかの組み合わせで、16タイプに分かれます。</p>
<div class="table-wrap"><table>
<thead><tr><th>軸</th><th>一方</th><th>もう一方</th></tr></thead>
<tbody>{axes_table}</tbody>
</table></div>

<h2>16の恋愛タイプ</h2>
<div class="table-wrap"><table class="type-table">
<thead><tr><th>タイプ</th><th>特徴</th></tr></thead>
<tbody>{type_rows}</tbody>
</table></div>
<p>好きな人との相性を見たい方は<a href="/tools/mbti-aisho-uranai/">16タイプ（MBTI）×星座でみる恋愛相性占い</a>や<a href="/tools/aisho-uranai/">生年月日でみる二人の相性占い</a>もどうぞ。</p>
</article>

<article><h2>よくある質問</h2>
{faq_html}</article>

<div class="related"><h2>関連する占い・診断・記事</h2><ul><li><a href="/tools/mbti-aisho-uranai/">16タイプ（MBTI）×星座でみる恋愛相性占い｜二人の相性度と距離が縮まるヒント</a></li><li><a href="/tools/aisho-uranai/">生年月日でみる二人の相性占い｜関係の傾向とすれ違いやすい点、話し方のヒント</a></li><li><a href="/tools/seiza-renai-uranai/">星座でみる恋愛傾向占い｜12星座の恋愛傾向と婚活のヒント</a></li><li><a href="/articles/denwa-uranai-konkatsu/">婚活・恋愛の迷いを電話占いで話す前に</a></li></ul></div>
</main>
{footer}
<button id="top" onclick="scrollTo({{top:0,behavior:'smooth'}})">↑</button>
"""
    data = {
        'AX': [[a, b, n, l, r] for a, b, n, l, r in AXES],
        'QA': [q[0] for q in QS],
        'T': {c: {'name': n, 'desc': d} for c, (n, d) in T.items()},
        'STR': STRENGTH, 'CAU': CAUTION,
        'BEST': {c: best_match(c) for c in T},
    }
    js = """<script>
(function(){
"use strict";
var SLUG='__SLUG__',TITLE='__TITLE__',PAGE_URL='__URL__';
var D=__DATA__;
var NQ=D.QA.length;
function track(n,p){try{if(typeof gtag==='function')gtag('event',n,p);}catch(e){}}
function $(id){return document.getElementById(id);}
(function(){var max=new Date().getFullYear()-18;var s=$('ay');if(!s)return;var h='<option value="">年</option>';for(var y=max;y>=1940;y--)h+='<option value="'+y+'">'+y+'年</option>';s.innerHTML=h;})();
function readDate(){var y=+$('ay').value,m=+$('am').value,d=+$('ad').value;if(!y||!m||!d)return null;var t=new Date(y,m-1,d);if(t.getFullYear()!==y||t.getMonth()!==m-1||t.getDate()!==d)return null;return {y:y,m:m,d:d};}
function answers(){var r=[];for(var i=0;i<NQ;i++){var c=document.querySelector('input[name="q'+i+'"]:checked');r.push(c?c.value:null);}return r;}
var started=false;
document.querySelector('.calc').addEventListener('change',function(){
  if(!started){started=true;track('uranai_start',{tool:SLUG});}
  var n=answers().filter(function(x){return x;}).length;$('prog').textContent=n+' / '+NQ+' 問';
});
var lastResult='';
function setShare(name){lastResult=name;var text=TITLE+'の結果は「'+name+'」でした｜Noe結婚設計室（無料）';$('shareX').href='https://x.com/intent/post?text='+encodeURIComponent(text)+'&url='+encodeURIComponent(PAGE_URL);}
$('shareX').addEventListener('click',function(){track('uranai_share',{tool:SLUG,result:lastResult});});
$('shareCopy').addEventListener('click',function(){var b=$('shareCopy');try{navigator.clipboard.writeText(PAGE_URL).then(function(){b.textContent='コピーしました';setTimeout(function(){b.textContent='リンクをコピー';},1800);});}catch(e){}track('uranai_share',{tool:SLUG,result:lastResult});});
$('prLink').addEventListener('click',function(){track('uranai_pr_click',{tool:SLUG,result:lastResult});});
// 年齢はこのブラウザ内で計算するだけ（送信・保存しない）。18歳未満なら広告枠を出さない
function isMinor(dt){var n=new Date(),age=n.getFullYear()-dt.y;if(n.getMonth()+1<dt.m||(n.getMonth()+1===dt.m&&n.getDate()<dt.d))age--;return age<18;}
onscroll=function(){$('top').classList.toggle('show',scrollY>300);};
$('run').addEventListener('click',function(){
  var ans=answers(),dt=readDate();
  if(ans.indexOf(null)>=0||!dt){$('err').style.display='block';return;}
  var cnt=[0,0,0,0];
  for(var i=0;i<NQ;i++){if(ans[i]==='a')cnt[D.QA[i]]++;}
  var code='',axes='';
  for(var k=0;k<4;k++){
    var left=cnt[k]>=2,ax=D.AX[k];code+=left?ax[0]:ax[1];
    axes+='<div class="axis-row"><span class="ax">'+ax[2]+'</span><span class="pole'+(left?' on':'')+'">'+ax[3]+'</span><span class="pole'+(left?'':' on')+'">'+ax[4]+'</span></div>';
  }
  var t=D.T[code],m=D.T[D.BEST[code]];
  $('rName').textContent=t.name;
  $('rCode').textContent='タイプコード：'+code;
  $('rAxes').innerHTML=axes;
  $('rDesc').textContent=t.desc;
  $('rStr').textContent=D.STR[code[0]]+'そして、'+D.STR[code[3]];
  $('rCau').textContent=D.CAU[code[1]]+D.CAU[code[2]];
  $('rMatch').innerHTML='<strong>'+m.name+'</strong>（'+D.BEST[code]+'）<br>'+m.desc+'求める関係の形が近く、役割は自然に補い合える組み合わせです。';
  setShare(t.name);
  var box=document.querySelector('.prbox');if(box){var mn=isMinor(dt);box.hidden=mn;box.style.display=mn?'none':'';}
  $('err').style.display='none';$('res').classList.add('show');$('res').scrollIntoView({behavior:'smooth',block:'start'});
  track('uranai_complete',{tool:SLUG,result:t.name});
});
})();
</script>
</body>
</html>
"""
    js = (js.replace('__SLUG__', SLUG).replace('__TITLE__', TITLE).replace('__URL__', URL)
            .replace('__DATA__', json.dumps(data, ensure_ascii=False)))
    out = head_top + '<style>' + css + '</style>\n' + ld_html + '</head>\n' + body + js
    os.makedirs(os.path.join(ROOT, 'tools', SLUG), exist_ok=True)
    with open(os.path.join(ROOT, 'tools', SLUG, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(out)
    print('wrote', SLUG)


if __name__ == '__main__':
    main()
