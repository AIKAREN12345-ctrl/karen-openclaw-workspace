from docx import Document
doc = Document('C:/Users/Karen/.openclaw/media/inbound/file_201---7a35459d-e199-4c0d-89e3-5f1a0460a4a2.docx')
with open('course_content.txt', 'w', encoding='utf-8') as f:
    for para in doc.paragraphs:
        f.write(para.text + '\n')