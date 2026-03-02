"""
Hello 模块

简单的问候函数，用于测试 Orchestrator 工作流
"""


def hello(name: str = "Orchestrator") -> str:
    """
    生成问候语

    Args:
        name: 要问候的名字，默认为 "Orchestrator"

    Returns:
        格式化的问候字符串

    Examples:
        >>> hello("World")
        'Hello, World!'
        >>> hello()
        'Hello, Orchestrator!'
    """
    return f"Hello, {name}!"
