# landing_page
Landing Pages

## Language pages: rebuild after every change to index.html

`index.html` is the English page and the source of truth. Its texts switch language by JavaScript (the
`translations` object), which search engines do not see. That is why every language also has its own static page:
`/tr/`, `/de/`, `/fr/`, `/es/`, `/ar/`, `/ja/` and `/zh/`, plus `sitemap.xml`. These are generated, so do not
edit them by hand. After any change to `index.html` (text, translations, head, scripts), run:

```
python tools/build_lang_pages.py
```

Commit the generated `<lang>/index.html` files and `sitemap.xml` together with `index.html`.

- Each language's `<title>` and meta description come from the `metaTitle` and `metaDesc` keys.
- The language menu goes to the language's address (`goLanguage`). The main page uses the visitor's saved
  choice, or the browser's language.
- Clicks that open the app send the GA4 event `open_app`.

## Growth and search plan (read before changing the site)

The plan for winning free users lives in the app repo:
`../../researchcube-web/ROADMAP.md`, section "Aşama 5e — Ücretsiz kullanıcı kazanmak" (2026-11-17).

What it means for this site:

- **Product facts.** ResearchCube is now a web app at app.rcubetech.com, and it is also coming to the Microsoft
  Store as an app. Projects live in the user's own Google Drive; account data is in Supabase.
- **Remove stale claims.** Do not write "local-first", "serverless", "Windows 10/11 only" or "download". The meta,
  OG and Twitter descriptions in `index.html` still say "local-first environment".
- **Pro button.** It points to the Microsoft Store, where there is no listing yet. Send people to the app until
  the listing is live.
- **Missing basics.** The site needs `robots.txt`, `sitemap.xml`, `canonical`, `hreflang`, JSON-LD
  `SoftwareApplication`, and a static Turkish page at `/tr/`. The JS language switch is invisible to Google.
- **Search pages.** Write one static HTML page per target search. English targets: free research management
  software, free academic PDF reader, AI research workspace, free literature review tool, research paper
  organizer, free academic writing software. Write Turkish pages too, plus one page per manuscript template.
  Comparison pages must be honest and dated.
- **Tracking.** Watch indexing in Google Search Console (domain property) and Bing Webmaster Tools.
- **Never touch** `Tokens/` or `rcubetch.rar`.
