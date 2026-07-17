# Contact form backend + ITU license dispenser (Google Apps Script)

Backend for the site's existing "Get in Touch" contact form — every
submission goes here now, there's no separate ITU page or form and Web3Forms
is no longer used. ResearchCube is a global product, so the reply language
follows the sender's own email domain:

- **`@itu.edu.tr` senders** get a Turkish reply. If their message contains
  the word "Lisans", the script also hands out one unused key from a private
  Google Sheet, marks it redeemed, and emails the key to them. Domain is
  re-checked server-side — never trust the client for that.
- **Everyone else** (the general, worldwide audience) gets a generic English
  acknowledgment reply. They never touch the license key pool — that offer
  is ITU-exclusive.

Either way, your `NOTIFY_EMAIL` gets a copy so nothing sent through the form
gets lost.

The `Tokens/University.tsv` file in the repo root holds the real keys. It is
git-ignored on purpose — never commit it or paste its contents into a public
place. This script keeps the keys in a Google Sheet that only you can see;
the website never receives the full key list, only the one key issued to it.

## 1. Create the Sheet

1. Create a new Google Sheet (keep it private — do **not** enable "Anyone
   with the link").
2. Rename the first tab to `Keys`.
3. Add this header row, then one row per key with `Status` set to
   `AVAILABLE` and the other two columns left blank:

   | Key | Status | RedeemedByEmail | RedeemedAt |
   |-----|--------|------------------|------------|
   | 2DFCK-CGTD6-TRM6Q-PGH32-2HD7Z | AVAILABLE | | |

   Populate this from the `Promotional code` column of
   `Tokens/University.tsv`.
4. Copy the Sheet's ID from its URL:
   `https://docs.google.com/spreadsheets/d/`**`THIS_PART`**`/edit`.

## 2. Create the Apps Script project

1. Go to [script.google.com](https://script.google.com) → New project.
2. Delete the default `Code.gs` contents and paste in this folder's
   `Code.gs`.
3. Set `SHEET_ID` at the top to the ID you copied above.
4. Adjust `NOTIFY_EMAIL` if you don't want a copy of every issued key, or
   leave it as `info@rcubetech.com`.
5. Add a **second file** to the project (the `+` next to "Files" → Script):
   name it `ImageData`, and paste in this folder's `ImageData.gs` — it's the
   banner image (`assets/rc_mail.jpeg`) embedded as base64 so the license
   email can show it inline without depending on any external hosting. If
   you swap the banner image later, regenerate this file (base64-encode the
   new image and replace the `BANNER_IMAGE_BASE64` value).

## 3. Deploy as a Web App

1. Deploy → New deployment → type **Web app**.
2. "Execute as": **Me**.
3. "Who has access": **Anyone**. (Required — visitors are not Google-signed-in.)
4. Deploy, authorize the requested Gmail/Sheets permissions, and copy the
   `.../exec` Web App URL it gives you.

## 4. Wire it into the site

In [index.html](../index.html), find:

```js
const CONTACT_BACKEND_ENDPOINT = "PASTE_YOUR_APPS_SCRIPT_WEB_APP_URL_HERE";
```

and replace the placeholder with the URL from step 3. `handleContactSubmit`
already posts every submission here — no other frontend change is needed.

## Notes

- Every time you edit `Code.gs` in the Apps Script editor you must create a
  **new deployment version** (Deploy → Manage deployments → edit → new
  version) for the changes to go live at the same URL.
- Gmail sending quota is ~100/day on a personal account, 1500/day on Google
  Workspace. Every contact form submission now sends at least one email
  (reply) plus one to `NOTIFY_EMAIL`, so a busy day counts against this quota
  faster than when only ITU submissions went through Apps Script. If the
  global contact form gets meaningful traffic, consider a Workspace account
  or a dedicated transactional email API instead of personal Gmail.
- Non-ITU senders never reach the Sheet at all, so general contact form
  traffic can't drain the license key pool.
- The lock (`LockService`) prevents two simultaneous submissions from being
  handed the same row, so a double-click or network retry can't hand the
  same person two different keys.
- If an email that already redeemed a key submits again, the script resends
  that *same* key (doesn't issue a new one) — handles "it went to spam" /
  "I lost it" without letting repeat submissions drain the pool. It can't
  stop one person from using several different `@itu.edu.tr` addresses,
  though — there's no identity check beyond the domain.
- To add more keys later, just append more `AVAILABLE` rows to the sheet.
