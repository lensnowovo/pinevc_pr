"""
LLM 客户端模块

提供统一的 LLM 调用接口
"""

import os
import json
from typing import Dict, Any, Optional, List
from anthropic import Anthropic


class LLMClient:
    """LLM 客户端"""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化客户端"""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            # 如果没有 API Key，使用模拟模式
            self.client = None
            print("[LLM] Warning: ANTHROPIC_API_KEY not set, using mock mode")

    def call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """
        调用 LLM

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            max_tokens: 最大 token 数
            temperature: 温度参数

        Returns:
            LLM 响应文本
        """
        if self.client is None:
            return self._mock_response(prompt)

        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": messages,
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)

            return response.content[0].text

        except Exception as e:
            return f"[LLM Error] {str(e)}"

    def call_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        调用 LLM 并返回 JSON

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            max_tokens: 最大 token 数

        Returns:
            解析后的 JSON 对象
        """
        # 添加 JSON 格式要求
        json_prompt = f"{prompt}\n\n请以 JSON 格式返回结果，不要包含其他文字。"

        response = self.call(json_prompt, system_prompt, max_tokens, temperature=0.3)

        try:
            # 尝试提取 JSON
            json_str = response.strip()
            # 移除可能的 markdown 代码块标记
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()

            return json.loads(json_str)
        except json.JSONDecodeError:
            # 如果解析失败，返回原始响应
            return {"raw_response": response, "parse_error": True}

    def _mock_response(self, prompt: str) -> str:
        """模拟响应（用于测试）"""
        if "分析" in prompt or "analyze" in prompt.lower():
            return json.dumps({
                "analysis": "任务分析完成",
                "complexity": "medium",
                "estimated_time": "2 hours"
            }, ensure_ascii=False)
        elif "代码" in prompt or "code" in prompt.lower():
            return "# Generated code\npass\n"
        elif "审查" in prompt or "review" in prompt.lower():
            return json.dumps({
                "passed": True,
                "score": 85,
                "issues": []
            }, ensure_ascii=False)
        elif "安全" in prompt or "security" in prompt.lower():
            return json.dumps({
                "passed": True,
                "risk_level": "low",
                "issues": []
            }, ensure_ascii=False)
        else:
            return "LLM mock response"


# 全局实例
llm = LLMClient()


# === 便捷函数 ===

def call_llm(prompt: str, system_prompt: Optional[str] = None) -> str:
    """调用 LLM"""
    return llm.call(prompt, system_prompt)


def call_llm_json(prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """调用 LLM 并返回 JSON"""
    return llm.call_json(prompt, system_prompt)


# === Agent 专用 Prompt 模板 ===

SYSTEM_PROMPTS = {
    "developer": """你是一个经验丰富的软件工程师。你的职责是：
1. 分析开发任务需求
2. 编写高质量、可维护的代码
3. 编写单元测试
4. 确保代码符合最佳实践

请用中文回复，保持专业和简洁。""",

    "reviewer": """你是一个严格的代码审查专家。你的职责是：
1. 检查代码干净程度（无注释代码、无调试语句）
2. 检查最佳实践（错误处理、类型标注、文档）
3. 评估可维护性（函数长度、模块职责）

请用中文回复，给出具体的评分和改进建议。""",

    "security": """你是一个安全审计专家。你的职责是：
1. 检查代码安全（无硬编码密钥、无注入漏洞）
2. 检查配置安全（环境变量、权限设置）
3. 检查内容安全（无敏感信息泄露）

请用中文回复，明确指出风险等级和具体问题。""",

    "operator": """你是一个运维工程师。你的职责是：
1. 执行部署前检查
2. 运行部署流程
3. 验证部署结果

请用中文回复，确保每一步都有明确的状态。"""
}


def get_system_prompt(agent_type: str) -> str:
    """获取 Agent 系统提示"""
    return SYSTEM_PROMPTS.get(agent_type, "")
