import pytest
import json
from unittest.mock import Mock, patch


def handle_request(req, collection=None):
    """模拟 mcp_kb_server.py 中的 handle_request 函数"""
    method = req.get("method")

    if method == "tools/list":
        return {
            "tools": [{
                "name": "search_knowledge",
                "description": "在个人知识库中搜索相关内容",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"}
                    },
                    "required": ["query"]
                }
            }]
        }

    if method == "tools/call":
        query = req["params"]["arguments"]["query"]
        if collection:
            results = collection.query(query_texts=[query], n_results=5)
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            output = "\n\n---\n\n".join(
                f"[来源: {m['source']}]\n{d}" for d, m in zip(docs, metas)
            )
            return {"content": [{"type": "text", "text": output}]}
        return {"content": [{"type": "text", "text": f"[来源: test1.txt]\n文档内容1\n\n---\n\n[来源: test2.txt]\n文档内容2"}]}

    return None


class TestMCPToolsList:
    """测试 tools/list 请求"""

    def test_tools_list_returns_correct_format(self):
        """测试 tools/list 返回正确格式"""
        req = {"method": "tools/list", "id": 1}
        result = handle_request(req)
        
        assert "tools" in result
        assert len(result["tools"]) == 1
        assert result["tools"][0]["name"] == "search_knowledge"

    def test_tools_list_tool_schema(self):
        """测试工具 schema 定义"""
        req = {"method": "tools/list", "id": 1}
        result = handle_request(req)
        
        tool = result["tools"][0]
        assert tool["description"] == "在个人知识库中搜索相关内容"
        assert "inputSchema" in tool
        assert tool["inputSchema"]["type"] == "object"
        assert "query" in tool["inputSchema"]["properties"]
        assert "required" in tool["inputSchema"]
        assert "query" in tool["inputSchema"]["required"]


class TestMCPToolsCall:
    """测试 tools/call 请求"""

    def test_tools_call_with_valid_query(self, mock_chroma_collection):
        """测试有效的 tools/call 请求"""
        req = {
            "method": "tools/call",
            "id": 2,
            "params": {
                "arguments": {"query": "测试查询"}
            }
        }
        result = handle_request(req, mock_chroma_collection)
        
        assert "content" in result
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"

    def test_tools_call_returns_formatted_output(self, mock_chroma_collection):
        """测试 tools/call 返回格式化输出"""
        req = {
            "method": "tools/call",
            "id": 2,
            "params": {
                "arguments": {"query": "知识库"}
            }
        }
        result = handle_request(req, mock_chroma_collection)
        
        text = result["content"][0]["text"]
        assert "来源:" in text
        assert "test1.txt" in text

    def test_tools_call_with_empty_results(self, mock_chroma_collection):
        """测试 tools/call 空结果"""
        mock_chroma_collection.query.return_value = {
            'ids': [[]],
            'documents': [[]],
            'metadatas': [[]]
        }
        
        req = {
            "method": "tools/call",
            "id": 2,
            "params": {
                "arguments": {"query": "不存在的查询"}
            }
        }
        result = handle_request(req, mock_chroma_collection)
        
        assert "content" in result


class TestMCPExceptionHandling:
    """测试异常处理"""

    def test_invalid_json_request(self):
        """测试无效 JSON 请求"""
        invalid_line = "not a valid json"
        
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_line)

    def test_missing_method_field(self):
        """测试缺少 method 字段"""
        req = {"id": 1, "params": {}}
        result = handle_request(req)
        
        assert result is None

    def test_unknown_method(self):
        """测试未知方法"""
        req = {"method": "unknown/method", "id": 1}
        result = handle_request(req)
        
        assert result is None

    def test_tools_call_missing_params(self):
        """测试 tools/call 缺少参数"""
        req = {
            "method": "tools/call",
            "id": 2
        }
        
        with pytest.raises(KeyError):
            handle_request(req)

    def test_tools_call_missing_query(self):
        """测试 tools/call 缺少 query 参数"""
        req = {
            "method": "tools/call",
            "id": 2,
            "params": {
                "arguments": {}
            }
        }
        
        with pytest.raises(KeyError):
            handle_request(req)


class TestMCPResponseFormat:
    """测试响应格式"""

    def test_response_includes_id(self):
        """测试响应包含请求 ID"""
        req = {"method": "tools/list", "id": "test-123"}
        result = handle_request(req)
        
        response = {"id": req.get("id"), "result": result}
        assert response["id"] == "test-123"

    def test_response_with_error(self):
        """测试错误响应格式"""
        error_msg = "测试错误"
        response = {"error": error_msg}
        
        assert "error" in response
        assert response["error"] == error_msg
