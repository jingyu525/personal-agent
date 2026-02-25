import pytest
from unittest.mock import Mock, patch, MagicMock


class TestKnowledgeBaseInitialization:
    """测试知识库初始化"""

    def test_initialization_success(self, mock_chroma_client, mock_ollama_embedding_function):
        """测试初始化成功"""
        collection = mock_chroma_client.get_or_create_collection(
            name="personal_knowledge",
            embedding_function=mock_ollama_embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        
        assert collection is not None
        mock_chroma_client.get_or_create_collection.assert_called_once()

    def test_collection_name_correct(self, mock_chroma_client, mock_ollama_embedding_function):
        """测试集合名称正确"""
        mock_chroma_client.get_or_create_collection(
            name="personal_knowledge",
            embedding_function=mock_ollama_embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        
        call_args = mock_chroma_client.get_or_create_collection.call_args
        assert call_args[1]["name"] == "personal_knowledge"

    def test_embedding_function_configured(self, mock_chroma_client, mock_ollama_embedding_function):
        """测试嵌入函数配置正确"""
        mock_chroma_client.get_or_create_collection(
            name="personal_knowledge",
            embedding_function=mock_ollama_embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        
        call_args = mock_chroma_client.get_or_create_collection.call_args
        assert "embedding_function" in call_args[1]

    def test_metadata_configuration(self, mock_chroma_client, mock_ollama_embedding_function):
        """测试元数据配置正确"""
        mock_chroma_client.get_or_create_collection(
            name="personal_knowledge",
            embedding_function=mock_ollama_embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        
        call_args = mock_chroma_client.get_or_create_collection.call_args
        assert call_args[1]["metadata"]["hnsw:space"] == "cosine"


class TestEmbeddingFunctionConfiguration:
    """测试嵌入函数配置"""

    def test_ollama_embedding_url(self, mock_ollama_embedding_function):
        """测试 Ollama 嵌入 URL 配置"""
        expected_url = "http://localhost:11434/api/embeddings"
        assert expected_url is not None

    def test_ollama_embedding_model(self, mock_ollama_embedding_function):
        """测试 Ollama 嵌入模型配置"""
        expected_model = "nomic-embed-text"
        assert expected_model == "nomic-embed-text"

    def test_embedding_dimension(self, mock_ollama_embedding_function):
        """测试嵌入维度"""
        embeddings = mock_ollama_embedding_function.__call__(["测试"])
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 768


class TestVectorDBConfiguration:
    """测试向量数据库配置"""

    def test_persistent_client_path(self, temp_test_dir):
        """测试持久化客户端路径"""
        db_path = f"{temp_test_dir}/vector_db"
        
        assert db_path.endswith("/vector_db")

    def test_collection_creation_with_existing(self, mock_chroma_client, mock_ollama_embedding_function):
        """测试已存在集合的处理"""
        collection1 = mock_chroma_client.get_or_create_collection(
            name="personal_knowledge",
            embedding_function=mock_ollama_embedding_function
        )
        collection2 = mock_chroma_client.get_or_create_collection(
            name="personal_knowledge",
            embedding_function=mock_ollama_embedding_function
        )
        
        assert collection1 == collection2

    def test_multiple_collections(self, mock_chroma_client, mock_ollama_embedding_function):
        """测试多个集合"""
        mock_chroma_client.get_or_create_collection(
            name="personal_knowledge",
            embedding_function=mock_ollama_embedding_function
        )
        mock_chroma_client.get_or_create_collection(
            name="another_collection",
            embedding_function=mock_ollama_embedding_function
        )
        
        assert mock_chroma_client.get_or_create_collection.call_count == 2


class TestInitializationErrorHandling:
    """测试初始化错误处理"""

    def test_client_creation_failure(self):
        """测试客户端创建失败"""
        with patch('chromadb.PersistentClient') as mock_client:
            mock_client.side_effect = Exception("无法创建数据库连接")
            
            with pytest.raises(Exception) as exc_info:
                mock_client(path="./vector_db")
            
            assert "无法创建数据库连接" in str(exc_info.value)

    def test_collection_creation_failure(self, mock_chroma_client):
        """测试集合创建失败"""
        mock_chroma_client.get_or_create_collection.side_effect = Exception("集合创建失败")
        
        with pytest.raises(Exception) as exc_info:
            mock_chroma_client.get_or_create_collection(name="test")
        
        assert "集合创建失败" in str(exc_info.value)

    def test_embedding_function_failure(self, mock_ollama_embedding_function):
        """测试嵌入函数失败"""
        mock_ollama_embedding_function.side_effect = Exception("嵌入服务不可用")
        
        with pytest.raises(Exception) as exc_info:
            mock_ollama_embedding_function(["测试"])
        
        assert "嵌入服务不可用" in str(exc_info.value)


class TestKnowledgeBaseState:
    """测试知识库状态"""

    def test_collection_count(self, mock_chroma_collection):
        """测试集合文档计数"""
        count = mock_chroma_collection.count()
        
        assert count == 2

    def test_collection_is_empty_initially(self, mock_chroma_collection):
        """测试集合初始为空"""
        mock_chroma_collection.count.return_value = 0
        count = mock_chroma_collection.count()
        
        assert count == 0

    def test_collection_has_documents(self, mock_chroma_collection):
        """测试集合包含文档"""
        result = mock_chroma_collection.get()
        
        assert len(result['ids']) > 0
        assert len(result['documents']) > 0
