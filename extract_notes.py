import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import re

def extract_text_from_pptx(pptx_path):
    """Extract text from PowerPoint file"""
    text_content = []
    
    try:
        with zipfile.ZipFile(pptx_path, 'r') as z:
            # Get all slide files
            slide_files = sorted([f for f in z.namelist() 
                                if f.startswith('ppt/slides/slide') and f.endswith('.xml')])
            
            for slide_file in slide_files:
                try:
                    slide_xml = z.read(slide_file).decode('utf-8', errors='ignore')
                    
                    # Extract text between <a:t> tags (PowerPoint text elements)
                    text_matches = re.findall(r'<a:t[^>]*>([^<]+)</a:t>', slide_xml)
                    
                    if text_matches:
                        slide_text = ' '.join(text_matches)
                        if slide_text.strip():
                            text_content.append(f"=== Slide {slide_file} ===")
                            text_content.append(slide_text)
                            text_content.append("")
                except Exception as e:
                    text_content.append(f"Error reading {slide_file}: {e}")
                    
    except Exception as e:
        text_content.append(f"Error opening PPTX: {e}")
    
    return '\n'.join(text_content)

def extract_text_from_docx(docx_path):
    """Extract text from Word document"""
    text_content = []
    
    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            # Read document.xml
            if 'word/document.xml' in z.namelist():
                doc_xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
                
                # Extract text between <w:t> tags (Word text elements)
                text_matches = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', doc_xml)
                
                if text_matches:
                    text_content.append(f"=== {Path(docx_path).name} ===")
                    text_content.append(' '.join(text_matches))
                    
    except Exception as e:
        text_content.append(f"Error opening DOCX: {e}")
    
    return '\n'.join(text_content)

# Process files
pptx_path = r'C:\Users\Karen\.openclaw\media\inbound\file_171---e50fdf3d-d783-4e73-a98b-a23b74e58b37.pptx'
docx1_path = r'C:\Users\Karen\.openclaw\media\inbound\file_172---7ea2f5fc-f1dd-4187-973b-bb66d2c6462c.docx'
docx2_path = r'C:\Users\Karen\.openclaw\media\inbound\file_173---3d59b74e-e54e-4376-8725-8335efdb52bf.docx'

print("=" * 60)
print("EXTRACTING FROM POWERPOINT")
print("=" * 60)
pptx_text = extract_text_from_pptx(pptx_path)
print(pptx_text[:10000] if len(pptx_text) > 10000 else pptx_text)

print("\n" + "=" * 60)
print("EXTRACTING FROM WORD DOC 1")
print("=" * 60)
docx1_text = extract_text_from_docx(docx1_path)
print(docx1_text[:5000] if len(docx1_text) > 5000 else docx1_text)

print("\n" + "=" * 60)
print("EXTRACTING FROM WORD DOC 2")
print("=" * 60)
docx2_text = extract_text_from_docx(docx2_path)
print(docx2_text[:5000] if len(docx2_text) > 5000 else docx2_text)

# Save all extracted text to a file
output_path = r'C:\Users\Karen\.openclaw\workspace\extracted_notes.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("ORGANIZATIONAL CULTURE - EXTRACTED NOTES\n")
    f.write("=" * 60 + "\n\n")
    f.write(pptx_text + "\n\n")
    f.write(docx1_text + "\n\n")
    f.write(docx2_text + "\n")

print(f"\n\nSaved all extracted content to: {output_path}")
