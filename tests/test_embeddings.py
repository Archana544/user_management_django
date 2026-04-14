# tests/test_embeddings.py

from unittest.mock import patch
from utils.vector_store  import get_embedding


@patch("utils.vector_store.client.models.embed_content")
def test_get_embedding(mock_embed):
    mock_embed.return_value.embeddings = [
        type("obj", (object,), {"values": [0.1] * 800})
    ]

    result = get_embedding(["hello world"])

    assert len(result) == 1
    assert len(result[0]) == 768
    assert isinstance(result[0][0], float)