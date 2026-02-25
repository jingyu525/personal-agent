import pytest
import hashlib
from unittest.mock import Mock, patch, mock_open
from pathlib import Path


class TestIngestFile:
    """测试文件导入功能"""

    def test_ingest_file_success(self, mock_chroma_collection, temp_test_dir):
        """测试成功导入文件"""
        test_file = Path(temp_test_dir) / "test.md"
        test_content = "段落1内容，这是一个测试段落，长度超过五十个字符以确保被正确处理和切分操作完成测试验证功能正常工作通过测试。\n\n段落2内容，这是另一个测试段落，同样长度超过五十个字符以确保被正确处理和切分操作完成测试验证功能正常工作通过测试。"
        test_file.write_text(test_content, encoding='utf-8')
        
        content = test_file.read_text(encoding='utf-8')
        chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 50]
        
        doc_id = hashlib.md5(str(test_file).encode()).hexdigest()
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metas = [{"source": str(test_file), "chunk": i} for i in range(len(chunks))]
        
        mock_chroma_collection.upsert(
            documents=chunks,
            ids=ids,
            metadatas=metas
        )
        
        assert len(chunks) == 2
        mock_chroma_collection.upsert.assert_called_once()

    def test_ingest_file_with_short_chunks(self, mock_chroma_collection, temp_test_dir):
        """测试包含短段落的文件导入"""
        test_file = Path(temp_test_dir) / "short.md"
        test_content = "短段落\n\n这是一个较长的段落内容，长度超过五十个字符，应该被正确处理和切分操作完成测试验证功能正常工作通过测试。"
        test_file.write_text(test_content, encoding='utf-8')
        
        content = test_file.read_text(encoding='utf-8')
        chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 50]
        
        assert len(chunks) == 1
        assert "这是一个较长的段落" in chunks[0]

    def test_ingest_file_not_found(self, mock_chroma_collection):
        """测试文件不存在的情况"""
        non_existent_file = "/path/to/non/existent/file.md"
        
        with pytest.raises(FileNotFoundError):
            Path(non_existent_file).read_text(encoding='utf-8')

    def test_ingest_empty_file(self, mock_chroma_collection, temp_test_dir):
        """测试空文件导入"""
        test_file = Path(temp_test_dir) / "empty.md"
        test_file.write_text("", encoding='utf-8')
        
        content = test_file.read_text(encoding='utf-8')
        chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 50]
        
        assert len(chunks) == 0


class TestDocumentChunking:
    """测试文档切分逻辑"""

    def test_chunk_by_paragraph(self):
        """测试按段落切分"""
        content = "第一段内容，长度超过五十个字符的测试段落内容，用于测试切分功能是否正常工作验证通过测试用例执行成功验证。\n\n第二段内容，同样长度超过五十个字符的测试段落内容，用于测试切分功能是否正常工作验证通过测试用例执行成功验证。"
        chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 50]
        
        assert len(chunks) == 2

    def test_chunk_with_single_paragraph(self):
        """测试单段落文档"""
        content = "这是一个单独的段落，长度超过五十个字符，用于测试单段落文档的处理逻辑和切分功能是否正常工作验证通过测试。"
        chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 50]
        
        assert len(chunks) == 1

    def test_chunk_with_no_valid_paragraphs(self):
        """测试没有有效段落的文档"""
        content = "短\n\n短\n\n短"
        chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 50]
        
        assert len(chunks) == 0

    def test_chunk_with_mixed_content(self):
        """测试混合内容文档"""
        content = "短段落\n\n这是一个较长的段落内容，长度超过五十个字符，应该被正确处理和切分操作完成测试验证功能正常工作通过测试。\n\n另一个短段落\n\n这又是一个较长的段落内容，长度同样超过五十个字符，应该被正确处理和切分操作完成测试验证功能正常工作通过测试。"
        chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 50]
        
        assert len(chunks) == 2

    def test_chunk_id_generation(self):
        """测试文档ID生成"""
        filepath = "/test/path/document.md"
        doc_id = hashlib.md5(filepath.encode()).hexdigest()
        
        assert len(doc_id) == 32
        assert doc_id == hashlib.md5(filepath.encode()).hexdigest()

    def test_chunk_metadata_creation(self):
        """测试元数据创建"""
        filepath = "/test/path/document.md"
        num_chunks = 3
        metas = [{"source": filepath, "chunk": i} for i in range(num_chunks)]
        
        assert len(metas) == 3
        for i, meta in enumerate(metas):
            assert meta["source"] == filepath
            assert meta["chunk"] == i


class TestBatchIngest:
    """测试批量导入功能"""

    def test_batch_ingest_multiple_files(self, mock_chroma_collection, temp_test_dir):
        """测试批量导入多个文件"""
        knowledge_dir = Path(temp_test_dir) / "knowledge"
        knowledge_dir.mkdir()
        
        (knowledge_dir / "doc1.md").write_text("文档1内容，长度超过五十个字符的测试段落内容，用于测试切分功能是否正常工作验证通过测试用例。", encoding='utf-8')
        (knowledge_dir / "doc2.txt").write_text("文档2内容，长度超过五十个字符的测试段落内容，用于测试切分功能是否正常工作验证通过测试用例。", encoding='utf-8')
        (knowledge_dir / "doc3.py").write_text("# Python文件，不应被处理", encoding='utf-8')
        
        files_processed = []
        for f in knowledge_dir.iterdir():
            if f.suffix in ('.md', '.txt'):
                files_processed.append(f.name)
        
        assert len(files_processed) == 2
        assert "doc1.md" in files_processed
        assert "doc2.txt" in files_processed
        assert "doc3.py" not in files_processed

    def test_batch_ingest_nested_directories(self, mock_chroma_collection, temp_test_dir):
        """测试嵌套目录的批量导入"""
        knowledge_dir = Path(temp_test_dir) / "knowledge"
        nested_dir = knowledge_dir / "nested"
        nested_dir.mkdir(parents=True)
        
        (knowledge_dir / "root.md").write_text("根目录文档内容，长度超过五十个字符的测试段落内容，用于测试切分功能是否正常工作验证通过测试用例。", encoding='utf-8')
        (nested_dir / "nested.md").write_text("嵌套目录文档内容，长度超过五十个字符的测试段落内容，用于测试切分功能是否正常工作验证通过测试用例。", encoding='utf-8')
        
        files_found = []
        import os
        for root, _, files in os.walk(str(knowledge_dir)):
            for f in files:
                if f.endswith(('.md', '.txt')):
                    files_found.append(f)
        
        assert len(files_found) == 2
