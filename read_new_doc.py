from docx import Document

doc = Document('C:/Users/Karen/.openclaw/media/inbound/file_3---eab2fb3c-229f-48ca-b93a-5d58224c7bd9.docx')
with open('new_doc_content.txt', 'w', encoding='utf-8') as f:
    for para in doc.paragraphs:
        f.write(para.text + '\n')