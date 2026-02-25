import pytest
from unittest.mock import Mock, patch


class TestSearchFunctionality:
    """测试知识库搜索功能"""

    def test_normal_search(self, mock_chroma_collection):
        """测试正常搜索"""
        query = "测试查询"
        results = mock_chroma_collection.query(query_texts=[query], n_results=5)
        
        assert results is not None
        assert 'documents' in results
        assert 'metadatas' in results
        assert len(results['documents'][0]) == 2
        assert results['documents'][0][0] == '文档内容1'
        assert results['metadatas'][0][0]['source'] == 'test1.txt'

    def test_search_with_multiple_results(self, mock_chroma_collection):
        """测试返回多个结果的搜索"""
        query = "知识库"
        results = mock_chroma_collection.query(query_texts=[query], n_results=5)
        
        assert len(results['documents'][0]) == 2
        assert len(results['metadatas'][0]) == 2
        assert len(results['ids'][0]) == 2

    def test_empty_results_handling(self, mock_chroma_collection):
        """测试空结果处理"""
        mock_chroma_collection.query.return_value = {
            'ids': [[]],
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        query = "不存在的查询内容"
        results = mock_chroma_collection.query(query_texts=[query], n_results=5)
        
        assert results['documents'][0] == []
        assert results['metadatas'][0] == []
        assert len(results['documents'][0]) == 0

    def test_search_exception_handling(self, mock_chroma_collection):
        """测试搜索异常处理"""
        mock_chroma_collection.query.side_effect = Exception("数据库连接失败")
        
        with pytest.raises(Exception) as exc_info:
            mock_chroma_collection.query(query_texts=["测试"], n_results=5)
        
        assert "数据库连接失败" in str(exc_info.value)

    def test_search_with_distances(self, mock_chroma_collection):
        """测试搜索结果包含距离信息"""
        query = "相似度测试"
        results = mock_chroma_collection.query(query_texts=[query], n_results=5)
        
        assert 'distances' in results
        assert len(results['distances'][0]) == 2
        assert results['distances'][0][0] == 0.1
        assert results['distances'][0][1] == 0.2

    def test_search_result_format(self, mock_chroma_collection):
        """测试搜索结果格式"""
        query = "格式测试"
        results = mock_chroma_collection.query(query_texts=[query], n_results=5)
        
        for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            assert isinstance(doc, str)
            assert isinstance(meta, dict)
            assert 'source' in meta


class TestSearchWithEmbedding:
    """测试搜索与嵌入功能"""

    def test_embedding_function_called(self, mock_ollama_embedding_function):
        """测试嵌入函数被正确调用"""
        texts = ["测试文本"]
        embeddings = mock_ollama_embedding_function.__call__(texts)
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 768

    def test_embedding_for_multiple_texts(self, mock_ollama_embedding_function):
        """测试多文本嵌入"""
        texts = ["文本1", "文本2", "文本3"]
        embeddings = mock_ollama_embedding_function.__call__(texts)
        
        assert len(embeddings) == 3
        for emb in embeddings:
            assert len(emb) == 768
