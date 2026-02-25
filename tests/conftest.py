import pytest
import tempfile
import shutil
from unittest.mock import Mock, MagicMock


@pytest.fixture
def temp_test_dir():
    test_dir = tempfile.mkdtemp()
    yield test_dir
    shutil.rmtree(test_dir)


@pytest.fixture
def mock_chroma_collection():
    collection = Mock()
    collection.add = Mock()
    collection.query = Mock(return_value={
        'ids': [['doc1', 'doc2']],
        'documents': [['文档内容1', '文档内容2']],
        'metadatas': [[{'source': 'test1.txt'}, {'source': 'test2.txt'}]],
        'distances': [[0.1, 0.2]]
    })
    collection.get = Mock(return_value={
        'ids': ['doc1'],
        'documents': ['文档内容1'],
        'metadatas': [{'source': 'test1.txt'}]
    })
    collection.delete = Mock()
    collection.count = Mock(return_value=2)
    return collection


@pytest.fixture
def mock_chroma_client(mock_chroma_collection):
    client = Mock()
    client.get_or_create_collection = Mock(return_value=mock_chroma_collection)
    client.create_collection = Mock(return_value=mock_chroma_collection)
    client.get_collection = Mock(return_value=mock_chroma_collection)
    client.delete_collection = Mock()
    client.list_collections = Mock(return_value=[])
    return client


@pytest.fixture
def mock_ollama_embedding_function():
    def mock_embed(texts):
        if isinstance(texts, str):
            texts = [texts]
        return [[0.1] * 768 for _ in texts]
    
    ef = Mock()
    ef.__call__ = mock_embed
    ef.embed = mock_embed
    return ef
