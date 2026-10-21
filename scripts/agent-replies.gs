// Literature Comb — reply endpoint for the promotion agent.
//
// Lives in a SEPARATE Apps Script project owned by the dedicated agent
// Google account ("Literature Comb Maintenance Agent"), NOT in Betsy's
// sheet-sync project, so every reply it posts is authored by the agent
// account and never by Betsy. Deployed as a web app (Execute as: Me,
// Who has access: Anyone) and locked with a shared secret held in this
// project's Script Properties (key SECRET) and in a local config file on
// Betsy's machine. Without the secret, the endpoint does nothing.
//
// It can do exactly one thing: add a reply to an existing comment thread
// on the one Literature Comb sheet. It cannot create top-level comments,
// edit or delete anything, resolve threads, or touch any other file.
// Every reply is prefixed with the agent label if the caller forgot it.
//
// Setup (in the agent account): Services (+) -> Drive API -> Add;
// Project Settings -> Script Properties -> add SECRET = <value Betsy was
// given>; Deploy -> New deployment -> Web app.

const SPREADSHEET_ID = '1O1VpsQtWpyYNiLdzt0Tsem2LTMZH0mQHgFUCakVUXNc';
const LABEL = '[automated maintenance agent for this sheet]';
const MAX_LEN = 3000;

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  const secret = PropertiesService.getScriptProperties().getProperty('SECRET');
  let body;
  try { body = JSON.parse(e.postData.contents); }
  catch (err) { return json_({ ok: false, error: 'bad json' }); }
  if (!secret || body.secret !== secret) return json_({ ok: false, error: 'unauthorized' });

  if (body.ping) return json_({ ok: true, pong: true });

  const commentId = String(body.comment_id || '');
  let text = String(body.text || '').trim();
  if (!commentId || !text) return json_({ ok: false, error: 'missing comment_id or text' });
  if (text.length > MAX_LEN) return json_({ ok: false, error: 'too long' });
  if (text.indexOf(LABEL) !== 0) text = LABEL + ' ' + text;

  try {
    const reply = Drive.Replies.create({ content: text }, SPREADSHEET_ID, commentId,
                                       { fields: 'id,createdTime,content' });
    return json_({ ok: true, reply: reply });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

// Optional: run once from the editor to trigger the Drive permission
// screen and confirm the account can see the sheet's comments.
function testAccess() {
  const r = Drive.Comments.list(SPREADSHEET_ID, { pageSize: 5, fields: 'comments(id,content)' });
  Logger.log(JSON.stringify(r).slice(0, 1500));
}
