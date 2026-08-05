/**
 * ResearchCube contact form backend + ITU free Pro license dispenser.
 *
 * Handles every submission from the site's "Get in Touch" form. ResearchCube
 * is a global product, so the reply language follows the sender's domain:
 * @itu.edu.tr senders get a Turkish reply (and can request a free license by
 * including "Lisans" in their message); everyone else gets a generic English
 * acknowledgment. Only ITU emails ever touch the license key pool.
 *
 * Deployment target: Google Apps Script, bound to a private Google Sheet.
 * See README.md in this folder for full setup steps.
 */

// ---- CONFIG: fill these in after you create the Sheet ----
const SHEET_ID = '12g78hz0z791RZm_wbAHhjDVEyux2YjlDyLtJwYVt0pY';
const SHEET_NAME = 'Keys';               // tab name inside the Sheet
const NOTIFY_EMAIL = 'info@rcubetech.com'; // gets a copy of every issued key; set to '' to disable
const MICROSOFT_STORE_URL = 'https://apps.microsoft.com/detail/9N5K085SCDVZ?hl=en&gl=TR&ocid=pdpshare';

// Accept exact @itu.edu.tr and any subdomain (e.g. @grad.itu.edu.tr)
const ALLOWED_EXACT_DOMAIN = 'itu.edu.tr';
const ALLOWED_DOMAIN_SUFFIX = '.itu.edu.tr';

// Sheet columns (row 1 = header): A Key | B Status | C RedeemedByEmail | D RedeemedAt
const COL_KEY = 1, COL_STATUS = 2, COL_EMAIL = 3, COL_DATE = 4;

// Only messages containing this word actually request a license key; everything
// else from an @itu.edu.tr sender is treated as plain feedback (no key sent/resent).
const LICENSE_KEYWORD = 'lisans';

// Anti-bot: the hidden "website" field must stay empty (real visitors never
// see it) and the form must have been open at least this long before submit
// (bots that hit the endpoint directly either omit loadedAt or fire instantly).
const MIN_FORM_FILL_MS = 2000;

// reCAPTCHA v3: never expose RECAPTCHA_SECRET_KEY to the client - verification
// happens here, server-side, which is what makes it a real check (unlike the
// honeypot/timing gate, which a targeted bot could read out of the page source).
const RECAPTCHA_SECRET_KEY = '6Lfib3ctAAAAANxASh2RrlN3am_iLm3ciZUJKqkq';
const RECAPTCHA_MIN_SCORE = 0.5;

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const body = JSON.parse(e.postData.contents || '{}');
    const name = (body.name || '').toString().trim();
    const email = (body.email || '').toString().trim().toLowerCase();
    const message = (body.message || '').toString().trim();
    const honeypot = (body.hp || '').toString().trim();
    const loadedAt = Number(body.loadedAt);
    const recaptchaToken = (body.recaptchaToken || '').toString();

    // Silently pretend success so bots get no signal to adapt to - no email
    // sent, sheet untouched, no notification, just a fake "ok" response.
    const looksLikeBot = honeypot !== ''
      || !loadedAt
      || (Date.now() - loadedAt) < MIN_FORM_FILL_MS
      || !verifyRecaptcha(recaptchaToken);
    if (looksLikeBot) {
      return jsonResponse({ status: 'ok' });
    }

    if (!isValidEmail(email)) {
      return jsonResponse({ status: 'error', code: 'INVALID_EMAIL', message: 'Please enter a valid email address.' });
    }

    // Non-ITU senders (the global, general public) never touch the license
    // pool - that offer is ITU-exclusive. They just get an English ack.
    if (!isItuEmail(email)) {
      sendGenericAckEmail(email, name);
      if (NOTIFY_EMAIL) {
        const messageLine = message ? `\n\nMessage:\n${message}` : '(no message)';
        MailApp.sendEmail(NOTIFY_EMAIL, 'ResearchCube: new contact form message',
          `${email} (${name || 'no name'}) sent a message.${messageLine}`);
      }
      return jsonResponse({ status: 'ok', kind: 'general' });
    }

    // Plain feedback/questions (no "lisans" in the message) never touch the key
    // pool - resending a license key in response to "great app, one suggestion.."
    // would be nonsensical. Acknowledge it and forward it to us instead.
    if (!containsLicenseKeyword(message)) {
      sendFeedbackAckEmail(email, name);
      if (NOTIFY_EMAIL) {
        const messageLine = message ? `\n\nMesaj:\n${message}` : '(mesaj boş)';
        MailApp.sendEmail(NOTIFY_EMAIL, 'ResearchCube: ITU mailinden geri bildirim',
          `${email} (${name || 'isim yok'}) geri bildirim gönderdi.${messageLine}`);
      }
      return jsonResponse({ status: 'ok', kind: 'feedback' });
    }

    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
    const data = sheet.getDataRange().getValues();

    // One key per person: if this email already redeemed one, resend the SAME key
    // instead of erroring out (covers "I lost the email" / spam-folder / retry cases)
    // without letting repeated submissions drain the pool.
    for (let i = 1; i < data.length; i++) {
      if (String(data[i][COL_EMAIL - 1]).toLowerCase() === email) {
        const existingKey = data[i][COL_KEY - 1];
        sendLicenseEmail(email, name, existingKey);
        if (NOTIFY_EMAIL) {
          MailApp.sendEmail(NOTIFY_EMAIL, 'ResearchCube: ITU anahtarı tekrar gönderildi',
            `${email} daha önce aldığı ${existingKey} anahtarını tekrar istedi, aynı anahtar tekrar gönderildi.`);
        }
        return jsonResponse({ status: 'ok', resent: true });
      }
    }

    let targetRow = -1;
    for (let i = 1; i < data.length; i++) {
      if (String(data[i][COL_STATUS - 1]).toUpperCase() === 'AVAILABLE') {
        targetRow = i;
        break;
      }
    }
    if (targetRow === -1) {
      return jsonResponse({ status: 'error', code: 'OUT_OF_STOCK', message: 'No license keys are left to distribute.' });
    }

    const key = data[targetRow][COL_KEY - 1];
    const rowIndex = targetRow + 1; // 1-based for Range API

    sheet.getRange(rowIndex, COL_STATUS).setValue('REDEEMED');
    sheet.getRange(rowIndex, COL_EMAIL).setValue(email);
    sheet.getRange(rowIndex, COL_DATE).setValue(new Date());
    SpreadsheetApp.flush();

    sendLicenseEmail(email, name, key);

    if (NOTIFY_EMAIL) {
      const messageLine = message ? `\n\nMesajları:\n${message}` : '';
      MailApp.sendEmail(NOTIFY_EMAIL, 'ResearchCube: yeni ITU lisansı verildi',
        `${email} (${name || 'isim yok'}) adresine ${key} anahtarı gönderildi.${messageLine}`);
    }

    return jsonResponse({ status: 'ok' });
  } catch (err) {
    return jsonResponse({ status: 'error', code: 'SERVER_ERROR', message: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Verifies a reCAPTCHA v3 token with Google. An empty token (e.g. the script
// was blocked client-side) fails closed - treated the same as a bot, since a
// missing token is exactly what a bot bypassing the frontend would send too.
function verifyRecaptcha(token) {
  if (!token) return false;
  try {
    const response = UrlFetchApp.fetch('https://www.google.com/recaptcha/api/siteverify', {
      method: 'post',
      payload: { secret: RECAPTCHA_SECRET_KEY, response: token },
      muteHttpExceptions: true
    });
    const result = JSON.parse(response.getContentText());
    return result.success === true
      && (typeof result.score !== 'number' || result.score >= RECAPTCHA_MIN_SCORE);
  } catch (err) {
    // Our call to Google failed (network blip, quota, etc.) - that's not
    // evidence the sender is a bot, so don't penalize them for our hiccup.
    return true;
  }
}

// Turkish-safe keyword check. JS's default (locale-independent) toLowerCase()
// turns 'İ' into "i" + a combining dot (two code points), not plain "i", so a
// naive .toLowerCase().includes('lisans') would silently fail to match
// "LİSANS" typed with the Turkish dotted capital İ. Fold both İ and I to a
// plain "i" ourselves before comparing.
function containsLicenseKeyword(message) {
  const normalized = message.replace(/İ/g, 'i').replace(/I/g, 'i').toLowerCase();
  return normalized.includes(LICENSE_KEYWORD);
}

function isItuEmail(email) {
  const domain = (email.split('@')[1] || '').toLowerCase();
  return domain === ALLOWED_EXACT_DOMAIN || domain.endsWith(ALLOWED_DOMAIN_SUFFIX);
}

function sendLicenseEmail(toEmail, name, licenseKey) {
  const subject = 'ResearchCube Pro - Lisans Anahtarınız';
  const greeting = name ? `Merhaba ${name},` : 'Merhaba,';

  const body = `${greeting}

ResearchCube ailesine hoş geldiniz!

İTÜ ile gerçekleştirdiğimiz iş birliği kapsamında ResearchCube Pro sürümünü ücretsiz kullanabilirsiniz.

Lisans Anahtarınız

${licenseKey}

Uygulamayı Microsoft Store'dan indirebilirsiniz:
${MICROSOFT_STORE_URL}

Bu lisans anahtarı kişiye özeldir, tek kullanımlıktır ve yalnızca sizin kullanımınız için oluşturulmuştur. Lütfen üçüncü kişilerle paylaşmayınız.

ResearchCube, araştırmacılar için geliştirilen yeni nesil AI destekli akademik çalışma platformudur. Amacımız, yapay zekânın bugün ulaştığı en ileri imkânları araştırma süreçlerine entegre ederek literatür taramayı, PDF okumayı, not almayı ve bilimsel üretimi daha verimli hale getirmektir.

Bu yolculuğun henüz başındayız.

İTÜ ile gerçekleştirdiğimiz bu iş birliği bizim için oldukça değerli. Sizlerden gelecek öneri, eleştiri ve geri bildirimler, ResearchCube'un gelişiminde doğrudan etkili olacak. Ürünü birlikte şekillendireceğimize inanıyoruz.

Her türlü görüş, öneri ve hata bildiriminizi bizimle paylaşabilirsiniz.

📧 info@rcubetech.com

ResearchCube'u tercih ettiğiniz ve bu yolculukta bizimle olduğunuz için teşekkür ederiz.

Keyifli araştırmalar dileriz.

ResearchCube Team
AI-Powered Research Workspace`;

  const htmlBody = `<div style="font-family:Arial,Helvetica,sans-serif; max-width:600px; margin:0 auto; color:#0f172a; font-size:15px; line-height:1.6;">
    <img src="cid:banner" alt="ResearchCube x ITU" style="width:100%; max-width:600px; display:block; margin-bottom:28px; border-radius:8px;">
    <p>${greeting}</p>
    <p>ResearchCube ailesine hoş geldiniz!</p>
    <p>İTÜ ile gerçekleştirdiğimiz iş birliği kapsamında ResearchCube Pro sürümünü ücretsiz kullanabilirsiniz.</p>
    <p style="margin-bottom:4px;"><strong>Lisans Anahtarınız</strong></p>
    <p style="font-size:20px; font-weight:bold; letter-spacing:1px; background:#f0f6ff; padding:14px 18px; border-radius:8px; text-align:center; margin:8px 0 20px;">${licenseKey}</p>
    <p style="text-align:center; margin:0 0 20px;"><a href="${MICROSOFT_STORE_URL}" style="display:inline-block; background:#2563eb; color:#ffffff; text-decoration:none; font-weight:bold; padding:12px 24px; border-radius:8px;">Microsoft Store'dan İndirin</a></p>
    <p>Bu lisans anahtarı kişiye özeldir, tek kullanımlıktır ve yalnızca sizin kullanımınız için oluşturulmuştur. Lütfen üçüncü kişilerle paylaşmayınız.</p>
    <p>ResearchCube, araştırmacılar için geliştirilen yeni nesil AI destekli akademik çalışma platformudur. Amacımız, yapay zekânın bugün ulaştığı en ileri imkânları araştırma süreçlerine entegre ederek literatür taramayı, PDF okumayı, not almayı ve bilimsel üretimi daha verimli hale getirmektir.</p>
    <p>Bu yolculuğun henüz başındayız.</p>
    <p>İTÜ ile gerçekleştirdiğimiz bu iş birliği bizim için oldukça değerli. Sizlerden gelecek öneri, eleştiri ve geri bildirimler, ResearchCube'un gelişiminde doğrudan etkili olacak. Ürünü birlikte şekillendireceğimize inanıyoruz.</p>
    <p>Her türlü görüş, öneri ve hata bildiriminizi bizimle paylaşabilirsiniz.</p>
    <p>📧 <a href="mailto:info@rcubetech.com">info@rcubetech.com</a></p>
    <p>ResearchCube'u tercih ettiğiniz ve bu yolculukta bizimle olduğunuz için teşekkür ederiz.</p>
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
    name: 'ResearchCube Team'
  });
}

function sendFeedbackAckEmail(toEmail, name) {
  const subject = 'ResearchCube - Mesajınızı Aldık';
  const greeting = name ? `Merhaba ${name},` : 'Merhaba,';

  const body = `${greeting}

Mesajınız için teşekkür ederiz! Görüş ve geri bildiriminizi aldık, ekibimiz en kısa sürede değerlendirecek.

Not: İTÜ iş birliği kapsamında ücretsiz ResearchCube Pro lisansınızı almak isterseniz, bu adrese göndereceğiniz mesajın içine "Lisans" yazmanız yeterli.

ResearchCube Team
AI-Powered Research Workspace`;

  const htmlBody = `<div style="font-family:Arial,Helvetica,sans-serif; max-width:600px; margin:0 auto; color:#0f172a; font-size:15px; line-height:1.6;">
    <img src="cid:banner" alt="ResearchCube x ITU" style="width:100%; max-width:600px; display:block; margin-bottom:28px; border-radius:8px;">
    <p>${greeting}</p>
    <p>Mesajınız için teşekkür ederiz! Görüş ve geri bildiriminizi aldık, ekibimiz en kısa sürede değerlendirecek.</p>
    <p style="color:#64748b; font-size:13px;">Not: İTÜ iş birliği kapsamında ücretsiz ResearchCube Pro lisansınızı almak isterseniz, bu adrese göndereceğiniz mesajın içine <strong>"Lisans"</strong> yazmanız yeterli.</p>
    <p>ResearchCube Team<br>AI-Powered Research Workspace</p>
  </div>`;

  const bannerBlob = Utilities.newBlob(Utilities.base64Decode(BANNER_IMAGE_BASE64), BANNER_IMAGE_MIME_TYPE, 'banner.jpg');

  MailApp.sendEmail({
    to: toEmail,
    subject: subject,
    body: body,
    htmlBody: htmlBody,
    inlineImages: { banner: bannerBlob },
    name: 'ResearchCube Team'
  });
}

function sendGenericAckEmail(toEmail, name) {
  const subject = 'ResearchCube - We received your message';
  const greeting = name ? `Hi ${name},` : 'Hi,';

  const body = `${greeting}

Thank you for reaching out! We've received your message and our team will review it shortly.

ResearchCube Team
AI-Powered Research Workspace`;

  const htmlBody = `<div style="font-family:Arial,Helvetica,sans-serif; max-width:600px; margin:0 auto; color:#0f172a; font-size:15px; line-height:1.6;">
    <p>${greeting}</p>
    <p>Thank you for reaching out! We've received your message and our team will review it shortly.</p>
    <p>ResearchCube Team<br>AI-Powered Research Workspace</p>
  </div>`;

  MailApp.sendEmail({
    to: toEmail,
    subject: subject,
    body: body,
    htmlBody: htmlBody,
    name: 'ResearchCube Team'
  });
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
