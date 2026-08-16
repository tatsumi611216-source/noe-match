# note入稿の実行メモ（2026-08-15）

投稿先：**hachimitsu88812（Noe結婚設計室）**。giraffe777には出さない。
公開・予約は**CEO承認後**。下書き保存までがこの作業の範囲。

## 入稿する2本

### 1本目

- タイトル：**義実家がしんどいのは、あなたの心が狭いからではない**
- 本文HTML：`C:\tmp\note1.txt`（本文1,929字）
- タグ：`#義実家` `#嫁姑` `#産後` `#夫婦` `#出産準備`
- 着地先：ガルガル診断／義母・実母記事

### 2本目

- タイトル：**夫婦仲が悪いのか、条件が悪いのか**
- 本文HTML：`C:\tmp\note2.txt`（本文1,600字前後）
- タグ：`#夫婦仲` `#夫婦` `#産後` `#家事分担` `#パートナーシップ`
- 着地先：妻源病診断／ガルガル期の全体解説

**タグの方針**：主題は中間帯の語（義実家4,052／夫婦仲2,977）、
そこにビッグワード（#産後 #夫婦）を併記して大語の棚にも並べる。
noteは1記事に複数タグを付けられるので、狙う語は排他ではない。

## エディタの実装メモ（2026-08-15に確認）

- 新規作成 `https://note.com/notes/new` → `editor.note.com/notes/<id>/edit/` へ遷移
- タイトル：`textarea`（placeholder「記事タイトル」）1つだけ
- 本文：`[contenteditable]`（ProseMirror）
- **本文の投入は paste イベント一発**。`text/html` を `DataTransfer` に載せる。
  execCommandのループは使わない（クラッシュする・過去の実測）
- **editor.note.com は note.com と別オリジン**のため、
  `/api/v1/current_user` 等でのアカウント照合はエディタ側からは取れない。
  照合は note.com 側のタブか、公開APIの `creators/hachimitsu88812` で行う

## 投入手順

```js
// タイトル
const ta=document.querySelector('textarea'); ta.focus();
const s=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
s.call(ta, TITLE); ta.dispatchEvent(new Event('input',{bubbles:true}));

// 本文（paste一発）
const ce=document.querySelector('[contenteditable]'); ce.focus();
const dt=new DataTransfer(); dt.setData('text/html', HTML);
ce.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));
```

投入後に**必ず確認**：空段落が増えていないか（過去に「スペースが多くて読みにくい」FBの原因）。
`md2note.py` は空段落を作らない変換にしてあるが、貼り付け後の実物で見る。
