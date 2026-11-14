/**
 * One-off mailing: moves the İTÜ users of the old "ResearchCube Pro Desktop" app to the new
 * ResearchCube (web, Windows from the Microsoft Store, Mac). Everyone gets their OWN email with their
 * OWN single-use ResearchCube promotion code (typed in the app under Account -> Plan).
 *
 * The codes never live in this repository: they are in a private tab of the same Sheet as Code.gs.
 * Tab "Migration", row 1 = header:  Email | Code | Status | SentAt
 *   Status empty -> send; SENT -> already sent (skipped, so running again never sends twice);
 *   HOLD -> never sent (e.g. the Store buyer whose email we do not know).
 * The codes themselves must already exist in Supabase (researchcube-web/docs/promo-codes.md).
 *
 * Run from the Apps Script editor (no deployment needed):
 *   1. sendMigrationTest()   -> one sample email to TEST_EMAIL, with the first row's code. Check it.
 *   2. sendMigrationEmails() -> every row whose Status is empty, one email each.
 */

const MIGRATION_TAB = 'Migration';
const TEST_EMAIL = 'info@rcubetech.com';               // the sample goes here
const APP_URL = 'https://app.rcubetech.com';
const NEW_STORE_URL = '';                              // the new ResearchCube's Store link; '' = no Store button
const PRO_PERIOD_TEXT = 'kodu kullandığınız günden itibaren 1 yıl';   // keep in line with the codes' pro_days
const REDEEM_BY_TEXT = '31 Mart 2027';                 // the codes' redeem_by

function sendMigrationTest() {
  const rows = migrationRows_();
  if (!rows.length) throw new Error('The Migration tab has no codes.');
  sendMigrationEmail_(TEST_EMAIL, rows[0].code, true);
  Logger.log('Sample sent to ' + TEST_EMAIL);
}

function sendMigrationEmails() {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(MIGRATION_TAB);
    const rows = migrationRows_();
    let sent = 0, skipped = 0;
    const failed = [];
    for (const r of rows) {
      if (r.status || !isValidEmail(r.email)) { skipped++; continue; }
      if (MailApp.getRemainingDailyQuota() < 2) { failed.push('daily quota reached, run again tomorrow'); break; }
      try {
        sendMigrationEmail_(r.email, r.code, false);
        sheet.getRange(r.row, 3).setValue('SENT');
        sheet.getRange(r.row, 4).setValue(new Date());
        SpreadsheetApp.flush();
        sent++;
      } catch (err) {
        failed.push(r.email + ': ' + err);
      }
    }
    const summary = `Sent ${sent}, skipped ${skipped}` + (failed.length ? `, failed ${failed.length}:\n` + failed.join('\n') : '');
    Logger.log(summary);
    if (NOTIFY_EMAIL) MailApp.sendEmail(NOTIFY_EMAIL, 'ResearchCube: İTÜ geçiş e-postaları', summary);
  } finally {
    lock.releaseLock();
  }
}

function migrationRows_() {
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(MIGRATION_TAB);
  if (!sheet) throw new Error('Add a tab named "' + MIGRATION_TAB + '" (Email | Code | Status | SentAt).');
  return sheet.getDataRange().getValues().slice(1)
    .map((v, i) => ({ row: i + 2, email: String(v[0]).trim().toLowerCase(), code: String(v[1]).trim(), status: String(v[2]).trim().toUpperCase() }))
    .filter(r => r.code);
}

function sendMigrationEmail_(toEmail, code, isTest) {
  const subject = (isTest ? '[DENEME] ' : '') + 'ResearchCube Pro\'nuz yeni uygulamaya taşınıyor';
  const storeLine = NEW_STORE_URL ? `\nWindows için Microsoft Store: ${NEW_STORE_URL}` : '';

  const body = `Merhaba,

İTÜ iş birliği kapsamında kullandığınız ResearchCube Pro Desktop, yerini yeni ResearchCube uygulamasına bırakıyor. Yeni ResearchCube tarayıcıda, Windows'ta (Microsoft Store) ve Mac'te çalışıyor; projeleriniz yine kendi Google Drive'ınızda duruyor.

Pro'nuz devam ediyor. Size özel promosyon kodunuz:

${code}

Nasıl kullanılır?
1. ResearchCube'u açın: ${APP_URL}${storeLine}
2. Google hesabınızla giriş yapın ve Google Drive'ı bağlayın.
3. Hesap > Plan bölümünde "Promosyon kodun var mı?" alanına kodu yazıp "Kodu kullan"a basın.

Pro, ${PRO_PERIOD_TEXT} açık kalır. Kod en geç ${REDEEM_BY_TEXT} tarihine kadar kullanılabilir. Süre bitince hesabınız ücretsiz plana geçer, verileriniz yerinde kalır.

Bu kod kişiye özeldir ve tek kullanımlıktır; lütfen üçüncü kişilerle paylaşmayınız. Eski masaüstü uygulamasını kaldırabilirsiniz.

Görüş, öneri ve hata bildirimleriniz için: info@rcubetech.com

Keyifli araştırmalar dileriz.

ResearchCube Team
AI-Powered Research Workspace`;

  const button = (href, label, primary) =>
    `<a href="${href}" style="display:inline-block; background:${primary ? '#2563eb' : '#ffffff'}; color:${primary ? '#ffffff' : '#2563eb'}; border:1px solid #2563eb; text-decoration:none; font-weight:bold; padding:12px 24px; border-radius:8px; margin:4px;">${label}</a>`;
  const htmlBody = `<div style="font-family:Arial,Helvetica,sans-serif; max-width:600px; margin:0 auto; color:#0f172a; font-size:15px; line-height:1.6;">
    <img src="cid:banner" alt="ResearchCube x ITU" style="width:100%; max-width:600px; display:block; margin-bottom:28px; border-radius:8px;">
    <p>Merhaba,</p>
    <p>İTÜ iş birliği kapsamında kullandığınız <strong>ResearchCube Pro Desktop</strong>, yerini yeni <strong>ResearchCube</strong> uygulamasına bırakıyor. Yeni ResearchCube tarayıcıda, Windows'ta (Microsoft Store) ve Mac'te çalışıyor; projeleriniz yine kendi Google Drive'ınızda duruyor.</p>
    <p style="margin-bottom:4px;"><strong>Pro'nuz devam ediyor. Size özel promosyon kodunuz:</strong></p>
    <p style="font-size:20px; font-weight:bold; letter-spacing:1px; background:#f0f6ff; padding:14px 18px; border-radius:8px; text-align:center; margin:8px 0 20px;">${code}</p>
    <p style="text-align:center; margin:0 0 20px;">${button(APP_URL, 'ResearchCube\'u Açın', true)}${NEW_STORE_URL ? button(NEW_STORE_URL, 'Microsoft Store', false) : ''}</p>
    <p style="margin-bottom:4px;"><strong>Nasıl kullanılır?</strong></p>
    <ol style="margin-top:4px;">
      <li>ResearchCube'u açın (<a href="${APP_URL}">app.rcubetech.com</a>${NEW_STORE_URL ? ' ya da Microsoft Store' : ''}).</li>
      <li>Google hesabınızla giriş yapın ve Google Drive'ı bağlayın.</li>
      <li><strong>Hesap &gt; Plan</strong> bölümünde "Promosyon kodun var mı?" alanına kodu yazıp <strong>Kodu kullan</strong>'a basın.</li>
    </ol>
    <p>Pro, ${PRO_PERIOD_TEXT} açık kalır. Kod en geç ${REDEEM_BY_TEXT} tarihine kadar kullanılabilir. Süre bitince hesabınız ücretsiz plana geçer, verileriniz yerinde kalır.</p>
    <p>Bu kod kişiye özeldir ve tek kullanımlıktır; lütfen üçüncü kişilerle paylaşmayınız. Eski masaüstü uygulamasını kaldırabilirsiniz.</p>
    <p>Görüş, öneri ve hata bildirimleriniz için: 📧 <a href="mailto:info@rcubetech.com">info@rcubetech.com</a></p>
    <p>Keyifli araştırmalar dileriz.</p>
    <p>ResearchCube Team<br>AI-Powered Research Workspace</p>
  </div>`;

  const bannerBlob = Utilities.newBlob(Utilities.base64Decode(BANNER_IMAGE_BASE64), BANNER_IMAGE_MIME_TYPE, 'banner.jpg');
  MailApp.sendEmail({
    to: toEmail,
    subject: subject,
    body: body,
    htmlBody: htmlBody,
    inlineImages: { banner: bannerBlob },
    name: 'ResearchCube Team',
    replyTo: 'info@rcubetech.com'
  });
}
