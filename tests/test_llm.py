# tests/test_llm.py

from unittest.mock import patch
from utils.llm_service import generate_answer


@patch("utils.llm_service.client.models.generate_answer")
def test_generate_answer(mock_generate):
    mock_generate.return_value.text = "This is a test answer"

    result = generate_answer("Test prompt")

    assert result == "This is a test answer"