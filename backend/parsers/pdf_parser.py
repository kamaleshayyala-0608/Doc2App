import fitz

def extract_pdf_text(file_path):
    text = ""

    doc = fitz.open(file_path)

    for page in doc:
        text += page.get_text()

    return text
