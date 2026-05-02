import re

# Read diff file
with open('diff_utf8.txt', 'r', encoding='utf-8') as f:
    diff_text = f.read()

# Remove line numbers from diff
diff_text = re.sub(r'^\d+:\s', '', diff_text, flags=re.MULTILINE)

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

def get_after_lines(lang):
    pattern = rf"(?<=\n)            {lang}: {{\n(.*?)(?=\n            }},)"
    match = re.search(pattern, diff_text, re.DOTALL)
    if not match:
        # try 13 spaces
        pattern = rf"(?<=\n)             {lang}: {{\n(.*?)(?=\n             }},)"
        match = re.search(pattern, diff_text, re.DOTALL)
    if not match: return None
    
    chunk = match.group(1)
    after_lines = []
    for line in chunk.split('\n'):
        if line.startswith('+'):
            after_lines.append(line[1:])
        elif not line.startswith('-'):
            after_lines.append(line[1:] if line.startswith(' ') else line)
    return after_lines

for lang in ['ar', 'fr', 'es', 'de', 'ja', 'zh']:
    after_lines = get_after_lines(lang)
    if not after_lines: 
        print(f"Could not find diff block for {lang}")
        continue
    
    # Create a dictionary of the updated keys from diff
    updated_keys = {}
    for line in after_lines:
        # We need to handle values that might contain escaped quotes \"
        # A simple regex for this:
        match = re.search(r'^\s*"?([a-zA-Z0-9_]+)"?:\s*"(.*)",?$', line)
        if match:
            key, val = match.groups()
            # If the regex greedily matched the trailing quote and comma:
            if val.endswith('",'):
                val = val[:-2]
            elif val.endswith('"'):
                val = val[:-1]
            updated_keys[key] = val

    # Do not change heroTitle and heroSub
    updated_keys.pop('heroTitle', None)
    updated_keys.pop('heroSub', None)
    
    deleted_keys = ['priceMonthly', 'priceYearly', 'price3Year', 'tagBestValue', 'amtMonthly', 'amtYearlyOld', 'amtYearlyMain', 'amt3YearOld', 'amt3YearMain', 'planProPrice', 'planProBillingNote']

    html_pattern = rf"(?<=\n)            {lang}: {{\n(.*?)(?=\n            }},)"
    html_match = re.search(html_pattern, html, re.DOTALL)
    if not html_match:
        html_pattern = rf"(?<=\n)             {lang}: {{\n(.*?)(?=\n             }},)"
        html_match = re.search(html_pattern, html, re.DOTALL)
    
    if not html_match: 
        print(f"Could not find HTML block for {lang}")
        continue
    
    current_chunk = html_match.group(1)
    new_chunk_lines = []
    
    for line in current_chunk.split('\n'):
        key_match = re.search(r'^\s*"?([a-zA-Z0-9_]+)"?:\s*".*",?$', line)
        if key_match:
            key = key_match.group(1)
            if key in deleted_keys:
                continue # Skip deleted keys
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

print("HTML updated successfully.")
