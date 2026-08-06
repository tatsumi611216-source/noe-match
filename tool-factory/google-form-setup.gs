// Noe ツール発注フォーム — Google Form 自動生成スクリプト
//
// 使い方（1回だけ）:
// 1. https://script.google.com → 新しいプロジェクト → 既存コードを全部消して貼り付け
// 2. 保存して「実行」（初回は承認画面が出る。「詳細」→「移動」→「許可」）
// 3. 実行ログにフォームURL・編集URL・回答シートURLが表示される
//
// 発注後の流れ:
// フォームに回答 → Claudeに「Google Formの発注を確認して製造して」と伝える
// → Claudeが回答シート「Noe ツール発注 回答」の最新行を読み、実現可否を判定してから製造する

function createNoeOrderForm() {
  var ss = SpreadsheetApp.create('Noe ツール発注 回答');
  var form = FormApp.create('Noe ツール発注フォーム — 自動化ヒアリングシート');

  form.setDescription(
    '自動化したい作業について答えてください。部品や技術の知識は不要です。\n' +
    '送信後、Claudeに「Google Formの発注を確認して製造して」と伝えると、\n' +
    '実現可否の判定 → ツールの製造が始まります。'
  );
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  form.setConfirmationMessage(
    '発注を受け付けました。\n' +
    'Claudeに「Google Formの発注を確認して製造して」と伝えてください。'
  );

  form.addParagraphTextItem()
    .setTitle('Q1. 自動化したいこと')
    .setHelpText(
      '今は手でやっている（またはやれていない）作業を、そのまま書いてください。\n' +
      '例：毎週、気になる中古物件をサイトで見て回って、良さそうなものをスプレッドシートにメモしている。'
    )
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Q2. きっかけ — その作業はいつ始まる？')
    .setChoiceValues([
      '自分が頼んだとき',
      '毎日・毎週など決まったタイミング',
      '何かが起きた瞬間（メールが来たら即、など）'
    ])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('Q3. 材料 — 何を見て・何を使う作業？')
    .setHelpText('複数選択可')
    .setChoiceValues([
      '誰でも見られるWebサイト',
      'ログインが必要なサイト・アプリ',
      'Gmail・カレンダー・Notion・Drive',
      '手元のファイル（Excel・PDFなど）',
      '社内システム・専用ソフト',
      '特になし（頭の中の考え・相談ごと）'
    ]);

  form.addCheckboxItem()
    .setTitle('Q4. 加工 — その材料に何をしている？')
    .setHelpText('複数選択可')
    .setChoiceValues([
      '集める・整理する・まとめる',
      '決まった基準で選別・計算・判定する',
      '文章・資料・レポートを作る',
      '案を考える・検証する・意思決定する',
      '感覚で判断している（基準をまだ言葉にできない）'
    ]);

  form.addCheckboxItem()
    .setTitle('Q5. 成果 — 最後に何がどこにあれば完了？')
    .setHelpText('複数選択可')
    .setChoiceValues([
      'チャットで報告してくれれば良い',
      'レポート・一覧表になっている',
      'Notion・スプレッドシート等に記録されている',
      'メール送信・SNS投稿など外に発信されている'
    ]);

  form.addMultipleChoiceItem()
    .setTitle('Q6. 自分の関わり方')
    .setChoiceValues([
      '全部おまかせでいい',
      '最後に自分が確認してから確定したい',
      '途中の大事な判断は自分がやりたい'
    ]);

  form.addParagraphTextItem()
    .setTitle('Q7. 頻度と量・補足')
    .setHelpText('どのくらいの頻度・件数か、判断基準、その他伝えたいこと');

  Logger.log('✅ フォームができました');
  Logger.log('回答用URL（ブックマーク推奨）: ' + form.getPublishedUrl());
  Logger.log('編集用URL: ' + form.getEditUrl());
  Logger.log('回答スプレッドシート: ' + ss.getUrl());
}
