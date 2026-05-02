import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace HTML line
html = re.sub(
    r'<div class="price" data-i18n="tierFreePrice">\$0<span> forever</span></div>',
    r'<div class="price" data-i18n="tierFreePrice">\$0</div>',
    html
)

replacements = {
    'en': {
        'tierFreePrice': '$0'
    },
    'tr': {
        'tierFreePrice': '$0'
    },
    'ar': {
        'tierFreePrice': '$0'
    },
    'fr': {
        'tierFreePrice': '0 €'
    },
    'es': {
        'tierFreePrice': '0 €'
    },
    'de': {
        'tierFreePrice': '0 €'
    },
    'zh': {
        'tierFreePrice': '￥0'
    },
    'ja': {
        'tierFreePrice': '￥0'
    }
}

for lang, repls in replacements.items():
    pattern = rf"(?<=\n) *\"?{lang}\"?: {{\n(.*?)(?=\n *\}},)"
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        print(f"Could not find block for {lang}")
        continue
    
    current_chunk = match.group(1)
    new_chunk_lines = []
    
    for line in current_chunk.split('\n'):
        # Parse key
        key_match = re.search(r'^\s*"?([a-zA-Z0-9_]+)"?:\s*".*",?$', line)
        if key_match:
            key = key_match.group(1)
            if key in repls:
                has_comma = line.endswith(',')
                indent = re.match(r'^(\s*)', line).group(1)
                key_has_quotes = '"' + key + '"' in line
                key_str = f'"{key}"' if key_has_quotes else key
                # Need to escape double quotes in the value if any, but none here
                new_line = f'{indent}{key_str}: "{repls[key]}"' + (',' if has_comma else '')
                new_chunk_lines.append(new_line)
                repls[key] = None
            else:
                new_chunk_lines.append(line)
        else:
            new_chunk_lines.append(line)
            
    for key, val in repls.items():
        if val is not None:
            if len(new_chunk_lines) > 0 and not new_chunk_lines[-1].endswith(','):
                new_chunk_lines[-1] += ','
            new_chunk_lines.append(f'                {key}: "{val}",')

    if new_chunk_lines[-1].endswith(','):
        new_chunk_lines[-1] = new_chunk_lines[-1][:-1]

    new_chunk = '\n'.join(new_chunk_lines)
    html = html.replace(current_chunk, new_chunk)

# Fix backslashes in HTML replacement
html = html.replace(r'\$0', '$0')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("All done!")
