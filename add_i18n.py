import re
import os

# Dictionary of translations to add
new_translations = {
    'en': {
        'cardAISuggestions': 'AI Suggestions',
        'cardOneClickSave': 'One-Click Save',
        'cardSmartHighlight': 'Smart Highlight',
        'cardPdfChat': 'PDF Chat',
        'cardAutoSummary': 'Auto-Summary',
        'cardAnnotation': 'Annotation',
        'cardDataProcessing': 'Data Processing',
        'cardCodeGen': 'Code Gen',
        'cardConceptExtract': 'Concept Extract',
        'cardDrafting': 'Drafting',
        'cardAutoFormat': 'Auto-Format',
        'cardMsWordAssistant': 'MS Word Assistant',
        'cardLatexEditor': 'LaTeX Editor',
        'cardLiveCollab': 'Live Collab',
        'orbitPdf': 'PDF Reader',
        'orbitSearch': 'Literature Search',
        'orbitEditor': 'Smart Editor',
        'orbitAI': 'AI Tools',
        'btnSending': 'Sending...',
        'btnSent': 'Sent!',
        'btnError': 'Error!',
        'footerRights': '&copy; 2026 ResearchCube. All rights reserved.',
        'footerDevelopedBy': 'Developed by <strong>rcubetech</strong>',
        'footerFollowUs': 'Follow us for updates'
    },
    'tr': {
        'cardAISuggestions': 'Yapay Zeka Önerileri',
        'cardOneClickSave': 'Tek Tıkla Kaydet',
        'cardSmartHighlight': 'Akıllı Vurgu',
        'cardPdfChat': 'PDF Sohbeti',
        'cardAutoSummary': 'Oto-Özet',
        'cardAnnotation': 'Not Alma',
        'cardDataProcessing': 'Veri İşleme',
        'cardCodeGen': 'Kod Üretimi',
        'cardConceptExtract': 'Kavram Çıkarımı',
        'cardDrafting': 'Taslak Hazırlama',
        'cardAutoFormat': 'Oto-Biçimlendirme',
        'cardMsWordAssistant': 'MS Word Asistanı',
        'cardLatexEditor': 'LaTeX Editörü',
        'cardLiveCollab': 'Canlı Çalışma',
        'orbitPdf': 'PDF Okuyucu',
        'orbitSearch': 'Literatür Taraması',
        'orbitEditor': 'Akıllı Editör',
        'orbitAI': 'Yapay Zeka Araçları',
        'btnSending': 'Gönderiliyor...',
        'btnSent': 'Gönderildi!',
        'btnError': 'Hata Oluştu!',
        'footerRights': '&copy; 2026 ResearchCube. Tüm hakları saklıdır.',
        'footerDevelopedBy': '<strong>rcubetech</strong> tarafından geliştirilmiştir',
        'footerFollowUs': 'Güncellemeler için bizi takip edin'
    },
    'ar': {
        'footerRights': '&copy; 2026 ResearchCube. جميع الحقوق محفوظة.',
        'footerDevelopedBy': 'تم التطوير بواسطة <strong>rcubetech</strong>',
        'footerFollowUs': 'تابعنا للحصول على التحديثات'
    },
    'de': {
        'footerRights': '&copy; 2026 ResearchCube. Alle Rechte vorbehalten.',
        'footerDevelopedBy': 'Entwickelt von <strong>rcubetech</strong>',
        'footerFollowUs': 'Folgen Sie uns für Updates'
    },
    'es': {
        'footerRights': '&copy; 2026 ResearchCube. Todos los derechos reservados.',
        'footerDevelopedBy': 'Desarrollado por <strong>rcubetech</strong>',
        'footerFollowUs': 'Síguenos para actualizaciones'
    },
    'fr': {
        'footerRights': '&copy; 2026 ResearchCube. Tous droits réservés.',
        'footerDevelopedBy': 'Développé par <strong>rcubetech</strong>',
        'footerFollowUs': 'Suivez-nous pour les mises à jour'
    },
    'ja': {
        'footerRights': '&copy; 2026 ResearchCube. All rights reserved.',
        'footerDevelopedBy': 'Developed by <strong>rcubetech</strong>',
        'footerFollowUs': '最新情報をフォローする'
    },
    'zh': {
        'footerRights': '&copy; 2026 ResearchCube. 保留所有权利',
        'footerDevelopedBy': '由 <strong>rcubetech</strong> 开发',
        'footerFollowUs': '关注我们的动态'
    }
}

html_file = r'd:\RcubeTech\rcubetech.github.io\index.html'

if not os.path.exists(html_file):
    print(f"Error: {html_file} not found.")
    exit(1)

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the HTML labels with data-i18n tags if not already present
html_replacements = {
    'AI Suggestions': 'cardAISuggestions',
    'One-Click Save': 'cardOneClickSave',
    'Smart Highlight': 'cardSmartHighlight',
    'PDF Chat': 'cardPdfChat',
    'Auto-Summary': 'cardAutoSummary',
    'Annotation': 'cardAnnotation',
    'Data Processing': 'cardDataProcessing',
    'Code Gen': 'cardCodeGen',
    'Concept Extract': 'cardConceptExtract',
    'Drafting': 'cardDrafting',
    'Auto-Format': 'cardAutoFormat',
    'MS Word Assistant': 'cardMsWordAssistant',
    'LaTeX Editor': 'cardLatexEditor',
    'Live Collab': 'cardLiveCollab'
}

for text, key in html_replacements.items():
    # Only replace if it doesn't already have data-i18n
    pattern = rf'<span class="card-title">{text}</span>'
    replacement = f'<span class="card-title" data-i18n="{key}">{text}</span>'
    content = content.replace(pattern, replacement)

# 2. Inject the translations into the javascript dictionary
# We'll look for blocks like `en: {` or `"en": {`
# and insert only MISSING pairs.

for lang, trans_dict in new_translations.items():
    # Find the language block
    lang_pattern = rf'(\b{lang}\b:?\s*{{)'
    match = re.search(lang_pattern, content)
    
    if match:
        start_idx = match.end()
        # Find end of block (assuming no nested braces)
        end_idx = content.find('}', start_idx)
        if end_idx != -1:
            body = content[start_idx:end_idx]
            
            # Check which keys are missing
            additions = []
            for k, v in trans_dict.items():
                if f'"{k}":' not in body and f"'{k}':" not in body:
                    additions.append(f'                "{k}": "{v}"')
            
            if additions:
                new_body = body.rstrip()
                if not new_body.endswith(',') and new_body.strip():
                    new_body += ','
                new_body += '\n' + ',\n'.join(additions) + ','
                content = content[:start_idx] + new_body + content[end_idx:]
                print(f"Added {len(additions)} keys to {lang}")
            else:
                print(f"No keys to add for {lang}")
    else:
        print(f"Warning: Could not find language block for {lang}")

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done updating translations.")
