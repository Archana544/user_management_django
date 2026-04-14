# tests/test_file_processing.py

import tempfile
import csv
from utils.document_parser import parse_csv


def test_parse_csv():
    with tempfile.NamedTemporaryFile(mode="w+", newline="", delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age"])
        writer.writeheader()
        writer.writerow({"name": "Archana", "age": "25"})
        file_path = f.name

    result = parse_csv(file_path)

    assert "Archana" in result