import csv
from pypdf import PdfReader 

def extract_pdf_text(file_path: str) -> str:
    """
    Extract text from PDF.
    pypdf is more reliable than PyPDF2 for modern PDFs.
    """
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()


def parse_csv(file_path: str) -> str:
    extracted_data = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            extracted_data.append(str(row))
    return "\n".join(extracted_data)