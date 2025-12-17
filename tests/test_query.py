from unittest.mock import patch
from src.query import embed_text
from types import SimpleNamespace

@patch("src.query.client")
def test_embed_text_mocked(mock_openai):
    test = "Sample text for embedding"
    item = SimpleNamespace(embedding=[0.1, 0.2, 0.3, 0.4])
    response = SimpleNamespace(data=[item])
    
    mock_openai.embeddings.create.return_value = response
    
    result = embed_text(test)
    
    assert result == response.data[0].embedding

    mock_openai.embeddings.create.assert_called_once_with(
        model="text-embedding-3-small",
        input=test
    )   