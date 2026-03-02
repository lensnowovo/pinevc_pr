"""
Hello 函数测试

测试 orchestrator.hello 模块
"""

import pytest


class TestHello:
    """Hello 函数测试类"""

    def test_hello_with_name(self):
        """测试: 带名字参数"""
        # Arrange
        from orchestrator.hello import hello

        # Act
        result = hello("World")

        # Assert
        assert result == "Hello, World!"

    def test_hello_with_empty_string(self):
        """测试: 空字符串"""
        from orchestrator.hello import hello

        # Act
        result = hello("")

        # Assert
        assert result == "Hello, !"

    def test_hello_with_chinese(self):
        """测试: 中文名字"""
        from orchestrator.hello import hello

        # Act
        result = hello("世界")

        # Assert
        assert result == "Hello, 世界!"

    def test_hello_default(self):
        """测试: 默认参数"""
        from orchestrator.hello import hello

        # Act
        result = hello()

        # Assert
        assert result == "Hello, Orchestrator!"
