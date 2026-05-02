import re

# Read diff file
with open('diff_utf8.txt', 'r', encoding='utf-8') as f:
    diff_text = f.read()

diff_text = re.sub(r'^\d+:\s', '', diff_text, flags=re.MULTILINE)

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# For ja, let's just find the block manually
pattern = r"ja: \{\n(.*?)zh: \{"
match = re.search(pattern, diff_text, re.DOTALL)
if match:
    chunk = match.group(1)
    # remove the trailing },
    chunk = re.sub(r'\},?\s*$', '', chunk)
    after_lines = []
    for line in chunk.split('\n'):
        if line.startswith('+'):
            after_lines.append(line[1:])
        elif not line.startswith('-'):
            after_lines.append(line[1:] if line.startswith(' ') else line)
            
    updated_keys = {}
    for line in after_lines:
        m = re.search(r'^\s*"?([a-zA-Z0-9_]+)"?:\s*"(.*)",?$', line)
        if m:
            key, val = m.groups()
            if val.endswith('",'): val = val[:-2]
            elif val.endswith('"'): val = val[:-1]
            updated_keys[key] = val

    updated_keys.pop('heroTitle', None)
    updated_keys.pop('heroSub', None)
    deleted_keys = ['priceMonthly', 'priceYearly', 'price3Year', 'tagBestValue', 'amtMonthly', 'amtYearlyOld', 'amtYearlyMain', 'amt3YearOld', 'amt3YearMain', 'planProPrice', 'planProBillingNote']

    html_pattern = r"(?<=\n)             ja: \{\n(.*?)(?=\n             \},)"
    html_match = re.search(html_pattern, html, re.DOTALL)
    if html_match:
        current_chunk = html_match.group(1)
        new_chunk_lines = []
        for line in current_chunk.split('\n'):
            km = re.search(r'^\s*"?([a-zA-Z0-9_]+)"?:\s*".*",?$', line)
            if km:
                key = km.group(1)
                if key in deleted_keys: continue
                if key in updated_keys:
                    has_comma = line.endswith(',')
                    indent = re.match(r'^(\s*)', line).group(1)
                    key_has_quotes = '"' + key + '"' in line
                    key_str = f'"{key}"' if key_has_quotes else key
                    new_line = f'{indent}{key_str}: "{updated_keys[key]}"' + (',' if has_comma else '')
                    new_chunk_lines.append(new_line)
                    updated_keys[key] = None
                else:
                    new_chunk_lines.append(line)
            else:
                new_chunk_lines.append(line)
        for key, val in updated_keys.items():
            if val is not None:
                if len(new_chunk_lines) > 0 and not new_chunk_lines[-1].endswith(','):
                    new_chunk_lines[-1] += ','
                new_chunk_lines.append(f'                {key}: "{val}",')
        if new_chunk_lines[-1].endswith(','):
            new_chunk_lines[-1] = new_chunk_lines[-1][:-1]
            
        new_chunk = '\n'.join(new_chunk_lines)
        html = html.replace(current_chunk, new_chunk)
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Fixed ja!")
    else:
        print("html match failed")
else:
    print("diff match failed")
