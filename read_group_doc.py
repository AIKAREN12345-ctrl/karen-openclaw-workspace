from docx import Document

doc = Document('C:/Users/Karen/.openclaw/media/inbound/file_206---fe30928b-1115-4d6b-99a2-1a454a28a73c.docx')
with open('group_work.txt', 'w', encoding='utf-8') as f:
    for para in doc.paragraphs:
        f.write(para.text + '\n')