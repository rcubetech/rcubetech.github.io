"""Builds a static page per language (/tr/, /de/, ...) from index.html, plus sitemap.xml.

index.html is the English page and the source of truth. Its texts change by JavaScript (data-i18n keys
in the `translations` object), which search engines do not see, so every language also gets its own
address with the text already in the HTML. Run after every change to index.html:

    python tools/build_lang_pages.py

and commit the generated <lang>/index.html files and sitemap.xml with it.
"""
import datetime
import html
import io
import json
import os
import re
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://rcubetech.com'
LANGS = ['en', 'tr', 'ar', 'fr', 'es', 'de', 'zh', 'ja']
OG_LOCALE = {'en': 'en_US', 'tr': 'tr_TR', 'ar': 'ar_AR', 'fr': 'fr_FR', 'es': 'es_ES', 'de': 'de_DE', 'zh': 'zh_CN', 'ja': 'ja_JP'}
STATIC_PAGES = [
    [('en', '/features.html')],
    [('en', '/overleaf-alternative/'), ('tr', '/tr/overleaf-alternatifi/')],
    [('en', '/overleaf-alternatives/'), ('tr', '/tr/overleaf-alternatifleri/')],
]
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


def page_url(lang):
    return f'{SITE}/' if lang == 'en' else f'{SITE}/{lang}/'


def translations(src):
    """The `const translations = {...};` object of the page, as a dict."""
    start = src.index('const translations = {') + len('const translations = ')
    depth, i, in_str = 0, start, False
    while True:
        c = src[i]
        if in_str:
            if c == '\\':
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        i += 1
    js = src[start:i + 1]
    js = re.sub(r'^(\s*)(\w+): \{', r'\1"\2": {', js, flags=re.M)   # language keys
    js = re.sub(r',(\s*)\}', r'\1}', js)                              # trailing commas
    return json.loads(js)


class I18nElements(HTMLParser):
    """Content ranges (start, end offsets) of the elements with a data-i18n key."""

    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.line_starts = [0]
        for m in re.finditer('\n', src):
            self.line_starts.append(m.end())
        self.stack, self.found = [], []

    def at(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        key = dict(attrs).get('data-i18n')
        self.stack.append((tag, key, self.at() + len(self.get_starttag_text())))

    def handle_endtag(self, tag):
        for k in range(len(self.stack) - 1, -1, -1):
            if self.stack[k][0] == tag:
                _, key, start = self.stack[k]
                del self.stack[k:]
                if key:
                    self.found.append((start, self.at(), key))
                return


def render(src, lang, t, en):
    # Text of the elements, as setLanguage() would set it (a missing key keeps the English)
    parser = I18nElements(src)
    parser.feed(src)
    out = src
    for start, end, key in sorted(parser.found, reverse=True):
        if key in t:
            out = out[:start] + t[key] + out[end:]

    def attr(v):
        return html.escape(v, quote=True)

    # Placeholders
    def placeholder(m):
        tag = m.group(0)
        key = re.search(r'data-i18n-placeholder="([^"]+)"', tag).group(1)
        if key not in t:
            return tag
        # placeholder="…" itself, not the data-i18n-placeholder="key" next to it
        return re.sub(r'(?<![\w-])placeholder="[^"]*"', lambda _: f'placeholder="{attr(t[key])}"', tag)
    out = re.sub(r'<(?:input|textarea)\b[^>]*data-i18n-placeholder="[^"]+"[^>]*>', placeholder, out)

    # The head: language, title, description, address
    title, desc = t.get('metaTitle', en['metaTitle']), t.get('metaDesc', en['metaDesc'])
    dir_ = ' dir="rtl"' if lang == 'ar' else ''
    out = re.sub(r'<html lang="en">', f'<html lang="{lang}"{dir_} data-page-lang="{lang}">', out, count=1)
    out = re.sub(r'<title>[^<]*</title>', f'<title>{html.escape(title, quote=False)}</title>', out, count=1)
    for pat in (r'(<meta name="description" content=")[^"]*', r'(<meta property="og:description" content=")[^"]*',
                r'(<meta name="twitter:description" content=")[^"]*'):
        out = re.sub(pat, lambda m: m.group(1) + attr(desc), out, count=1)
    for pat in (r'(<meta property="og:title" content=")[^"]*', r'(<meta name="twitter:title" content=")[^"]*'):
        out = re.sub(pat, lambda m: m.group(1) + attr(title), out, count=1)
    out = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + page_url(lang), out, count=1)
    out = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + page_url(lang), out, count=1)
    out = re.sub(r'("description": )"[^"]*"', lambda m: m.group(1) + json.dumps(desc, ensure_ascii=False), out, count=1)
    out = out.replace('<meta property="og:type" content="website">',
                      f'<meta property="og:type" content="website">\n    <meta property="og:locale" content="{OG_LOCALE[lang]}">', 1)

    # Files next to index.html are one folder up from /<lang>/
    out = re.sub(r'\b(href|src)="(?!https?:|mailto:|tel:|#|/|data:|javascript:)([^"]+)"', r'\1="../\2"', out)
    return out


def main():
    src = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    t = translations(src)
    missing = [l for l in LANGS if l not in t]
    assert not missing, f'no translations for {missing}'
    for lang in LANGS[1:]:
        page = render(src, lang, t[lang], t['en'])
        folder = os.path.join(ROOT, lang)
        os.makedirs(folder, exist_ok=True)
        with io.open(os.path.join(folder, 'index.html'), 'w', encoding='utf-8', newline='') as f:
            f.write(page)
        print(f'{lang}/index.html  {len(page) // 1024} KB  ' + ', '.join(k for k in t['en'] if k not in t[lang]))

    today = datetime.date.today().isoformat()
    alt = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{page_url(l)}"/>' for l in LANGS)
    alt += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{page_url("en")}"/>'
    urls = ''.join(f'\n  <url>\n    <loc>{page_url(l)}</loc>\n    <lastmod>{today}</lastmod>{alt}\n  </url>' for l in LANGS)

    # Hand-written pages (search pages, comparisons). Each group lists the same page in its languages;
    # the first entry is the x-default. lastmod is the file's own modification date.
    count = len(LANGS)
    for group in STATIC_PAGES:
        alt = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{SITE}{p}"/>' for l, p in group)
        if len(group) > 1:
            alt += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{group[0][1]}"/>'
        for lang, path in group:
            file = os.path.join(ROOT, path.strip('/').replace('/', os.sep), 'index.html') if path.endswith('/') else os.path.join(ROOT, path.strip('/'))
            assert os.path.exists(file), f'missing {file}'
            mod = datetime.date.fromtimestamp(os.path.getmtime(file)).isoformat()
            urls += f'\n  <url>\n    <loc>{SITE}{path}</loc>\n    <lastmod>{mod}</lastmod>{alt if len(group) > 1 else ""}\n  </url>'
            count += 1
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
               f'{urls}\n</urlset>\n')
    with io.open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='') as f:
        f.write(sitemap)
    print('sitemap.xml', count, 'pages')


if __name__ == '__main__':
    main()
