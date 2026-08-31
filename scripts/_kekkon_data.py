# -*- coding: utf-8 -*-
"""結婚新生活支援（令和8年度の名称は「結婚・妊娠・共育ての相談機会提供・支援プログラム」）の一次データ。
一都三県の実施自治体・全数。正本。

取得日: 2026年8月31日。各自治体の公式ページからの原文抜粋は agent/research_kekkon/raw_digest.md。
実施自治体の母集団は各都県の公表一覧:
  千葉県 令和8年度地域少子化対策重点推進交付金（30市町村）
  埼玉県 令和8年度地域少子化対策重点推進交付金活用事業（17市町）
  神奈川県 恋カナ！プロジェクト 新婚世帯等への経済的補助事業（13市町村）
  東京都 TOKYOふたりSTORY 区市町村による支援施策

金額は1世帯あたりの補助上限額（円）。None は「公式ページで確認できなかった」であって0ではない。
推測で埋めない。
"""

CHECKED = "2026年8月31日"

# 国の基準（令和8年度・こども家庭庁 地域少子化対策重点推進交付金）
KUNI = {
    "age": "夫婦ともに婚姻日における年齢が39歳以下",
    "income": "世帯所得500万円未満",
    "amount": "夫婦ともに29歳以下は60万円、夫婦ともに39歳以下は30万円",
    "kouza": "国が指定する内容の講座の受講または相談（令和8年度から要件化）",
    "src": "https://www.pref.chiba.lg.jp/kosodate/shoshikataisaku/r8sicyousonzigyou.html",
    "src_label": "令和8年度地域少子化対策重点推進交付金（千葉県・国の補助対象の記載）",
}

M = []


def add(**kw):
    kw.setdefault("checked", "2026-08-31")
    kw.setdefault("qa_note", "")
    kw.setdefault("age_note", "")
    kw.setdefault("special", "")
    M.append(kw)


# ---------------- 千葉県（30市町村） ----------------
add(pref="千葉県", muni="千葉市", slug="chiba-shi",
    program="千葉市団地住替え支援事業（新婚世帯）",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=None,
    income_note="所得500万円未満の枠と500万円以上の枠の両方がある（申請状況も別々に公表されている）",
    costs=["取得（中古住宅）", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年2月28日（所得500万円未満は令和9年3月31日まで）",
    apply="令和8年6月1日〜令和9年2月28日（消印有効）",
    kouza=True,
    special="高経年住宅団地への転居が条件。団地から他団地・同一団地への転居、新築購入は対象外",
    src="https://www.city.chiba.jp/toshi/kenchiku/jutakuseisaku/danchisumikaekekkon.html",
    src_label="千葉市団地住替え支援事業（新婚世帯）｜千葉市")

add(pref="千葉県", muni="銚子市", slug="choshi",
    program="銚子市結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年2月28日", apply=None, kouza=True,
    special="住居の購入または賃借も令和8年4月1日〜令和9年2月28日の間に行う必要がある",
    src="https://www.city.choshi.chiba.jp/shisei/page020295.html",
    src_label="結婚新生活支援事業｜銚子市")

add(pref="千葉県", muni="市川市", slug="ichikawa",
    program="市川市新婚生活住まい応援事業",
    tiers=[["家賃・共益費 月額2万円まで×12か月", 240000]], max_yen=240000,
    age_max=39, income_max=6000000,
    income_note="所得合算600万円未満（国基準より100万円緩い）",
    costs=["賃借"],
    konin="令和8年1月1日〜令和9年3月31日",
    apply="令和8年6月12日〜令和9年3月31日（オンラインは23時59分まで）", kouza=None,
    special="一時金ではなく家賃補助型。敷金・礼金・仲介手数料も対象経費。パートナーシップ届出も対象",
    qa_note="敷金・礼金・仲介手数料に別枠の上限があるかは公式ページで確認できなかった",
    src="https://www.city.ichikawa.lg.jp/page/4966.html",
    src_label="市川市新婚生活住まい応援事業｜市川市")

add(pref="千葉県", muni="船橋市", slug="funabashi",
    program="船橋市結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和9年3月31日まで", kouza=True,
    special="船橋市パートナーシップ宣誓をした2人も対象",
    src="https://www.city.funabashi.lg.jp/machi/juutaku/005/p129063.html",
    src_label="令和8年度結婚新生活支援事業について｜船橋市")

add(pref="千葉県", muni="木更津市", slug="kisarazu",
    program="木更津市結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年6月15日〜令和9年3月31日", kouza=True,
    special="街なか居住マンション取得助成・空家リフォーム助成との併給不可",
    src="https://www.city.kisarazu.lg.jp/soshiki/kenkokodomo/kosodateshien/1/4455.html",
    src_label="令和8年度結婚新生活支援事業補助金のご案内｜木更津市")

add(pref="千葉県", muni="松戸市", slug="matsudo",
    program="松戸市結婚新生活住宅支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin=None, apply="令和8年6月1日〜令和9年3月31日（必着）", kouza=True,
    special="令和8年7月31日時点で予算額の約5パーセントが受付済みと公表",
    src="https://www.city.matsudo.chiba.jp/kurashi/sumai/tatemono_jyosei/marriage_new_life.html",
    src_label="結婚新生活住宅支援｜松戸市")

add(pref="千葉県", muni="野田市", slug="noda",
    program="野田市結婚支援事業（結婚新生活支援）",
    tiers=[["夫婦ともに29歳以下", 600000], ["それ以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜", kouza=True,
    special="婚姻の届出をした日の60日前までに支払った分は対象外",
    src="https://www.city.noda.chiba.jp/kurashi/1016881/1016976/index.html",
    src_label="令和8年度 野田市での結婚新生活に係る住居費・引越費用を補助します｜野田市")

add(pref="千葉県", muni="成田市", slug="narita",
    program="成田市結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="令和8年4月1日から夫婦そろって対象講座を受講することが要件に加わった。前年度に上限額に達していない世帯は継続申請できる",
    src="https://www.city.narita.chiba.jp/shisei/page0101_00052.html",
    src_label="結婚を機に新生活を始める新婚世帯に最大60万円を助成します｜成田市")

add(pref="千葉県", muni="佐倉市", slug="sakura",
    program="佐倉市結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000,
    income_note="夫婦以外の同居者がいる場合はその所得も合算する",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="リフォームは請負工事契約が別かつ工期が別であれば住宅費と併用できる",
    src="https://www.city.sakura.lg.jp/soshiki/jutakuka/103/2843.html",
    src_label="令和8年度佐倉市結婚新生活支援事業について｜佐倉市")

add(pref="千葉県", muni="東金市", slug="togane",
    program="東金市結婚新生活支援事業補助金",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜", kouza=True,
    special="交付申請の前に資格認定を受ける必要がある。上限額は2年間を通した額。勤務先の住宅手当相当額は対象経費から除く",
    src="https://www.city.togane.chiba.jp/0000011171.html",
    src_label="新婚世帯の新生活を応援します｜東金市")

add(pref="千葉県", muni="市原市", slug="ichihara",
    program="いちはら結婚新生活応援事業",
    tiers=[["住宅取得＋市外転入＋中古＋居住誘導区域＋29歳以下（加算すべて）", 1300000],
           ["住宅取得（基本）", 500000],
           ["賃貸・リフォーム・引越＋夫婦とも29歳以下", 600000],
           ["賃貸・リフォーム・引越（基本）", 300000]], max_yen=1300000,
    age_max=39, income_max=5000000,
    income_note="所得合計500万円未満。ただし住宅取得の場合は550万円未満",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日以降（令和8年3月31日以前に新築・購入の契約が完了している場合は令和7年中の婚姻も対象）",
    apply="令和8年10月1日〜令和9年3月31日（継続補助は令和8年4月1日から）", kouza=True,
    special="取得型は基本50万円に加算（市外からの転入50万円・中古住宅10万円・居住誘導区域内10万円・29歳以下10万円）。フラット35地域連携型の金利優遇と連携。3年以上の居住が条件",
    src="https://www.city.ichihara.chiba.jp/article?articleId=60237680ece4651c88c1860a",
    src_label="いちはら結婚新生活応援事業（婚姻等に伴う住居費等への補助）｜市原市")

add(pref="千葉県", muni="鎌ケ谷市", slug="kamagaya",
    program="鎌ケ谷市結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=None,
    special="レンタカーを借りて引越をした場合は対象外。申請日から2年以上の居住意思が必要",
    src="https://www.city.kamagaya.chiba.jp/kurashi-tetsuzuki/sumai/kekkonsinseikatu.html",
    src_label="鎌ケ谷市結婚新生活支援事業｜鎌ケ谷市")

add(pref="千葉県", muni="富津市", slug="futtsu",
    program="富津市結婚新生活支援事業補助金",
    tiers=[["年齢区分なし（一律）", 700000]], max_yen=700000,
    age_max=49, age_note="婚姻日における年齢が夫婦ともに49歳以下（国基準は39歳以下）",
    income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=True,
    special="対象費用の支払期限が令和10年3月31日までと長い",
    src="https://www.city.futtsu.lg.jp/0000006538.html",
    src_label="令和8年度富津市結婚新生活支援事業補助金｜富津市")

add(pref="千葉県", muni="四街道市", slug="yotsukaido",
    program="四街道市結婚新生活応援事業補助金",
    tiers=[["夫婦ともに29歳以下", 600000], ["それ以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000,
    income_note="特定地域に指定している千代田1〜5丁目に住民登録がある場合は所得制限がない",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月12日", apply=None, kouza=True,
    special="千代田地区だけ所得要件が免除される（市内で扱いが分かれる珍しい設計）",
    src="https://www.city.yotsukaido.chiba.jp/kosodate/kekkon/kekkonshinseikatsu.html",
    src_label="四街道市結婚新生活応援事業補助金｜四街道市")

add(pref="千葉県", muni="八街市", slug="yachimata",
    program="八街市結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000,
    income_note="夫婦と同居する者がいる場合はその所得も合算する",
    costs=["取得"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日（先着順）", kouza=True,
    special="対象は住宅取得費用のみ。賃貸・引越は対象外",
    src="https://www.city.yachimata.lg.jp/site/iju/26713.html",
    src_label="八街市結婚新生活支援事業補助金｜八街市")

add(pref="千葉県", muni="白井市", slug="shiroi",
    program="白井市結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="前年度に上限額に達しなかった世帯は継続申請できる",
    src="https://www.city.shiroi.chiba.jp/soshiki/seisaku/s03/kis004/kis019/20241029/15356.html",
    src_label="結婚新生活支援補助金制度について｜白井市")

add(pref="千葉県", muni="富里市", slug="tomisato",
    program="富里市結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["それ以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=True,
    special="倉庫・車庫・門・フェンス・植栽の工事、エアコンや洗濯機など家電の購入・設置費用は対象外。申請書の提出前に相談が必要",
    src="https://www.city.tomisato.lg.jp/0000016139.html",
    src_label="富里市結婚新生活支援事業補助金｜富里市")

add(pref="千葉県", muni="匝瑳市", slug="sosa",
    program="匝瑳市結婚新生活応援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["それ以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年3月1日〜令和9年3月31日", apply=None, kouza=True,
    special="申請日から2年以上継続して市内に居住する意思が必要",
    src="https://www.city.sosa.lg.jp/page/page004720.html",
    src_label="結婚新生活応援事業補助金を交付します【令和8年度事業】｜匝瑳市")

add(pref="千葉県", muni="香取市", slug="katori",
    program="香取市結婚新生活支援事業補助金",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=None,
    special="建物購入費に係るローン返済費用も対象。前年度の交付額が上限に満たない世帯は継続申請できる場合がある",
    src="https://www.city.katori.lg.jp/kosodate/teate_josei/kekkonnshinnseikatsu.html",
    src_label="令和8年度「香取市結婚新生活支援事業補助金」｜香取市")

add(pref="千葉県", muni="山武市", slug="sammu",
    program="山武市結婚新生活支援補助金",
    tiers=[["夫婦とも29歳以下", 600000], ["それ以外で夫婦とも39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=None,
    special="世帯を代表する者が日本人であるか、永住者・定住者・特別永住者の在留資格を有することが要件",
    src="https://www.city.sammu.lg.jp/kurashi/hojyo-shien/page001004.html",
    src_label="山武市結婚新生活支援補助金｜山武市")

add(pref="千葉県", muni="いすみ市", slug="isumi",
    program="いすみ市結婚新生活支援事業",
    tiers=[["夫婦共に29歳以下", 600000], ["夫婦共に39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["賃借", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="対象は住宅の賃貸費用と引越費用のみ（取得・リフォームは対象外）",
    src="https://www.city.isumi.lg.jp/soshikikarasagasu/child_care/kosodateshienshitsu/2/3/1001.html",
    src_label="令和8年度 いすみ市結婚新生活支援事業｜いすみ市")

add(pref="千葉県", muni="大網白里市", slug="oamishirasato",
    program="大網白里市結婚新生活支援事業",
    tiers=[["夫婦の両方が29歳以下", 600000], ["上記以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=None,
    special="家賃・共益費は令和9年3月支払い分まで、かつ同居開始日以降の分が対象",
    src="https://www.city.oamishirasato.lg.jp/0000012142.html",
    src_label="新婚世帯に最大60万円を補助します｜大網白里市")

add(pref="千葉県", muni="栄町", slug="sakae",
    program="栄町結婚新生活支援事業",
    tiers=[["夫婦共に29歳以下", 600000], ["それ以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日以降", apply=None, kouza=True,
    special="住居費は戸建て住宅の購入またはアパートの家賃",
    src="https://www.town.sakae.chiba.jp/kurashi/teijushien/page003131.html",
    src_label="結婚新生活支援補助金｜栄町")

add(pref="千葉県", muni="東庄町", slug="tohnosho",
    program="東庄町結婚新生活支援事業",
    tiers=[["所得500万円未満かつ夫婦ともに29歳以下", 600000],
           ["所得500万円未満", 300000],
           ["上記に該当しない世帯", 150000]], max_yen=600000,
    age_max=39, income_max=None,
    income_note="所得500万円以上でも15万円の枠がある（国の所得要件を外れても町が単独で出す設計）",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin=None, apply=None, kouza=None,
    special="所得500万円以上の世帯にも15万円を交付する独自枠がある",
    src="https://www.town.tohnosho.chiba.jp/soshiki/somuka/kikakuzaisei_kakari/gyomu/hojokin_joseikin/1466.html",
    src_label="新婚夫婦に引っ越し費用・住居費等を補助します｜東庄町")

add(pref="千葉県", muni="九十九里町", slug="kujukuri",
    program="九十九里町結婚新生活支援補助金",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=True,
    src="https://www.town.kujukuri.chiba.jp/0000008044.html",
    src_label="九十九里町結婚新生活支援補助金を交付します｜九十九里町")

add(pref="千葉県", muni="横芝光町", slug="yokoshibahikari",
    program="横芝光町結婚新生活支援事業",
    tiers=[["おふたりとも29歳以下", 600000], ["それ以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    src="https://www.town.yokoshibahikari.chiba.jp/soshiki/3/28438.html",
    src_label="令和8年度結婚新生活支援事業を実施しています｜横芝光町")

add(pref="千葉県", muni="長生村", slug="chosei",
    program="長生村結婚新生活支援事業補助金",
    tiers=[["夫婦とも満39歳以下・所得500万円未満", 600000],
           ["夫婦とも満39歳以下・所得500万〜750万円未満", 300000],
           ["夫婦のいずれかが満40〜49歳・所得750万円未満", 100000]], max_yen=600000,
    age_max=49, age_note="夫婦の双方または一方が満49歳以下（婚姻日時点）",
    income_max=7500000,
    income_note="所得750万円未満まで対象（国基準の500万円未満より250万円緩い）",
    costs=["取得", "賃借", "リフォーム", "引越", "家具・家電（村内の店舗・業者で購入・限度額10万円）"],
    konin=None, apply=None, kouza=None,
    special="家具・家電の購入費が対象に入る数少ない自治体。同じ年度内の村内転居であれば限度額の範囲内で2回目以降も対象",
    src="https://www.vill.chosei.chiba.jp/0000000592.html",
    src_label="結婚新生活支援事業補助金｜長生村")

add(pref="千葉県", muni="白子町", slug="shirako",
    program="白子町結婚新生活支援事業補助金",
    tiers=[["夫婦の年齢が満39歳以下", 300000], ["上記以外（満49歳以下）", 150000]], max_yen=300000,
    age_max=49, age_note="婚姻日の年齢が夫婦ともに満49歳以下",
    income_max=5000000, income_note="世帯の所得が500万円未満（世帯年収約540万円未満と町が説明）",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年4月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=None,
    special="29歳以下の60万円区分がない。上限は最大30万円",
    src="https://www.town.shirako.lg.jp/0000005757.html",
    src_label="結婚新生活を始めるための費用を補助します！｜白子町")

add(pref="千葉県", muni="長南町", slug="chonan",
    program="長南町結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=None,
    special="対象はリフォーム・賃借・引越（住宅取得の記載はない）",
    src="https://www.town.chonan.chiba.jp/osirase/44965/",
    src_label="令和8年度 長南町結婚新生活支援事業｜長南町")

add(pref="千葉県", muni="大多喜町", slug="otaki",
    program="大多喜町結婚新生活支援事業補助金",
    tiers=[["夫婦ともに29歳以下", 600000], ["いずれか一方または双方が30〜39歳", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="事前申請はできない。婚姻・引越と対象費用の支払いを終えてから申請する",
    src="https://www.town.otaki.chiba.jp/soshiki/kikaku/2/1/3/817.html",
    src_label="大多喜町結婚新生活支援事業補助金｜大多喜町")

# ---------------- 埼玉県（17市町） ----------------
add(pref="埼玉県", muni="秩父市", slug="chichibu",
    program="秩父市結婚新生活支援事業補助金",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="目安として年収約680万円未満と市が説明",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="前払家賃は対象期間に支払ったものに限る（令和8年3月に払った4月分は不可、令和9年3月に払った4月分は可）",
    src="https://www.city.chichibu.lg.jp/9605.html",
    src_label="秩父市結婚新生活支援事業補助金｜秩父市")

add(pref="埼玉県", muni="鴻巣市", slug="kounosu",
    program="鴻巣市結婚新生活支援事業",
    tiers=[["年齢の高い方が29歳以下", 600000], ["年齢の高い方が30〜39歳", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="予算額と予算残額を市が公表している。住宅手当の支給額は対象経費から控除",
    src="https://www.city.kounosu.saitama.jp/page/13309.html",
    src_label="結婚新生活支援事業｜鴻巣市")

add(pref="埼玉県", muni="深谷市", slug="fukaya",
    program="深谷市結婚新生活支援事業",
    tiers=[["夫婦ともに満29歳以下", 600000], ["年齢の高い者が満30〜39歳", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="賃貸費用のうち家賃・共益費は3か月分が上限。予算額と残額を公表",
    src="https://www.city.fukaya.saitama.jp/soshiki/kyoudou/kyoudou/tanto/kekkon_shien/16211.html",
    src_label="令和8年度結婚新生活支援事業について｜深谷市")

add(pref="埼玉県", muni="坂戸市", slug="sakado",
    program="坂戸市結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["それ以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="夫婦のいずれかが令和8年4月1日〜令和9年3月31日に市外から坂戸市へ転入することが条件",
    src="https://www.city.sakado.lg.jp/soshiki/27/22924.html",
    src_label="結婚新生活支援事業｜坂戸市")

add(pref="埼玉県", muni="毛呂山町", slug="moroyama",
    program="毛呂山町結婚新生活支援事業",
    tiers=[["年齢が29歳以下", 600000], ["年齢が39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["賃借"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="賃貸住宅の家賃等を補助する制度。年齢区分は夫婦いずれかの高い方による",
    src="https://www.town.moroyama.saitama.jp/soshikikarasagasu/kikakuzaiseika/kikakukakari/kekkonshiennikansurukoto/12119.html",
    src_label="結婚新生活支援事業｜毛呂山町")

add(pref="埼玉県", muni="川島町", slug="kawajima",
    program="川島町結婚新生活支援事業",
    tiers=[["年齢の高い方が29歳以下", 600000], ["年齢の高い方が30〜39歳", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="年収換算で約680万円相当と町が説明",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年3月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=True,
    special="勤務先から住宅手当が支給されている場合は対象経費から控除",
    src="https://www.town.kawajima.saitama.jp/5882.htm",
    src_label="結婚新生活支援事業補助金｜川島町")

add(pref="埼玉県", muni="長瀞町", slug="nagatoro",
    program="長瀞町結婚新生活支援事業費補助金",
    tiers=[["夫婦ともに婚姻届受理日に29歳以下", 600000], ["上記以外", 300000]], max_yen=600000,
    age_max=39, age_note="補助金の交付申請時に夫婦ともに39歳以下",
    income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="交付から3年以上町内に居住する意思が必要。地域優良賃貸住宅の家賃低廉化を受けている分は控除",
    src="https://www.town.nagatoro.saitama.jp/life/%e7%b5%90%e5%a9%9a%e6%96%b0%e7%94%9f%e6%b4%bb%e6%94%af%e6%8f%b4%e4%ba%8b%e6%a5%ad%e8%b2%bb%e8%a3%9c%e5%8a%a9%e9%87%91/",
    src_label="結婚新生活支援事業費補助金｜長瀞町")

add(pref="埼玉県", muni="小鹿野町", slug="ogano",
    program="小鹿野町結婚・妊娠・共育ての相談機会提供・支援プログラム",
    tiers=[["29歳以下", 600000], ["39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="年齢区分は夫婦のいずれか高い方。前年度に上限未満だった世帯には上限額まで追加支給できる。交付から3年以上の居住意思が必要",
    src="https://www.town.ogano.lg.jp/kekkonsinseikatusienzigyou/",
    src_label="小鹿野町結婚・妊娠・共育ての相談機会提供・支援プログラム（令和8年度）｜小鹿野町")

add(pref="埼玉県", muni="美里町", slug="misato",
    program="美里町結婚新生活支援事業費補助金",
    tiers=[["夫婦ともに婚姻時29歳以下", 600000], ["上記以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和9年3月31日まで", kouza=True,
    special="交付から3年以上町内に居住することが条件で、3年未満で転出した場合は返還。残額は翌年度に限り申請できる",
    src="https://www.town.saitama-misato.lg.jp/0000000027.html",
    src_label="美里町結婚新生活支援事業（令和8年度）｜美里町")

add(pref="埼玉県", muni="神川町", slug="kamikawa",
    program="神川町結婚・妊娠・共育ての相談機会提供・支援プログラム",
    tiers=[["夫婦ともに29歳以下", 600000], ["上記以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日以降", apply=None, kouza=True,
    special="交付から3年以上町内に居住する意思が必要。活用を検討する場合は事前に町民福祉課へ問い合わせる",
    src="https://www.town.kamikawa.saitama.jp/soshiki/chominfukushi/kekkonsien/4051.html",
    src_label="結婚新生活支援事業｜神川町")

add(pref="埼玉県", muni="寄居町", slug="yorii",
    program="寄居町結婚新生活支援事業補助金",
    tiers=[["夫婦ともに29歳以下", 600000], ["上記以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月16日〜令和9年3月31日", kouza=None,
    special="",
    src="https://www.town.yorii.saitama.jp/soshiki/02/kekkonshinseikatsu.html",
    src_label="結婚新生活支援事業補助金｜寄居町")

add(pref="埼玉県", muni="熊谷市", slug="kumagaya",
    program="熊谷市結婚新生活支援事業",
    tiers=[["年齢区分なし（一律）", 300000]], max_yen=300000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年6月1日〜令和9年3月31日", kouza=True,
    special="29歳以下の60万円区分がなく、1世帯当たり30万円が上限。令和9年度への繰り越し申請の予定はないと明記",
    src="https://www.city.kumagaya.lg.jp/about/soshiki/sogo/kikaku/oshirase/lifedesignkumagaya.html",
    src_label="【令和8年6月から受付開始】熊谷市結婚新生活支援事業｜熊谷市")

add(pref="埼玉県", muni="川口市", slug="kawaguchi",
    program="川口市結婚新生活支援補助金",
    tiers=[["年齢区分なし（一律）", 100000]], max_yen=100000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和9年3月31日15時受付まで", kouza=True,
    special="住居費と引越費用の一部で上限10万円。60万円を採る自治体が多いなかでは低い水準。土地購入費や自力での引越は対象外",
    src="https://www.city.kawaguchi.lg.jp/soshiki/01080/060/kekkonnsinnseikatu/50414.html",
    src_label="結婚新生活支援補助金（令和8年度）｜川口市")

add(pref="埼玉県", muni="春日部市", slug="kasukabe",
    program="春日部市結婚新生活支援補助金",
    tiers=[["夫婦のいずれもが29歳以下（対象経費の2分の1）", 600000],
           ["上記以外（対象経費の2分の1）", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "引越"],
    konin="申請年度の1月1日〜翌年3月31日", apply=None, kouza=True,
    special="補助率が2分の1（多くの自治体は実費の全額を上限まで補助する）。住宅手当分は対象外",
    src="https://www.city.kasukabe.lg.jp/kurashi/sumai/sumainikansurujosei/10470.html",
    src_label="結婚新生活支援補助金｜春日部市")

add(pref="埼玉県", muni="上尾市", slug="ageo",
    program="上尾市結婚新生活支援事業",
    tiers=[["29歳以下", 600000], ["それ以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="交付決定日から3年を超える期間の居住意思が必要。予算に対する申請額の割合を公表している",
    src="https://www.city.ageo.lg.jp/page/304984.html",
    src_label="結婚新生活支援事業｜上尾市")

add(pref="埼玉県", muni="横瀬町", slug="yokoze",
    program="横瀬町結婚新生活支援事業",
    tiers=[["夫婦のいずれも29歳以下", 600000], ["それ以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年4月1日〜令和9年3月31日", apply=None, kouza=True,
    special="町税等の滞納がないことが条件",
    src="https://www.town.yokoze.saitama.jp/kurashi/teate/4168",
    src_label="結婚新生活支援事業｜横瀬町")

add(pref="埼玉県", muni="松伏町", slug="matsubushi",
    program="松伏町結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["いずれかが30〜39歳", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=True,
    special="住宅取得費用は建物費用のみが対象。自分や友人が家財を運んだ費用は対象外",
    src="https://www.town.matsubushi.lg.jp/0000000546.html",
    src_label="結婚新生活支援事業補助金｜松伏町")

# ---------------- 神奈川県（13市町村） ----------------
add(pref="神奈川県", muni="相模原市", slug="sagamihara",
    program="結婚新生活・移住定住支援事業",
    tiers=[["年齢区分なし（一律）", 150000]], max_yen=150000,
    age_max=None, age_note="公式ページに年齢要件の記載を確認できなかった",
    income_max=5000000, income_note="",
    costs=["引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年6月1日〜令和9年3月31日", kouza=None,
    special="対象は引越業者・運送業者へ支払った実費のみ。家賃・不用品処分・クリーニング・レンタカーは対象外。パートナーシップ宣誓も対象",
    qa_note="年齢要件は県ページ・市ページのいずれでも明示を確認できなかった",
    src="https://www.city.sagamihara.kanagawa.jp/kurashi/1026489/sumai/1026513/1030229.html",
    src_label="結婚新生活・移住定住支援事業補助金｜相模原市")

add(pref="神奈川県", muni="横須賀市", slug="yokosuka",
    program="横須賀市結婚新生活支援事業",
    tiers=[["29歳以下", 600000], ["39歳以下", 300000], ["49歳以下", 200000]], max_yen=600000,
    age_max=49, age_note="49歳以下まで対象（40〜49歳は20万円）",
    income_max=5000000, income_note="年収では650万円前後が目安と市が説明",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="2026年1月1日〜2027年2月25日", apply=None, kouza=True,
    special="40〜49歳の区分を持つ数少ない自治体。40〜49歳とパートナーシップ宣誓者は講座受講が任意。婚姻日から1年以上同居している住宅は対象外",
    src="https://www.city.yokosuka.kanagawa.jp/0810/kekkonshien.html",
    src_label="【令和8年度】結婚新生活支援事業｜横須賀市")

add(pref="神奈川県", muni="三浦市", slug="miura",
    program="三浦市結婚新生活支援補助金事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月10日", apply="令和8年7月1日〜", kouza=True,
    special="令和7年度に補助決定を受けて上限未達の世帯は講座受講が免除される",
    src="https://www.city.miura.kanagawa.jp/soshiki/seisakuka/seisakuka_seisaku/kekkon/10429.html",
    src_label="結婚新生活支援補助金｜三浦市")

add(pref="神奈川県", muni="秦野市", slug="hadano",
    program="秦野市結婚新生活支援事業助成金",
    tiers=[["夫婦ともに29歳以下", 600000], ["夫婦ともに40歳以下", 300000]], max_yen=600000,
    age_max=40, age_note="婚姻日における年齢が夫婦ともに40歳以下（国基準は39歳以下）",
    income_max=5000000, income_note="",
    costs=["賃借", "引越"],
    konin="令和8年1月1日〜令和9年2月28日", apply="令和9年2月末日まで", kouza=True,
    special="対象は住宅の賃借費用と引越費用のみ（取得・リフォームは対象外）。上限未達なら翌年度に限り繰り越せる",
    src="https://www.city.hadano.kanagawa.jp/soshiki/6/1039/5/2/2709.html",
    src_label="【令和8年度】結婚新生活支援事業助成金のご案内｜秦野市")

add(pref="神奈川県", muni="南足柄市", slug="minamiashigara",
    program="結婚新生活移住支援補助金",
    tiers=[["2人がともに29歳以下", 700000], ["2人がともに39歳以下", 300000]], max_yen=700000,
    age_max=39, income_max=6500000,
    income_note="合計所得650万円未満（国基準より150万円緩い）",
    costs=["取得", "賃借", "リフォーム"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="上限70万円は富津市と並び、市原市に次ぐ高さ。5年以上継続して居住する意思が必要。パートナーシップ宣誓証明も対象",
    src="https://www.city.minamiashigara.kanagawa.jp/teiju/ijyu-shien/p08275.html",
    src_label="結婚新生活移住支援補助金｜南足柄市")

add(pref="神奈川県", muni="寒川町", slug="samukawa",
    program="寒川町結婚新生活支援行政ポイント付与事業",
    tiers=[["さむかわPayポイント（自治会加入加算込み）", 65000], ["現金", 60000]], max_yen=65000,
    age_max=39, income_max=None,
    income_note="公式ページに所得要件の記載を確認できなかった",
    costs=["使途の指定なし（住居費に限定しない給付）"],
    konin="令和8年4月1日〜令和11年3月31日", apply="婚姻届を受理された日から1年以内", kouza=None,
    special="補助金ではなくデジタル地域通貨のポイント付与に切り替えた自治体。従来の結婚新生活支援事業費補助金は令和7年度で終了。基本5万円＋自治会加入加算1万円",
    qa_note="所得要件の有無は公式ページで確認できなかった",
    src="https://www.town.samukawa.kanagawa.jp/soshiki/manabi/kodomoseisaku/kodomoseisaku/info/kekkonsinseikatusien/20492.html",
    src_label="寒川町結婚新生活支援行政ポイント付与事業｜寒川町")

add(pref="神奈川県", muni="中井町", slug="nakai",
    program="中井町結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["それ以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年2月26日", apply="令和8年4月1日〜", kouza=None,
    special="上限未達なら翌年度に限り申請できるが、適用される上限額は前年度のもの",
    src="https://www.town.nakai.kanagawa.jp/soshiki/chiikibosaikachiikijohohan/kekkon/2649.html",
    src_label="結婚新生活支援事業｜中井町")

add(pref="神奈川県", muni="松田町", slug="matsuda",
    program="松田町結婚新生活支援補助金",
    tiers=[["年齢区分なし（一律）", 150000]], max_yen=150000,
    age_max=39, income_max=5000000, income_note="",
    costs=["賃借"],
    konin="申請年度の4月1日〜翌年3月31日", apply=None, kouza=None,
    special="対象は新規の住宅賃借費用のみ（賃料・敷金・礼金・共益費・仲介手数料）。引越費用は対象外",
    src="https://town.matsuda.kanagawa.jp/site/teiju-syoushi/kekkonshien.html",
    src_label="結婚新生活支援事業のご案内｜松田町")

add(pref="神奈川県", muni="山北町", slug="yamakita",
    program="山北町結婚新生活支援事業",
    tiers=[["双方とも29歳以下", 600000], ["双方とも39歳以下", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="前年度1月1日〜翌年3月31日", apply=None, kouza=True,
    special="交付決定の日から10年以上継続して町内に定住する意思が必要（本ページで確認できた範囲では最も長い）。パートナーシップ宣誓も対象",
    src="https://www.town.yamakita.kanagawa.jp/0000005925.html",
    src_label="結婚新生活支援事業｜山北町")

add(pref="神奈川県", muni="箱根町", slug="hakone",
    program="箱根町民間賃貸住宅家賃補助制度（住みたいまち箱根推進事業）",
    tiers=[["実質家賃負担額の2分の1・月額上限2万円×24か月", 480000]], max_yen=480000,
    age_max=39, age_note="婚姻届出日においていずれも40歳未満",
    income_max=None, income_note="公式ページに所得要件の記載を確認できなかった",
    costs=["賃借（家賃の月額補助）"],
    konin="申請日から起算して過去1年以内に婚姻届を提出", apply=None, kouza=None,
    special="一時金ではなく月額の家賃補助。交付期間は最初の申請月の翌月から24か月間。転入若者世帯も対象。パートナーシップ宣誓も対象",
    qa_note="所得要件の有無は公式ページで確認できなかった。48万円は月額上限2万円×24か月から算出した理論上の最大値",
    src="https://www.town.hakone.kanagawa.jp/www/contents/1100000002059/index.html",
    src_label="箱根町民間賃貸住宅家賃補助制度｜箱根町")

add(pref="神奈川県", muni="湯河原町", slug="yugawara",
    program="湯河原町結婚新生活支援事業",
    tiers=[["夫婦共に29歳以下", 600000], ["それ以外", 300000]], max_yen=600000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="令和8年1月1日〜令和9年3月31日の間に転入または転居の届出をしていることが条件",
    src="https://www.town.yugawara.kanagawa.jp/soshiki/13/1570.html",
    src_label="【新婚世帯の方へ】結婚新生活支援事業について｜湯河原町")

add(pref="神奈川県", muni="愛川町", slug="aikawa",
    program="愛川町結婚新生活支援事業",
    tiers=[["夫婦ともに29歳以下", 600000], ["上記以外", 300000]], max_yen=600000,
    age_max=39,
    age_note="39歳以下は誕生日の前々日までに婚姻届が受理されていることと町が明記",
    income_max=5000000, income_note="",
    costs=["取得", "賃借", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply=None, kouza=True,
    special="年齢の数え方（誕生日の前日に加算される）まで公式ページで説明している",
    src="https://www.town.aikawa.kanagawa.jp/soshiki/minsei/kosodate_shien/kodomofukushi/info/teate/1492588731643.html",
    src_label="結婚新生活支援事業｜愛川町")

add(pref="神奈川県", muni="清川村", slug="kiyokawa",
    program="清川村結婚新生活支援事業補助金",
    tiers=[["夫婦ともに29歳以下", 600000], ["その他世帯", 300000]], max_yen=600000,
    age_max=39, income_max=6000000,
    income_note="所得600万円未満（国基準より100万円緩い）",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年3月1日〜令和9年3月31日", apply=None, kouza=None,
    special="同期間内に村内への転入届等を提出し受理済みであることが条件",
    src="https://www.town.kiyokawa.kanagawa.jp/soshiki/hokenhukushi/kosodate/Subsidy/386.html",
    src_label="結婚新生活支援事業補助金｜清川村")

# ---------------- 東京都 ----------------
add(pref="東京都", muni="立川市", slug="tachikawa",
    program="立川市結婚新生活支援事業",
    tiers=[["年齢区分なし（一律）", 300000]], max_yen=300000,
    age_max=39, income_max=5000000, income_note="",
    costs=["取得", "賃借", "リフォーム", "引越"],
    konin="令和8年1月1日〜令和9年3月31日", apply="令和8年4月1日〜令和9年3月31日", kouza=True,
    special="29歳以下の60万円区分がなく一世帯あたり最大30万円。予算額と残額を公表している",
    src="https://www.city.tachikawa.lg.jp/kurashi/1023799/1023802/1024624.html",
    src_label="結婚新生活支援事業（最大30万円を補助します！）｜立川市")

# 東京都で確認できた「終了・移行」の事例（比較表には出すが、住居費補助としては対象外）
ENDED = [
    {
        "pref": "東京都", "muni": "青梅市", "slug": "ome",
        "program": "結婚新生活スタートアップ応援事業費補助金（最大60万円）",
        "status": "住居費の補助は終了。令和7年4月以降は「おふたりOmeでとう！お祝い金（2.2万円）」と、"
                  "婚姻から5年経過後に住宅を取得している場合の「応援金（10万円＋加算最大50万円）」に移行",
        "note": "東京都の公式ポータル「TOKYOふたりSTORY」からリンクされている旧ページは"
                "2026年8月31日時点で404になっている",
        "src": "https://www.city.ome.tokyo.jp/soshiki/76/100589.html",
        "src_label": "おふたりOmeでとう！お祝い金&応援金｜青梅市",
        "checked": "2026-08-31",
    },
]
