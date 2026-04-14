# tests/test_search.py

from unittest.mock import patch, MagicMock
from utils.vector_store import search_similar_chunks


@patch("utils.vector_store.get_embedding")
@patch("utils.vector_store.get_db_connection")
def test_search_returns_results(mock_db, mock_embedding):
    mock_embedding.return_value = [[0.1] * 768]

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock DB responses
    mock_cursor.fetchone.side_effect = [(5,)]  # total chunks
    mock_cursor.fetchall.return_value = [
        ("Sample chunk text", 0.1)
    ]

    results = search_similar_chunks("test query")

    assert len(results) == 1
    assert "Sample chunk" in results[0]