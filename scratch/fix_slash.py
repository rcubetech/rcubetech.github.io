with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = html.replace(r'\$49.99', '$49.99')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
