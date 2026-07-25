# Noe結婚設計室 — note立ち上げキット

## アカウント基本情報

**アカウント名：** Noe結婚設計室

**bio（自己紹介文・note設定画面にそのままコピペ）：**

```
マッチングアプリ・婚活・結婚準備・お金のことを、公式データと実体験で整理する編集部。
「なんとなく」で選ばない結婚準備を。詳しい比較・データはWebサイトで。
※仕組み化・ビジネス発信の「Noe仕組み設計室」の姉妹チャンネルです。
🔗 noe-match.com
```

**note固定表示用の自己紹介記事（初回投稿の前に作っておくと良い・任意）：**

```
はじめまして、Noe結婚設計室です。

マッチングアプリ選びから、結婚相談所、式場探し、婚約指輪、
新生活の準備、そしてお金のことまで。
「なんとなく」で決めてしまいがちな結婚準備の判断材料を、
公式データと実体験をもとに整理してお届けします。

仕組み化・ビジネス発信を行っている「Noe仕組み設計室」の姉妹チャンネルとして、
今回は結婚・婚活というテーマに絞って発信していきます。

各記事の詳しいデータ・比較表は運営サイト（noe-match.com）に
まとめています。気になった記事があれば、ぜひサイトの方もチェックしてみてください。
```

---

## 投稿カレンダー（週2本・火曜/金曜想定）

優先度は「高単価クラスタ→話題性の強いフック→通常クラスタ」の順。
記事本文は `agent/note_drafts/` の同名ファイルをそのままコピペする。

| # | 曜日目安 | ファイル | フック |
|---|---------|---------|--------|
| 1 | 週1・火 | soudanjo-hikaku.md | 「高い方が安いことがある」逆説 |
| 2 | 週1・金 | shikijo-erabi-guide.md | 「初回見積もりは100万円上がる」警告 |
| 3 | 週2・火 | tantei-erabikata.md | 「業界に比較サイトがない」発見 |
| 4 | 週2・金 | kekkon-tenshoku-guide.md | 「住宅ローンとの関係」実用 |
| 5 | 週3・火 | with-seriousness-data.md | 「withで婚活できる？」検証 |
| 6 | 週3・金 | success-rate-data.md | 「結婚した人は4組に1組」統計 |
| 7 | 週4・火 | youbride-marrish-hikaku.md | ユーブライドvsマリッシュ比較 |
| 8 | 週4・金 | batsuichi-guide.md | 再婚活のリアル |
| 9 | 週5・火 | omiai-guide.md | 「omiai成婚率」は非公表という話 |
| 10 | 週5・金 | civil-servant-guide.md | 公務員は最強カードを出し損ねてる |
| 11 | 週6・火 | tokyo-guide.md | 東京の候補が多すぎる問題 |
| 12 | 週6・金 | app-tsukare-guide.md | アプリ疲れの構造的原因 |
| 13 | 週7・火 | youbride-guide.md | 成婚実績を公表している数字の話 |
| 14 | 週7・金 | marrish-guide.md | 離婚歴を最初から言える場所 |

7週間分（約1.5ヶ月）のストックが確保できている計算。
以降は月曜の記事工場が生成する新記事から、都度note_draftsに追加していく
（AGENT.mdの既存ルール通り、新記事生成時に自動でnote下書きも作られる）。

---

## 投稿時の注意点（メモリ記録済みのハマりどころ）

- note下書きへの投入は**paste（貼り付け）イベント一発方式**で行う。
  execCommandループでの自動投入はクラッシュするため使わない
- 空行は「空段落」になり読みにくいと過去に指摘あり。
  貼り付け後、不要な空段落が連続していないか目視確認する
- **見出し画像のアップロードはブラウザ自動化から操作不可**（検証済み）。
  画像は下記の方法で生成し、note編集画面から手動で設定する
- noteにアフィリエイトリンクは直接貼らない（規約リスク）。
  下書きは全て「詳細はサイトへ」の導線のみで作成済み・安全
- サイト記事の丸写しはしない。全て書き下ろし要約（重複コンテンツ回避）

---

## ヘッダー画像・アイキャッチ画像の生成方法

note標準のブラウザ自動化では画像アップロードができないため、
PILで画像を生成し、手動でアップロードする運用にする。

以下のPythonスクリプトで、シンプルなテキストベースのアイキャッチを生成できる
（noe-matchのブランドカラー #ff4d7e を基調）。

```python
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

def make_eyecatch(title, out_path, size=(1280, 670)):
    img = Image.new('RGB', size, color='#fff0f4')
    draw = ImageDraw.Draw(img)
    # 上部にピンクの帯
    draw.rectangle([0, 0, size[0], 12], fill='#ff4d7e')
    # タイトルテキスト（日本語フォントのパスは環境に応じて調整）
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/meiryob.ttc", 56)
        font_small = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 28)
    except Exception:
        font = ImageFont.load_default()
        font_small = font
    # 簡易的な折り返し
    import textwrap
    lines = textwrap.wrap(title, width=14)
    y = size[1]//2 - (len(lines)*70)//2
    for line in lines:
        w = draw.textlength(line, font=font)
        draw.text(((size[0]-w)/2, y), line, fill='#1c2b33', font=font)
        y += 70
    draw.text((size[0]/2-100, size[1]-60), "Noe結婚設計室", fill='#ff4d7e', font=font_small)
    img.save(out_path)

# 使用例
make_eyecatch("成婚実績を公表している\n婚活アプリの話", "eyecatch_soudanjo.jpg")
```

生成後、note編集画面の「見出し画像を追加」から手動でアップロードする。

---

## 効果測定の指標（8月末に確認）

- note各記事のビュー数・スキ数（note管理画面）
- GSCでの指名検索（「noe match」「Noe結婚設計室」等）の出現有無
- サイト全体（noe-match.com）の表示回数の傾き変化
  （note投稿開始前後で伸び率に差が出るか）
