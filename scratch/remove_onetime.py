import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace HTML line
html = re.sub(
    r'<div class="price" data-i18n="tierProPrice">\$49\.99<span> one-time</span></div>',
    r'<div class="price" data-i18n="tierProPrice">\$49.99</div>',
    html
)

replacements = {
    'en': {
        'cardPrivacyTitle': 'Full Ownership',
        'cardPrivacyDesc': 'You remain the sole owner of your research files.',
        'pricingTitle': 'Professional Plans',
        'pricingDesc': 'ResearchCube is built on a serverless architecture that drastically reduces operational costs—allowing us to offer premium features at an exceptional value.',
        'tierProPrice': '$49.99',
        'tierProSub': 'Premium access to all advanced academic features.'
    },
    'tr': {
        'cardPrivacyTitle': 'Tam Sahiplik',
        'cardPrivacyDesc': 'Araştırma dosyalarınızın ve verilerinizin tek sahibi sizsiniz.',
        'pricingTitle': 'Profesyonel Planlar',
        'pricingDesc': 'Sunucu maliyetlerini ortadan kaldırarak tasarrufun %100\'ünü size yansıtıyoruz. Uygun fiyatla premium özelliklere erişin.',
        'tierProPrice': '$49.99',
        'tierProSub': 'Tüm premium akademik özelliklere sınırsız erişim.'
    },
    'ar': {
        'cardPrivacyTitle': 'ملكية كاملة',
        'cardPrivacyDesc': 'أنت المالك الوحيد لملفات البحث الخاصة بك.',
        'pricingTitle': 'خطط احترافية',
        'pricingDesc': 'نوفر لك الميزات المتميزة بقيمة استثنائية بفضل البنية الخالية من الخوادم.',
        'tierProPrice': '$49.99',
        'tierProSub': 'وصول متميز إلى جميع الميزات الأكاديمية المتقدمة.'
    },
    'fr': {
        'cardPrivacyTitle': 'Pleine propriété',
        'cardPrivacyDesc': 'Vous restez le seul propriétaire de vos fichiers de recherche.',
        'pricingTitle': 'Plans Professionnels',
        'pricingDesc': 'ResearchCube est bâti sur une architecture sans serveur qui réduit les coûts - nous permettant d\'offrir le meilleur à un prix exceptionnel.',
        'tierProPrice': '49,99 $',
        'tierProSub': 'Accès premium à toutes les fonctionnalités avancées.'
    },
    'es': {
        'cardPrivacyTitle': 'Propiedad total',
        'cardPrivacyDesc': 'Sigues siendo el único dueño de tus archivos de investigación.',
        'pricingTitle': 'Planes Profesionales',
        'pricingDesc': 'ResearchCube se basa en una arquitectura sin servidor que reduce costes, permitiéndonos ofrecer un valor excepcional.',
        'tierProPrice': '49,99 $',
        'tierProSub': 'Acceso premium a todas las funciones avanzadas.'
    },
    'de': {
        'cardPrivacyTitle': 'Vollständiges Eigentum',
        'cardPrivacyDesc': 'Sie bleiben der alleinige Eigentümer Ihrer Forschungsdateien.',
        'pricingTitle': 'Professionelle Pläne',
        'pricingDesc': 'ResearchCube basiert auf einer serverlosen Architektur, die es uns ermöglicht, Premium-Funktionen zu einem außergewöhnlichen Preis anzubieten.',
        'tierProPrice': '49,99 $',
        'tierProSub': 'Premium-Zugang zu allen erweiterten akademischen Funktionen.'
    },
    'zh': {
        'cardPrivacyTitle': '完全所有权',
        'cardPrivacyDesc': '您始终是研究文件的唯一所有者。',
        'pricingTitle': '专业计划',
        'pricingDesc': 'ResearchCube 基于无服务器架构，从而能够以极高的性价比提供高级功能。',
        'tierProPrice': '$49.99',
        'tierProSub': '获得所有高级学术功能的专业权限。'
    },
    'ja': {
        'tierProPrice': '￥5,900',
        'tierProSub': 'すべての高度な学術機能へのプレミアムアクセス。'
    }
}

for lang, repls in replacements.items():
    # Find the language block
    # It might be `lang: {` or `"lang": {`
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

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("All done!")
