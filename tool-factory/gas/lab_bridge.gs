// Noeツールラボ — Apps Script ブリッジ
//
// MCP連携ではできない2つの操作を担当する：
//   1. 既存スプレッドシートへの行追記
//   2. メールの実送信（Gmail連携は下書きまでしかできない）
//
// セットアップ（1回だけ）:
//   1. https://script.google.com → 新しいプロジェクト → 既存コードを消してこれを貼る
//   2. 下の TOKEN を、自分だけが知っている長い文字列に書き換える
//   3. 保存 → 「デプロイ」→「新しいデプロイ」→ 種類「ウェブアプリ」
//        実行するユーザー：自分
//        アクセスできるユーザー：全員
//   4. 発行されたURLを控える（このURLとTOKENの組が鍵になる。人に見せない）
//
// セキュリティ上の注意:
//   このWebアプリはURLを知っていれば誰でも叩けるため、TOKEN で認証している。
//   URLとTOKENは公開リポジトリやチャットに貼らないこと。
//   漏れた場合は TOKEN を変更して再デプロイすれば無効化できる。
//   送信先は ALLOWED_RECIPIENTS に列挙したアドレスだけに制限している（誤送信・悪用の防止）。

var TOKEN = 'ここを長いランダム文字列に書き換える';

// メールを送ってよい宛先。空配列にすると「自分だけ」に制限される。
var ALLOWED_RECIPIENTS = [];

function doPost(e) {
  try {
    var req = JSON.parse(e.postData.contents);
    if (req.token !== TOKEN) {
      return respond({ ok: false, error: 'invalid token' });
    }
    switch (req.action) {
      case 'append':  return respond(appendRows(req));
      case 'mail':    return respond(sendMail(req));
      case 'ping':    return respond({ ok: true, message: 'lab bridge alive' });
      default:        return respond({ ok: false, error: 'unknown action: ' + req.action });
    }
  } catch (err) {
    return respond({ ok: false, error: String(err) });
  }
}

// --- 行の追記 -------------------------------------------------------------
// {token, action:'append', sheetId, sheetName, rows:[[...],[...]], keyColumn:1}
// keyColumn を指定すると、その列の値が既にある行はスキップする（二重登録の防止）
function appendRows(req) {
  var ss = SpreadsheetApp.openById(req.sheetId);
  var sheet = req.sheetName ? ss.getSheetByName(req.sheetName) : ss.getSheets()[0];
  if (!sheet) return { ok: false, error: 'sheet not found: ' + req.sheetName };

  var rows = req.rows || [];
  if (!rows.length) return { ok: false, error: 'rows is empty' };

  var skipped = 0;
  if (req.keyColumn) {
    var col = sheet.getRange(1, req.keyColumn, Math.max(1, sheet.getLastRow()), 1).getValues();
    var existing = {};
    col.forEach(function (r) { existing[String(r[0])] = true; });
    rows = rows.filter(function (row) {
      var key = String(row[req.keyColumn - 1]);
      if (existing[key]) { skipped++; return false; }
      existing[key] = true;
      return true;
    });
  }

  if (rows.length) {
    sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, rows[0].length).setValues(rows);
  }
  return { ok: true, appended: rows.length, skipped: skipped, sheet: sheet.getName() };
}

// --- メール送信 -----------------------------------------------------------
// {token, action:'mail', to, subject, body}
// to を省略すると自分宛。ALLOWED_RECIPIENTS 以外への送信は拒否する。
function sendMail(req) {
  var me = Session.getActiveUser().getEmail();
  var to = req.to || me;
  if (to !== me && ALLOWED_RECIPIENTS.indexOf(to) < 0) {
    return { ok: false, error: 'recipient not allowed: ' + to };
  }
  MailApp.sendEmail(to, req.subject || '(件名なし)', req.body || '');
  return { ok: true, to: to };
}

function respond(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
