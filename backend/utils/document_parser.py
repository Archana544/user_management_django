import csv
from PyPDF2 import PdfReader


def extract_pdf_text(file_path):
    text = ""
    reader = PdfReader(file_path)

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    return text


def parse_csv(file_path):
    extracted_data = []

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            extracted_data.append(str(row))

    return "\n".join(extracted_data)