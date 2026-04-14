# tests/test_database.py

from unittest.mock import patch, MagicMock
from utils.vector_store import add_document_to_index


@patch("utils.vector_store.get_embedding")
@patch("utils.vector_store.get_db_connection")
def test_add_document_to_index(mock_db, mock_embedding):
    mock_embedding.return_value = [[0.1] * 768]

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    add_document_to_index(1, "This is a test document")

    assert mock_cursor.execute.called or mock_cursor.executemany.called
    assert mock_conn.commit.called