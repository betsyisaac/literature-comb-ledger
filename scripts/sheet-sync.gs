// Literature Comb — "Leads" tab refresher.
//
// Lives here for documentation/version-history, but Google Apps Script
// doesn't run code from a git repo directly — this file is pasted into
// the Apps Script editor bound to the Google Sheet (Extensions > Apps
// Script from within the sheet). Keep this file and the pasted copy in
// sync by hand if you ever edit one.
//
// Replaces an =IMPORTDATA() formula that was in cell A1 of the Leads
// tab. IMPORTDATA is a live array-spill formula and turned out to be
// fragile in practice: any stray interaction with a cell inside its
// output range (a click, a sync hiccup, apparently sometimes nothing
// identifiable at all) can freeze that one cell into a static value,
// which then blocks every future refresh with a #REF! error until
// someone manually deletes the frozen cell. It also left visibly
// inconsistent formatting (font, size, date-as-serial-number) because
// IMPORTDATA writes into whatever formatting a cell already has, and
// cells that had been manually edited at different points in this
// project's history had picked up different leftover formatting.
//
// This script instead does a clean, deliberate overwrite on a timer:
// wipe the sheet completely (content AND formatting), fetch the CSV,
// write plain values, then apply one uniform formatting pass. Every
// refresh starts from a blank slate, so there's no leftover state to
// drift or freeze.

const SPREADSHEET_ID = '1O1VpsQtWpyYNiLdzt0Tsem2LTMZH0mQHgFUCakVUXNc';
const SHEET_NAME = 'Leads';
const INFO_SHEET_NAME = 'Project Info';
const INFO_LAST_UPDATED_CELL = 'B4';
const CSV_URL = 'https://raw.githubusercontent.com/betsyisaac/literature-comb-ledger/main/leads.csv';

function refreshLeads() {
  const response = UrlFetchApp.fetch(CSV_URL, { muteHttpExceptions: true });
  if (response.getResponseCode() !== 200) {
    throw new Error('Fetch failed: HTTP ' + response.getResponseCode());
  }
  const csvText = response.getContentText();
  const rows = Utilities.parseCsv(csvText);
  if (!rows || rows.length === 0) {
    // Refuse to wipe a working sheet with an empty fetch result — a
    // transient GitHub hiccup should leave the last-good data in place,
    // not blank the tab.
    throw new Error('CSV parsed to zero rows — leaving the sheet untouched.');
  }

  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    throw new Error('No sheet named "' + SHEET_NAME + '" found.');
  }

  sheet.clear(); // content AND formatting — no stale state survives a refresh

  const numRows = rows.length;
  const numCols = rows[0].length;
  const targetRange = sheet.getRange(1, 1, numRows, numCols);

  // Force plain-text format BEFORE writing values, so Sheets never
  // auto-converts a date-shaped string ("2026-10-20") into a date
  // serial number.
  targetRange.setNumberFormat('@');
  targetRange.setValues(rows);

  // Uniform cosmetic formatting — same font/size everywhere, answers
  // Betsy's "why is row 1 different" question by making it not be.
  targetRange.setFontFamily('Arial').setFontSize(10).setVerticalAlignment('top');
  targetRange.setWrap(true);

  const headerRange = sheet.getRange(1, 1, 1, numCols);
  headerRange.setFontWeight('bold').setBackground('#d9d9d9');

  sheet.setFrozenRows(1);

  for (let c = 1; c <= numCols; c++) {
    sheet.autoResizeColumn(c);
  }

  // Stamp "Last updated" on the Project Info tab — but ONLY when the CSV
  // content actually differs from the last sync. (The trigger fires every
  // 6 hours regardless; an earlier version stamped on every run, which
  // made "Last updated" mean "last heartbeat" rather than "last change".)
  const csvHash = Utilities.base64Encode(
    Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, csvText, Utilities.Charset.UTF_8));
  const props = PropertiesService.getScriptProperties();
  const infoSheet = ss.getSheetByName(INFO_SHEET_NAME);
  if (infoSheet && props.getProperty('lastCsvHash') !== csvHash) {
    infoSheet.getRange(INFO_LAST_UPDATED_CELL)
      .setValue(Utilities.formatDate(new Date(), 'UTC', 'yyyy-MM-dd HH:mm') + ' UTC');
    props.setProperty('lastCsvHash', csvHash);
  }
}

// Run this ONCE by hand: select "setup" in the function dropdown at the
// top of the Apps Script editor, click Run. It does one immediate
// refresh and installs the recurring trigger (every 6 hours). Safe to
// re-run later — it clears any existing trigger first, so it never
// creates duplicates.
function setup() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'refreshLeads') {
      ScriptApp.deleteTrigger(t);
    }
  });
  ScriptApp.newTrigger('refreshLeads').timeBased().everyHours(6).create();
  refreshLeads();
}

// ---------------------------------------------------------------------
// COMMENT FEED for the headless promotion agent.
//
// SpreadsheetApp can't see threaded Comments (only cell Notes), and the
// daily promotion routine runs headless (no browser). So this doGet()
// turns the Sheet's comment threads into JSON that the routine fetches
// with curl. Deployed as a web app: Execute as = Me, Who has access =
// Anyone. That exposes nothing new — anyone with the Sheet link can
// already read every comment — and the web-app URL itself lives only in
// a local config file on Betsy's machine, never in this repo.
//
// Requires the Drive advanced service: in the Apps Script editor, left
// sidebar "Services" (+) -> "Drive API" -> Add (keep the default version).
// The function reads comments on THIS ONE FILE only and writes nothing.
// ---------------------------------------------------------------------
function doGet(e) {
  const comments = [];
  let pageToken = null;
  do {
    const resp = Drive.Comments.list(SPREADSHEET_ID, {
      pageSize: 100,
      pageToken: pageToken,
      includeDeleted: false,
      fields: 'nextPageToken,comments(id,createdTime,modifiedTime,resolved,deleted,' +
              'content,anchor,quotedFileContent,author(displayName,me),' +
              'replies(id,createdTime,modifiedTime,deleted,content,action,author(displayName,me)))'
    });
    (resp.comments || []).forEach(function (c) { comments.push(c); });
    pageToken = resp.nextPageToken;
  } while (pageToken);
  return ContentService
    .createTextOutput(JSON.stringify({ fetched_at: new Date().toISOString(), comments: comments }))
    .setMimeType(ContentService.MimeType.JSON);
}

// Run once by hand from the editor after adding the Drive service, to
// trigger Google's permission screen for the new Drive scope and to check
// the output in the execution log before deploying.
function testCommentFeed() {
  Logger.log(doGet().getContent().slice(0, 2000));
}
