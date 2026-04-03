import re

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
        'cardLiveCollab': 'Live Collab'
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
        'cardLiveCollab': 'Canlı Çalışma'
    },
    'ar': {
        'cardAISuggestions': 'اقتراحات الذكاء الاصطناعي',
        'cardOneClickSave': 'حفظ بنقرة واحدة',
        'cardSmartHighlight': 'تظليل ذكي',
        'cardPdfChat': 'دردشة PDF',
        'cardAutoSummary': 'تلخيص آلي',
        'cardAnnotation': 'تعليق توضيحي',
        'cardDataProcessing': 'معالجة البيانات',
        'cardCodeGen': 'توليد الكود',
        'cardConceptExtract': 'استخراج المفاهيم',
        'cardDrafting': 'صياغة',
        'cardAutoFormat': 'تنسيق آلي',
        'cardMsWordAssistant': 'مساعد MS Word',
        'cardLatexEditor': 'محرر LaTeX',
        'cardLiveCollab': 'تعاون مباشر'
    },
    'de': {
        'cardAISuggestions': 'KI-Vorschläge',
        'cardOneClickSave': 'Ein-Klick Speichern',
        'cardSmartHighlight': 'Smartes Markieren',
        'cardPdfChat': 'PDF-Chat',
        'cardAutoSummary': 'Auto-Zusammenfassung',
        'cardAnnotation': 'Anmerkung',
        'cardDataProcessing': 'Datenverarbeitung',
        'cardCodeGen': 'Code-Gen',
        'cardConceptExtract': 'Konzept-Extraktion',
        'cardDrafting': 'Entwurf',
        'cardAutoFormat': 'Auto-Formatierung',
        'cardMsWordAssistant': 'MS Word Assistent',
        'cardLatexEditor': 'LaTeX-Editor',
        'cardLiveCollab': 'Live-Zusammenarbeit'
    },
    'es': {
        'cardAISuggestions': 'Sugerencias de IA',
        'cardOneClickSave': 'Guardar con un clic',
        'cardSmartHighlight': 'Resaltado Inteligente',
        'cardPdfChat': 'Chat de PDF',
        'cardAutoSummary': 'Auto-Resumen',
        'cardAnnotation': 'Anotación',
        'cardDataProcessing': 'Proces. de Datos',
        'cardCodeGen': 'Gen. de Código',
        'cardConceptExtract': 'Extrac. de Conceptos',
        'cardDrafting': 'Borrador',
        'cardAutoFormat': 'Auto-Formato',
        'cardMsWordAssistant': 'Asistente MS Word',
        'cardLatexEditor': 'Editor LaTeX',
        'cardLiveCollab': 'Colab. en Vivo'
    },
    'fr': {
        'cardAISuggestions': 'Suggestions IA',
        'cardOneClickSave': 'Sauvegarde en 1 Clic',
        'cardSmartHighlight': 'Surlignage Intel.',
        'cardPdfChat': 'Chat PDF',
        'cardAutoSummary': 'Auto-Résumé',
        'cardAnnotation': 'Annotation',
        'cardDataProcessing': 'Traitement Data',
        'cardCodeGen': 'Gén. Code',
        'cardConceptExtract': 'Extrac. Concept',
        'cardDrafting': 'Rédaction',
        'cardAutoFormat': 'Formatage Auto',
        'cardMsWordAssistant': 'Assistant MS Word',
        'cardLatexEditor': 'Éditeur LaTeX',
        'cardLiveCollab': 'Collab. Direct'
    },
    'ja': {
        'cardAISuggestions': 'AIの提案',
        'cardOneClickSave': 'ワンクリック保存',
        'cardSmartHighlight': 'スマートハイライト',
        'cardPdfChat': 'PDFチャット',
        'cardAutoSummary': '自動要約',
        'cardAnnotation': '注釈',
        'cardDataProcessing': 'データ処理',
        'cardCodeGen': 'コード生成',
        'cardConceptExtract': '概念抽出',
        'cardDrafting': '下書き',
        'cardAutoFormat': '自動フォーマット',
        'cardMsWordAssistant': 'MS Wordアシスタント',
        'cardLatexEditor': 'LaTeXエディタ',
        'cardLiveCollab': 'リアルタイム共同作業'
    },
    'zh': {
        'cardAISuggestions': 'AI 建议',
        'cardOneClickSave': '一键保存',
        'cardSmartHighlight': '智能高亮',
        'cardPdfChat': 'PDF 聊天',
        'cardAutoSummary': '自动摘要',
        'cardAnnotation': '批注',
        'cardDataProcessing': '数据处理',
        'cardCodeGen': '代码生成',
        'cardConceptExtract': '概念提取',
        'cardDrafting': '起草',
        'cardAutoFormat': '自动排版',
        'cardMsWordAssistant': 'MS Word 助手',
        'cardLatexEditor': 'LaTeX 编辑器',
        'cardLiveCollab': '实时协作'
    }
}

html_file = r'd:\\RcubeTech\\rcubetech.github.io\\index.html'

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the HTML labels with data-i18n tags
html_replacements = {
    '<span class="card-title">AI Suggestions</span>': '<span class="card-title" data-i18n="cardAISuggestions">AI Suggestions</span>',
    '<span class="card-title">One-Click Save</span>': '<span class="card-title" data-i18n="cardOneClickSave">One-Click Save</span>',
    '<span class="card-title">Smart Highlight</span>': '<span class="card-title" data-i18n="cardSmartHighlight">Smart Highlight</span>',
    '<span class="card-title">PDF Chat</span>': '<span class="card-title" data-i18n="cardPdfChat">PDF Chat</span>',
    '<span class="card-title">Auto-Summary</span>': '<span class="card-title" data-i18n="cardAutoSummary">Auto-Summary</span>',
    '<span class="card-title">Annotation</span>': '<span class="card-title" data-i18n="cardAnnotation">Annotation</span>',
    '<span class="card-title">Data Processing</span>': '<span class="card-title" data-i18n="cardDataProcessing">Data Processing</span>',
    '<span class="card-title">Code Gen</span>': '<span class="card-title" data-i18n="cardCodeGen">Code Gen</span>',
    '<span class="card-title">Concept Extract</span>': '<span class="card-title" data-i18n="cardConceptExtract">Concept Extract</span>',
    '<span class="card-title">Drafting</span>': '<span class="card-title" data-i18n="cardDrafting">Drafting</span>',
    '<span class="card-title">Auto-Format</span>': '<span class="card-title" data-i18n="cardAutoFormat">Auto-Format</span>',
    '<span class="card-title">MS Word Assistant</span>': '<span class="card-title" data-i18n="cardMsWordAssistant">MS Word Assistant</span>',
    '<span class="card-title">LaTeX Editor</span>': '<span class="card-title" data-i18n="cardLatexEditor">LaTeX Editor</span>',
    '<span class="card-title">Live Collab</span>': '<span class="card-title" data-i18n="cardLiveCollab">Live Collab</span>'
}

for old, new in html_replacements.items():
    content = content.replace(old, new)

# 2. Inject the translations into the javascript dictionary
# We'll look for blocks like `en: {` or `"en": {`
# and insert our new pairs right after the opening brace.

for lang, trans_dict in new_translations.items():
    # Format the additions
    additions = "\n                " + ",\n                ".join([f'"{k}": "{v}"' for k, v in trans_dict.items()]) + ","
    
    # Try different regex for finding the language block
    pattern1 = rf'(\b{lang}\b:\s*{{)'
    pattern2 = rf'("{lang}":\s*{{)'
    
    if re.search(pattern1, content):
        content = re.sub(pattern1, r'\1' + additions, content, count=1)
    elif re.search(pattern2, content):
        content = re.sub(pattern2, r'\1' + additions, content, count=1)
    else:
        print(f"Warning: Could not find language block for {lang}")

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done updating translations.")
