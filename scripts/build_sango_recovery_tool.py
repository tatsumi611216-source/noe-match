# -*- coding: utf-8 -*-
"""産後リカバリー診断（抜け毛・肌・体型・再開時期）を fugenbyo-check をベースに生成する。

語の根拠（2026-08-23 サジェスト実測）:
  産後 いつ戻る=10（お腹・体重・体型・ホルモンバランス）／産後 老ける=10（対策・戻る・なぜ）／
  産後 美容 いつから=10／産後 リカバリー=10（グッズ系が多い）
  ★ 産後 美容 診断=0、産後 抜け毛 チェック=0 → 「診断」を主題語にせず「いつ戻る」「老ける」で組む
  SERP実測（8/22）: 産後の抜け毛・肌・体型・再開時期の上位はクリニックのコラムと汎用AI肌診断のみ。
  産後に特化した横断の診断形式は存在しない（空白）。

設計（CEO指示 2026-08-23）:
  気になる項目をチェックリストで聞く → 項目ごとに「対策・時期の目安・確認先」を出す →
  対策ごとに案件を結果連動で出す。周辺記事は「妊娠後の美容観点からのリカバリー」。
  簡易15問／完全版の2モード（ベースの仕組みを流用）。

安全装置（diagnostic-factory）:
  - 受診フラグ data-med: 出血・強い痛み・発熱・2週間以上続く落ち込み → 判定1段昇格＋受診案内
  - DVフラグ data-dv: 夫の威圧・行動制限 → 最上位＋#8008
  - 効果・安全性の断定なし。薬機法56項目の範囲外の表現を使わない（「治る」「消える」「発毛」を書かない）
  - 公的・公式に確認できる時期の目安だけを示し、出典を併記
  - 案件は「対策の選択肢」としてACTION段のみ。未提携の対策はリンク無しの「確認先」表示に留める
"""
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "fugenbyo-check", "index.html")
OUT = os.path.join(ROOT, "tools", "sango-recovery-check")
SLUG = "sango-recovery-check"
URL = "https://www.noe-match.com/tools/%s/" % SLUG
TITLE = "産後、いつ戻る？老けた？｜抜け毛・肌・体型・美容再開を気になる項目から整理する産後リカバリー診断【無料・簡易15問】"
DESC = ("産後の抜け毛・肌荒れ・体型・白髪、いつ戻るのか。授乳中の美容はいつから再開できるのか。"
        "気になる項目をチェックすると、公的・公式に確認できる時期の目安と、確認先（製造販売元・産後健診・皮膚科）、"
        "家族との調整のしかたを項目ごとに整理して表示します。判定はせず、段取りだけを出します。無料・登録不要。簡易15問／完全版33問。")

FAQ = [
 ("産後の抜け毛はいつ戻りますか？",
  "医療機関の公開情報では、産後2〜3か月ごろから増え、半年〜1年で落ち着くことが多いとされています（分娩後脱毛症）。ただし個人差が大きく、公的な統計として「何か月で戻る」を示したものはありません。1年を超えて続く場合や地肌が目立つ場合は皮膚科に相談してください。"),
 ("産後の体型はいつ戻りますか？",
  "「いつ戻る」を示す公的データは確認できていません。産後の体の回復は出産方法（経腟・帝王切開）や授乳の有無で違うため、この診断では時期を断定せず、産後健診で経過を確認してから運動や骨盤ケアの開始時期を医療者に相談する手順を示しています。"),
 ("授乳中に使えない化粧品成分のリストはありますか？",
  "国立成育医療研究センター「妊娠と薬情報センター」が公表しているのは薬の一覧で、化粧品成分の一覧は公表されていません（2026年8月確認）。この診断では、手元の製品の注意書き→製造販売元への問い合わせ→医療者への相談、の順で確認する手順を示します。"),
 ("産後の美容（まつげパーマ・ネイル・脱毛）はいつから再開できますか？",
  "統一された公的基準はなく、各店舗が受付基準を決めています。ヘアカラーは助産師監修の育児メディアが産後1か月以降を示す一方、脱毛は断乳後を条件にする店舗があるなど施術ごとに違います。詳しくは当サイトの「産後の美容はいつから再開できるのか」で施術別に整理しています。"),
 ("この診断は医学的なものですか？",
  "いいえ。医学的診断ではなく、気になる項目を整理して確認先と段取りを示すものです。出血・強い痛み・発熱・気分の落ち込みが続く場合は、診断の結果にかかわらず医療機関に相談してください。"),
 ("「老けた」と感じるのは普通ですか？",
  "産後はホルモンの変動・睡眠不足・栄養の偏りが重なり、肌や髪の状態が一時的に変わることが医療機関の公開情報で説明されています。多くは一時的とされますが、どの程度で戻るかを示す統計はありません。自分の状態と、家族にどう受け取られているかを分けて整理することを、この診断では勧めています。"),
 ("家族に「気にしすぎ」と言われます。",
  "産後の見た目の変化は、変化そのものより「扱われ方」が重くのしかかることがあります。この診断では、美容の問題として処理しようとしていたものが、実は分担や関わり方の問題だった場合に、ガルガル期セルフチェックや産後クライシスの記事へ案内します。"),
]

SECTIONS_JS = r"""
const SECTIONS = [
  { roman: "Ⅰ", title: "髪", note: "抜け毛・白髪・髪質。気になるものに「はい」を", items: [
    { t: "抜け毛が産前より明らかに増えた（排水口・枕で気づく）", w: 3, s: true, c: "hair" },
    { t: "産後1年を過ぎても抜け毛が落ち着かない", w: 4, med: true, c: "hair" },
    { t: "生え際や分け目の地肌が目立つようになった", w: 3, c: "hair" },
    { t: "白髪が急に増えた", w: 2, c: "hair" },
    { t: "髪がパサつく・うねる・以前と質が変わった", w: 2, c: "hair" },
    { t: "ヘアカラーや縮毛矯正を再開したいが、授乳中で迷っている", w: 2, s: true, c: "hair" },
  ]},
  { roman: "Ⅱ", title: "肌", note: "肌荒れ・シミ・乾燥。授乳中の成分も", items: [
    { t: "肌荒れ・ニキビ・乾燥が産前より増えた", w: 3, s: true, c: "skin" },
    { t: "シミ・くすみが増えた、または濃くなった気がする", w: 2, c: "skin" },
    { t: "使っていた化粧品を「授乳中に使っていいか」分からず止めている", w: 3, s: true, c: "skin" },
    { t: "かゆみ・赤み・湿疹が続いている", w: 3, med: true, c: "skin" },
    { t: "スキンケアに使える時間が1日5分もない", w: 2, c: "skin" },
  ]},
  { roman: "Ⅲ", title: "体型", note: "体重・お腹・骨盤。回復のペースは人それぞれ", items: [
    { t: "体重が産前に戻らない", w: 2, c: "body" },
    { t: "お腹まわりが戻らない・ぽっこりが気になる", w: 3, s: true, c: "body" },
    { t: "骨盤まわり・腰に違和感や痛みがある", w: 3, med: true, c: "body" },
    { t: "運動や骨盤ケアをいつから始めていいか分からない", w: 2, s: true, c: "body" },
    { t: "授乳中で食事制限をしていいか迷っている", w: 2, c: "body" },
  ]},
  { roman: "Ⅳ", title: "再開したい美容", note: "施術別に受付条件が違います", items: [
    { t: "脱毛（サロン・医療）を再開したい、または契約が残っている", w: 2, s: true, c: "salon" },
    { t: "まつげパーマ・ネイル・エステに行きたいが、いつからか分からない", w: 2, s: true, c: "salon" },
    { t: "美容院に行きたいが、時間と預け先が確保できない", w: 2, c: "salon" },
    { t: "産前に契約したコースの有効期限が気になる", w: 2, c: "salon" },
  ]},
  { roman: "Ⅴ", title: "いまの条件", note: "回復のペースに効く条件です", items: [
    { t: "産後3か月以内である", w: 1, s: true, c: "cond" },
    { t: "授乳中である", w: 1, s: true, c: "cond" },
    { t: "産後健診（1か月健診）で経過を確認していない、または結果が気になる", w: 3, med: true, c: "cond" },
    { t: "出血・強い痛み・発熱のいずれかがいまもある", w: 5, s: true, med: true, c: "cond" },
    { t: "睡眠がまとまって取れない日が週の半分以上", w: 2, c: "cond" },
  ]},
  { roman: "Ⅵ", title: "家族との関係", note: "見た目の悩みが、扱われ方の問題に転じていないか", items: [
    { t: "見た目の変化を家族に話したら「気にしすぎ」「それどころじゃない」と返された", w: 3, s: true, c: "family" },
    { t: "自分のために数時間使うことに罪悪感がある、または責められる", w: 3, s: true, c: "family" },
    { t: "気分の落ち込みが2週間以上続いている", w: 4, s: true, med: true, c: "family" },
    { t: "夫（パートナー）に威圧される・外出や交友を制限される", w: 5, dv: true, c: "family" },
  ]},
  { roman: "Ⅶ", title: "回復の手がかり", note: "最後に、すでにある資源を", items: [
    { t: "産後健診で「問題なし」と確認できている", w: -3, s: true, c: "res" },
    { t: "子どもを預けられる人・場所が週に1回以上ある", w: -3, c: "res" },
    { t: "家族と、見た目や体調の話を落ち着いてできる", w: -3, c: "res" },
    { t: "皮膚科・産婦人科など相談できる医療機関が決まっている", w: -2, c: "res" },
  ]},
];
"""

TIERS_JS = r"""
const TIERS = [
  {
    emoji: "🌱", img: null, label: "リカバリーの負荷：軽", name: "芽吹きの時期",
    color: "var(--safe)", bg: "var(--safe-bg)",
    catch: "気になる項目は少なく、回復の手がかりが機能している状態です。",
    stars: 1, damageLevel: "整っている",
    damage: "産後の変化は出ていても、確認先と段取りが見えている状態です。焦って手を広げるより、気になる項目を一つずつ確認していけば十分です。",
    tips: [
      "気になる項目が出てきたら、下の「項目ごとの段取り」の確認先から当たる",
      "自分のための時間を週に数時間、先に予定へ入れておく（後から確保するのは難しい）",
      "産後健診の結果を家族と共有しておくと、再開の相談が通りやすい",
    ],
    note: "負荷が軽くても、授乳中の製品の可否や施術の受付条件は個別に違います。確認先で一度ずつ確かめてください。",
  },
  {
    emoji: "🌿", img: null, label: "リカバリーの負荷：中", name: "整え始めの時期",
    color: "var(--mid)", bg: "var(--mid-bg)",
    catch: "気になる項目がいくつか重なっています。順番を決めれば動けます。",
    stars: 2, damageLevel: "順番待ち",
    damage: "髪・肌・体型のどれかが気になり、再開したいことも出てきている状態。全部を同時に動かそうとすると、確認だけで消耗します。",
    tips: [
      "気になる項目のうち、締切があるもの（契約の有効期限・健診）を先に処理する",
      "製品や施術は「成分から探す」より「手元の製品・行きたい店に直接聞く」方が一回で終わる",
      "家族には「何をしたいか」より先に「何時間必要か」を伝えると、段取りの話になる",
    ],
    note: "この段階は、情報を増やすより確認先を一つ決める方が早く進みます。",
  },
  {
    emoji: "🍂", img: null, label: "リカバリーの負荷：高", name: "立て直しの時期",
    color: "var(--high)", bg: "var(--high-bg)",
    catch: "体の確認が先です。美容の段取りは、健診と医療者への相談のあとに置いてください。",
    stars: 4, damageLevel: "体の確認が先",
    damage: "身体の症状か、産後健診の未確認、または気分の落ち込みが含まれています。見た目の回復より先に、体と心の経過を確認する段階です。",
    tips: [
      "産後健診が未受診なら最優先で受ける。受診済みで症状が続くなら産婦人科・皮膚科へ",
      "気分の落ち込みが2週間以上続いている場合は、美容の前に医療者へ相談する",
      "美容の再開は、医療者に「これをしたい」と製品・施術名を示して確認してから",
      "家族に「気にしすぎ」と言われて話せなくなっているなら、下のガルガル期チェックで整理する",
    ],
    note: "「戻らない」のは本人の怠りではありません。回復のペースには個人差があり、公的統計でも時期は示されていません。",
  },
  {
    emoji: "⚠️", img: null, label: "リカバリーの負荷：要相談", name: "ひとりで抱えない時期",
    color: "var(--crit)", bg: "var(--crit-bg)",
    catch: "この診断の範囲を超えています。医療者または相談窓口につながることを優先してください。",
    stars: 5, damageLevel: "要相談",
    damage: "身体の症状と、家族との関係のどちらか、または両方で、この診断が扱える範囲を超えた項目に「はい」が付いています。",
    tips: [
      "出血・強い痛み・発熱があれば、日を置かず産婦人科へ",
      "威圧・行動の制限がある場合は、下の相談窓口へ。美容の話は後回しで構いません",
      "信頼できる人に、いまの状態をそのまま伝える。整理して話す必要はありません",
    ],
    note: "産後の見た目の悩みから始まっても、ここに来た場合の本題は見た目ではありません。",
  },
];
"""

# 項目別の段取り（対策・時期の目安・確認先・案件差し込み口）
PLAN_JS = r"""
// 項目ごとの段取り。pr.u が空なら案件リンクは表示しない（未提携の差し込み口）
const PLAN = {
  hair: { title: "髪（抜け毛・白髪・髪質）",
    when: "医療機関の公開情報では、産後2〜3か月ごろから抜け毛が増え、半年〜1年で落ち着くことが多いとされています（分娩後脱毛症）。公的統計として「何か月で戻る」を示したものはありません。",
    steps: ["1年を超えて続く・地肌が目立つ場合は皮膚科へ（女性の脱毛を扱う医療機関もある）",
            "ヘアカラーは助産師監修の育児メディアが産後1か月以降を目安として示している。縮毛矯正・カラーは美容院に授乳中である旨を伝えて確認",
            "育毛剤・シャンプーは製造販売元の注意書きで「妊娠中・授乳中」の記載を確認。記載が無いことは安全の表明ではない"],
    links: [["/articles/sango-biyou-itsukara/", "産後の美容はいつから再開できるのか（施術別）"]],
    pr: { u: "", h: "", b: "", btn: "" } },
  skin: { title: "肌（肌荒れ・シミ・授乳中の成分）",
    when: "授乳中に使えない化粧品成分の公的な一覧は存在しません（国立成育医療研究センターが公表しているのは薬の一覧。2026年8月確認）。",
    steps: ["手元の製品の箱・公式サイトで「妊娠中・授乳中」の記載を見る",
            "記載が無ければ製造販売元に製品名を挙げて問い合わせる（成分一般ではなく製品を特定する）",
            "判断がつかなければ産後健診・乳児健診の機会に「これを使いたい」と製品を示して相談。症状が出ていれば皮膚科へ"],
    links: [["/articles/junyuchu-biyou/", "「授乳中に使えない化粧品成分」は誰が決めているのか"]],
    pr: { u: "", h: "", b: "", btn: "" } },
  body: { title: "体型（体重・お腹・骨盤）",
    when: "「いつ戻る」を示す公的データは確認できていません。出産方法と授乳の有無で回復のペースが違います。",
    steps: ["運動・骨盤ケアの開始時期は産後健診で経過を確認してから医療者に相談（多くの整骨院・整体も産後1〜2か月以降を受付基準にしている）",
            "授乳中の食事制限は自己判断せず、健診や助産師に相談。食事の手間を減らすことは安全側の対策になる",
            "骨盤矯正の料金は整骨院3,000〜6,000円／回、整体院5,000〜10,000円／回が公開相場（2026年8月・施設により差）。保険適用の可否は施設で確認"],
    links: [["/articles/garugaru-ki-guide/", "ガルガル期とは｜産後に起きることの基礎知識"]],
    pr: { u: "https://px.a8.net/svt/ejp?a8mat=4B8B4Q+5CWKMY+3RK+2TBJQA", h: "食事の手間をそもそも減らす", b: "授乳中の食事制限は自己判断しない方が安全です。代わりに「作る負担」を減らすと、睡眠と自分の時間が戻りやすくなります。Oisixは食材宅配のおためしセット（内容・価格は公式サイトでご確認ください）。", btn: "Oisixのおためしセットを見る", offer: "oisix" } },
  salon: { title: "再開したい美容（脱毛・まつげ・ネイル・美容院）",
    when: "再開時期に統一された公的基準はなく、店舗ごとに受付条件が違います。脱毛は断乳後を条件にする店舗がある一方、ネイルは授乳の有無をほぼ問いません。",
    steps: ["予約前に店舗へ4点を聞く：産後・授乳中の受付条件／産後健診の完了が必要か／所要時間と中断の可否／契約中コースの有効期限の扱い",
            "契約が残っている場合は「受けられる時期」より先に「期限が止まるか」を確認。申請しないと期限だけ進むことがある",
            "再開の時期は月数より「その場を離れられる時間」で決まる。授乳間隔と預け先を先に確保する"],
    links: [["/articles/sango-biyou-itsukara/", "施術別の目安と、その目安を誰が言っているのか"]],
    pr: { u: "", h: "", b: "", btn: "" } },
  cond: { title: "いまの条件（時期・授乳・健診・睡眠）",
    when: "産後健診の完了は、本人にとっても店舗にとっても最も分かりやすい区切りです。",
    steps: ["健診が未受診なら最優先で受ける。出血・強い痛み・発熱があれば日を置かず産婦人科へ",
            "睡眠がまとまらない時期は、美容より先に「眠れる時間帯を作る分担」を家族と決める"],
    links: [["/articles/sango-kaji-buntan/", "産後の家事分担｜実際に揉めるのはどこか"]],
    pr: { u: "", h: "", b: "", btn: "" } },
  family: { title: "家族との関係",
    when: "見た目の変化は、変化そのものより「扱われ方」が重くのしかかることがあります。",
    steps: ["「気にしすぎ」と返されて話せなくなっているなら、美容の話ではなく関わり方の問題として整理する",
            "自分のための数時間は、分担の問題。「何をしたいか」より「何時間必要か」を先に伝える",
            "気分の落ち込みが2週間以上続く場合は、美容の前に医療者へ"],
    links: [["/tools/garugaru-check/", "ガルガル期セルフチェック（無料）"], ["/articles/sango-crisis-guide/", "産後クライシスの全体像"]],
    pr: { u: "", h: "", b: "", btn: "" } },
};
function renderPlan(concerns) {
  const box = document.getElementById("rPlan");
  const keys = ["cond", "hair", "skin", "body", "salon", "family"].filter(k => concerns[k]);
  if (!keys.length) { box.innerHTML = '<p style="font-size:.9rem;color:var(--ink-soft)">「はい」の項目がありません。気になることが出てきたら、もう一度チェックしてください。</p>'; return; }
  box.innerHTML = keys.map(k => {
    const p = PLAN[k];
    const pr = (p.pr && p.pr.u) ? `<div style="margin-top:12px;padding:12px 14px;background:#fff;border:1px solid var(--border);border-radius:6px"><p style="font-size:.68rem;color:#999;margin:0 0 4px">PR</p><p style="font-weight:700;font-size:.86rem;margin:0 0 4px">${p.pr.h}</p><p style="font-size:.78rem;color:var(--ink-soft);margin:0 0 10px">${p.pr.b}</p><a href="${p.pr.u}" rel="nofollow sponsored noopener" target="_blank" data-offer="${p.pr.offer || ''}" style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;font-size:.82rem;padding:10px 22px;border-radius:2px;text-decoration:none">${p.pr.btn}</a></div>` : "";
    return `<div class="r-block" style="border:1px solid var(--border);border-radius:6px;padding:16px 18px;margin:12px 0;background:var(--bg)">
      <h3 style="margin:0 0 6px">${p.title}</h3>
      <p style="font-size:.84rem;color:var(--ink-soft);margin:0 0 8px">${p.when}</p>
      <ol style="margin:0 0 8px 1.2em;padding:0;font-size:.86rem;line-height:1.8">${p.steps.map(s => `<li>${s}</li>`).join("")}</ol>
      <p style="font-size:.82rem;margin:0">${p.links.map(l => `<a href="${l[0]}">${l[1]}</a>`).join(" ／ ")}</p>${pr}</div>`;
  }).join("");
  document.querySelectorAll('#rPlan a[data-offer]').forEach(a => a.addEventListener('click', () => track('sango_recovery_pr_click', { offer: a.dataset.offer })));
}
"""


def main():
    h = io.open(SRC, encoding="utf-8").read()

    # --- head ---
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % TITLE, h, count=1, flags=re.S)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', r"\g<1>%s\2" % DESC, h, count=1)
    h = h.replace("https://www.noe-match.com/tools/fugenbyo-check/", URL)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")', r"\g<1>%s\2" % TITLE, h, count=1)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")', r"\g<1>%s\2" % DESC, h, count=1)
    h = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', r"\g<1>%s\2" % TITLE, h, count=1)
    h = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', r"\g<1>%s\2" % DESC, h, count=1)
    h = re.sub(r'<meta property="og:image" content="[^"]*">', '<meta property="og:image" content="https://www.noe-match.com/images/garugaru-og.png">', h)
    h = re.sub(r'<meta name="twitter:image" content="[^"]*">', '<meta name="twitter:image" content="https://www.noe-match.com/images/garugaru-og.png">', h)
    # JSON-LD 全置換
    ld = [
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        {"@context": "https://schema.org", "@type": "WebApplication", "name": "産後リカバリー診断", "url": URL, "applicationCategory": "LifestyleApplication", "operatingSystem": "All", "inLanguage": "ja", "description": DESC, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}, "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": "https://www.noe-match.com/"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"}, {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": "https://www.noe-match.com/#tools"}, {"@type": "ListItem", "position": 3, "name": "産後リカバリー診断"}]},
    ]
    lds = "".join('<script type="application/ld+json">%s</script>\n' % json.dumps(d, ensure_ascii=False) for d in ld)
    h = re.sub(r'(<script type="application/ld\+json">.*?</script>\s*)+', lds, h, count=1, flags=re.S)

    # --- hero ---
    h = h.replace("../../images/lp/room-light.jpg", "../../images/lp/hands-touch.jpg")
    h = re.sub(r"<h1>夫源病危険度チェック診断</h1>\s*<p>.*?</p>",
               "<h1>産後、いつ戻る？老けた？｜産後リカバリー診断</h1>\n<p>抜け毛・肌・体型・再開したい美容。気になる項目をチェックすると、公的・公式に確認できる時期の目安と確認先、家族との段取りを項目ごとに整理します。判定はせず、段取りだけを出します。無料・登録不要。</p>", h, count=1, flags=re.S)

    # --- 診断についての導入（h2〜modeSwitch直前） ---
    a = h.find("<h2>この診断について</h2>"); b = h.find('<div class="mode-switch" id="modeSwitch">')
    assert a > 0 and b > a, (a, b)
    intro = """<h2>この診断について</h2>
<p>「産後 いつ戻る」「産後 老ける」で検索すると、クリニックのコラムか大手の肌診断が出てきます。どちらも<strong>産後という条件（授乳中・健診前・預け先がない）を前提にしていません</strong>。この診断は、気になる項目をチェックリストで聞き、<strong>項目ごとに「公的・公式に確認できる時期の目安」「確認先の順番」「家族との段取り」</strong>を出します。</p>
<p>安全性や効果は判定しません。授乳中に使える成分の公的な一覧は存在せず（国立成育医療研究センターが公表しているのは薬の一覧）、美容の再開時期にも統一基準がないためです。示せるのは「何がどこまで公表されていて、どこに聞けば自分の答えが出るか」までです。</p>
<div class="q-note" style="margin:14px 0 22px">身体の症状（出血・強い痛み・発熱・長く続く落ち込み）に「はい」が付いた場合は、点数に関わらず受診の案内を優先して表示します。</div>
"""
    h = h[:a] + intro + h[b:]
    # モード名
    h = h.replace("サクッと15問<span>約2分・要点だけ測る</span>", "簡易版15問<span>約2分・気になる項目だけ</span>")
    h = h.replace('ちゃんと測る45問<span>約4分・フル計測</span>', '完全版33問<span>約5分・条件と家族関係まで</span>')

    # --- 結果カード ---
    h = h.replace("<strong>受診をおすすめします</strong>：動悸・めまい・不眠・「異常なし」と言われた不調——症状がすでに体に出ています。この診断の点数に関わらず、心療内科または婦人科への相談を優先してください。",
                  "<strong>受診をおすすめします</strong>：出血・強い痛み・発熱・続く皮膚症状・2週間以上の落ち込み・健診の未確認のいずれかに「はい」が付いています。この診断の点数に関わらず、産婦人科（または皮膚科・心療内科）への相談を優先してください。")
    h = re.sub(r"(<div[^>]*id=\"rMedFlag\"[^>]*>.*?</strong>：[^<]*)(「夫の在宅[^<]*)", r"\1", h, flags=re.S)
    h = h.replace("威圧・経済的な支配・行動の制限は、夫源病ではなく<strong>モラルハラスメント・DVのサイン</strong>です。", "威圧・行動や交友の制限は、産後の見た目の悩みではなく<strong>モラルハラスメント・DVのサイン</strong>です。")
    h = h.replace("<h3>あなたへのダメージ想定</h3>", "<h3>いまの見立て</h3>")
    h = h.replace("<h3>処方箋（いま打てる手）</h3>", "<h3>いま打てる手</h3>")
    # 夫に渡す処方箋 → 家族に渡す一言
    h = re.sub(r"<h3>夫に渡す処方箋（コピーして使えます）</h3>.*?</div>\s*</div>",
               """<h3>家族に渡す一言（コピーして使えます）</h3>
<p style="font-size:.85rem;color:var(--ink-soft)">「気にしすぎ」で終わらせないための伝え方。何をしたいかより、何時間必要かを先に：</p>
<div style="background:var(--bg);border:1px dashed var(--line-strong);border-radius:6px;padding:14px 16px;font-size:.85rem;line-height:1.9">産後の体のことで確認したいことがあって、<strong>【例：来週の土曜の午前に2時間／皮膚科に行く1時間半】</strong>だけ時間がほしい。その間は見ていてもらえる？ 内容はあとで説明するから、まず時間だけ決めさせて。</div>
</div>""", h, count=1, flags=re.S)
    # PRブロック（2本の補給線）→ 項目ごとの段取り
    h = re.sub(r'<hr class="r-divider">\s*<div style="border:1px solid var\(--border\);border-radius:6px;padding:20px 22px;margin:26px 0;background:var\(--bg\)">\s*<p style="font-size:\.7rem;color:#999;margin:0 0 4px">PR</p>.*?各サービスの内容・価格は時期により変わります。公式サイトでご確認ください。</p>\s*</div>',
               '<hr class="r-divider">\n<div class="r-block"><h3>項目ごとの段取り（「はい」を付けた項目）</h3><p style="font-size:.84rem;color:var(--ink-soft);margin:0 0 10px">時期の目安は公的・公式に確認できるものだけ。対策の選択肢に広告（PR）を含む場合は、その旨を表示しています。</p><div id="rPlan"></div></div>',
               h, count=1, flags=re.S)
    # 結果内の解説r-block（夫源病とは〜対処の基本方針）を削除
    h = re.sub(r'<div class="r-block">\s*<h3>夫源病とは</h3>.*?(?=<p class="r-disclaimer">)', "", h, count=1, flags=re.S)
    h = h.replace("※本診断は医学的診断・心理検査ではありません。夫源病は俗称であり、症状の原因は自己判断せず医療機関でご確認ください。",
                  "※本診断は医学的診断ではありません。時期の目安は公的機関・医療機関・各社の公開情報に基づくもので、効果や安全性を示すものではありません。製品の使用可否・施術の再開は、製造販売元・施術先・医療者にご確認ください。")
    h = h.replace("よりそいホットライン", "よりそいホットライン")


    # 受診ボックス（産後版）
    h = re.sub(r'<div class="medical">.*?</div>', """<div class="medical">
<strong>我慢せず受診してほしいサイン</strong>
以下がある場合は、診断結果に関わらず医療機関（産婦人科・皮膚科・心療内科）へ。
<ul>
<li>出血が続く・強い痛み・発熱がある</li>
<li>かゆみ・赤み・湿疹が広がる、または長引く</li>
<li>涙が止まらない・気分の落ち込みが2週間以上続く</li>
<li>「消えてしまいたい」と感じることがある</li>
</ul>
つらさが強いときは、よりそいホットライン 0120-279-338（24時間・無料）も利用できます。産後の落ち込みの線引きは<a href="/articles/maternity-blue-chigai/">マタニティブルーと産後うつの違い</a>にまとめています。
</div>""", h, count=1, flags=re.S)
    h = h.replace("＞ 夫源病危険度チェック診断</div>", "＞ 産後リカバリー診断</div>")
    h = h.replace("夫源病危険度チェック診断｜noe-match.com/tools/fugenbyo-check", "産後リカバリー診断｜noe-match.com/tools/%s" % SLUG)
    h = h.replace("フル45問で測り直す（回答は引き継ぎ）", "完全版33問で測り直す（回答は引き継ぎ）")
    h = h.replace("夫の行動・環境まで含めた精度で見るなら", "条件と家族関係まで含めて見るなら")
    # 基礎知識の記事節を産後版に
    h = re.sub(r'<h2>夫源病の基礎知識</h2>.*?(?=<article>|<div class="related">|<!-- LINE-CTA -->)', """<h2>産後のリカバリーで、公表されていること・いないこと</h2>
<h3>時期の目安があるもの</h3>
<p>産後の抜け毛（分娩後脱毛症）は、医療機関の公開情報で「産後2〜3か月ごろから増え、半年〜1年で落ち着くことが多い」とされています。ヘアカラーの再開は、助産師監修の育児メディアが産後1か月以降を目安に示しています。いずれも公的統計ではなく、個人差があります。</p>
<h3>公表されていないもの</h3>
<p>「体型がいつ戻るか」「授乳中に使えない化粧品成分の一覧」「施術をいつから再開できるかの統一基準」は、公的機関から公表されていません（2026年8月確認）。化粧品について国立成育医療研究センターが公表しているのは薬の一覧です。施術の受付条件は店舗ごとに違います。</p>
<h3>この診断がやること・やらないこと</h3>
<p>やるのは、気になる項目ごとに「確認できる目安」「確認先の順番」「家族との段取り」を並べることです。やらないのは、安全性・効果の判定と、時期の断定です。公表されていないことを埋めるのは、手元の製品・行きたい店・かかりつけの医療者への確認であって、一般論のリストではありません。</p>
""", h, count=1, flags=re.S)
    # --- FAQ（可視）を関連リンクの前に ---
    faq_html = "<article><h2>よくある質問</h2>" + "".join("<h3>Q%d. %s</h3><p>%s</p>" % (i + 1, q, a) for i, (q, a) in enumerate(FAQ)) + "</article>\n"
    i = h.find('<div class="related">')
    h = h[:i] + faq_html + h[i:]
    # 関連リンク
    h = re.sub(r'<div class="related">.*?</div>',
               """<div class="related">
<h2>あわせて読みたい・使いたい</h2>
<ul>
<li><a href="/articles/sango-biyou-itsukara/">産後の美容はいつから再開できるのか｜施術別の目安と、その目安を誰が言っているのか</a></li>
<li><a href="/articles/junyuchu-biyou/">「授乳中に使えない化粧品成分」は誰が決めているのか｜公的機関の公表状況</a></li>
<li><a href="/tools/garugaru-check/">ガルガル期セルフチェック｜見た目の悩みが関わり方の問題に転じていないか（無料）</a></li>
<li><a href="/articles/garugaru-ki-guide/">ガルガル期とは｜いつから始まり何が起きるのかの基礎知識</a></li>
<li><a href="/articles/sango-crisis-guide/">産後クライシスの全体像</a></li>
<li><a href="/articles/maternity-blue-chigai/">マタニティブルーと産後うつの違い｜線引きの目安</a></li>
</ul>
</div>""", h, count=1, flags=re.S)
    # LINE CTA 文面
    h = re.sub(r'(<section id="line-cta".*?)<p style="margin:0 0 14px;font-size:20px[^>]*>[^<]*</p>\s*<p style="margin:0 0 22px;font-size:14px[^>]*>.*?</p>',
               r'\1<p style="margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:\'Yu Mincho\',\'游明朝\',serif;line-height:1.5;">産後の段取りを、LINEで</p>\n  <p style="margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;">製品・施術の確認手順と、家族との時間の決め方を、週1回・短文で届けます。<br>個別の相談も、追加後そのままトークでどうぞ。</p>', h, count=1, flags=re.S)
    h = h.replace("tool:'fugenbyo-check'", "tool:'%s'" % SLUG)

    # --- JS ---
    scripts = re.findall(r"<script(?![^>]*src)[^>]*>(.*?)</script>", h, re.S)
    main_js = max(scripts, key=len)
    js = main_js
    js = re.sub(r"const SECTIONS = \[.*?\n\];\n", SECTIONS_JS.strip() + "\n", js, count=1, flags=re.S)
    js = re.sub(r"const TIERS = \[.*?\n\];\n", TIERS_JS.strip() + "\n" + PLAN_JS.strip() + "\n", js, count=1, flags=re.S)
    js = js.replace("const BANDS = { short: [4, 10, 16], full: [10, 24, 38] };", "const BANDS = { short: [6, 14, 22], full: [10, 24, 40] };")
    js = js.replace('short: { range: 22, flex: [4, 6, 6, 6], labels: ["〜4 そよ風", "5〜10 曇り", "11〜16 低気圧", "17〜 台風"] }',
                    'short: { range: 30, flex: [6, 8, 8, 8], labels: ["〜6 軽", "7〜14 中", "15〜22 高", "23〜 要相談"] }')
    js = js.replace('full:  { range: 50, flex: [10, 14, 14, 12], labels: ["〜10 そよ風", "11〜24 曇り", "25〜38 低気圧", "39〜 台風"] }',
                    'full:  { range: 54, flex: [10, 14, 16, 14], labels: ["〜10 軽", "11〜24 中", "25〜40 高", "41〜 要相談"] }')
    js = js.replace("fugenbyo_", "sango_recovery_")
    js = js.replace("https://www.noe-match.com/tools/fugenbyo-check/", URL)
    js = re.sub(r"const shareText = `.*?`;", "const shareText = `診断結果：${tier.name}${tier.emoji}（${tier.label}）｜産後リカバリー診断【無料】 #産後`;", js, count=1)
    # data-c 属性を設問に付ける
    js = js.replace("${it.s ? 'data-short=\"1\"' : \"\"}>", "${it.s ? 'data-short=\"1\"' : \"\"} data-c=\"${it.c || ''}\">")
    # 判定時に concerns を集計して renderPlan
    js = js.replace("    if (item.dataset.dv && a === 1) dvFlag = true;\n  });",
                    "    if (item.dataset.dv && a === 1) dvFlag = true;\n    if (a === 1 && Number(item.dataset.w) > 0 && item.dataset.c) concerns[item.dataset.c] = true;\n  });")
    js = js.replace("let plus = 0, minus = 0, medFlag = false, dvFlag = false, answered = 0;", "let plus = 0, minus = 0, medFlag = false, dvFlag = false, answered = 0; const concerns = {};")
    js = js.replace("  document.getElementById(\"rMedFlag\").style.display = medFlag ? \"\" : \"none\";", "  renderPlan(concerns);\n  document.getElementById(\"rMedFlag\").style.display = medFlag ? \"\" : \"none\";")
    js = js.replace("if (medFlag && ti < 2) ti = 2;   // 身体症状あり → 低気圧停滞中 以上", "if (medFlag && ti < 2) ti = 2;   // 身体症状・健診未確認 → 立て直しの時期 以上")
    # 旧PRクリック計測（a8直リンク固定）を除去
    js = re.sub(r"document\.querySelectorAll\('#result a\[href\*=\"px\.a8\.net\"\]'\)\.forEach\(a => \{.*?\}\);\n", "", js, count=1, flags=re.S)
    h = h.replace(main_js, js)

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "index.html")
    io.open(p, "w", encoding="utf-8").write(h)
    # 検証
    out = io.open(p, encoding="utf-8").read()
    for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', out, re.S):
        json.loads(s)
    bad = re.findall(r"夫源病|fugenbyo", out)
    print("built:", p, "| bytes:", len(out), "| 残存(夫源病/fugenbyo):", len(bad))
    if bad:
        for m in re.finditer(r".{0,40}(?:夫源病|fugenbyo).{0,40}", out): print("  ", m.group(0).replace("\n", " "))


if __name__ == "__main__":
    main()
