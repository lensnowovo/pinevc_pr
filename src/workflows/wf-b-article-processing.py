"""
WF-B: 老板转发 → 内容加工工作流
使用 Dify API 构建
"""

import os
import json
import requests
from typing import Optional, Dict, Any

class DifyWorkflowBuilder:
    """Dify 工作流构建器"""

    def __init__(self, api_base: str = "http://localhost:5001", api_key: str = None):
        self.api_base = api_base
        self.api_key = api_key

    def create_knowledge_base(self, name: str, description: str) -> Dict:
        """创建知识库"""
        # 注意：Dify 知识库创建需要通过 Web 界面或内部 API
        # 这里提供 API 调用示例
        pass

    def run_workflow(self, workflow_id: str, inputs: Dict) -> Dict:
        """运行工作流"""
        url = f"{self.api_base}/v1/workflows/run"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": inputs,
            "user": "wf-b-automation"
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()


class WFBWorkflow:
    """
    WF-B: 老板转发 → 内容加工

    流程:
    1. 接收文章链接
    2. 获取文章内容
    3. 知识库检索匹配论点
    4. 知识库检索匹配企业
    5. LLM 生成内容
    6. 质量检查
    7. 输出结果
    """

    def __init__(self, dify_api_key: str, dify_api_base: str = "http://localhost:5001"):
        self.api_key = dify_api_key
        self.api_base = dify_api_base
        self.knowledge_bases = {
            "thesis": "thesis-framework",  # 论点框架知识库 ID
            "portfolio": "portfolio"        # 被投企业知识库 ID
        }

    def fetch_article(self, url: str) -> Dict[str, str]:
        """
        获取文章内容
        支持微信公众号、普通网页等
        """
        # 使用 n8n 或代理服务获取微信文章
        # 这里简化处理
        return {
            "url": url,
            "title": "",
            "content": "",
            "source": ""
        }

    def retrieve_theses(self, article_content: str, top_k: int = 3) -> list:
        """
        从知识库检索匹配的论点
        """
        url = f"{self.api_base}/v1/datasets/{self.knowledge_bases['thesis']}/retrieve"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "query": article_content[:2000],  # 限制长度
            "retrieval_model": {
                "search_method": "semantic_search",
                "top_k": top_k
            }
        }
        # response = requests.post(url, headers=headers, json=data)
        # return response.json()

        # 模拟返回
        return [
            {"content": "Clinical - 临床转化", "score": 0.85},
            {"content": "Discovery - 创新来源", "score": 0.72}
        ]

    def retrieve_companies(self, article_content: str, theses: list, top_k: int = 3) -> list:
        """
        从知识库检索相关被投企业
        """
        query = f"{article_content[:1000]} {' '.join([t['content'] for t in theses])}"
        # 类似 retrieve_theses 的实现
        return [
            {"company": "示例企业", "relevance": "high"}
        ]

    def generate_content(self, article: Dict, theses: list, companies: list) -> str:
        """
        调用 Dify 工作流生成内容
        """
        url = f"{self.api_base}/v1/workflows/run"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        inputs = {
            "article_title": article.get("title", ""),
            "article_url": article.get("url", ""),
            "article_content": article.get("content", ""),
            "matched_theses": json.dumps(theses, ensure_ascii=False),
            "related_companies": json.dumps(companies, ensure_ascii=False),
            "additional_note": ""
        }

        data = {
            "inputs": inputs,
            "user": "wf-b-automation"
        }

        # response = requests.post(url, headers=headers, json=data)
        # return response.json()

        return "生成的文章内容..."

    def quality_check(self, content: str) -> Dict:
        """
        质量检查
        """
        checks = {
            "length_ok": 800 <= len(content) <= 2000,
            "has_thesis": any(kw in content for kw in ["Clinical", "Discovery", "Engineering", "AI"]),
            "no_forbidden_words": not any(kw in content for kw in ["完爆", "碾压", "超越美国"]),
            "has_structure": all(section in content for section in ["##", "标签"])
        }

        return {
            "passed": all(checks.values()),
            "checks": checks,
            "score": sum(checks.values()) / len(checks) * 100
        }

    def run(self, article_url: str, additional_note: str = "") -> Dict:
        """
        执行完整工作流
        """
        # 1. 获取文章
        article = self.fetch_article(article_url)

        # 2. 检索论点
        theses = self.retrieve_theses(article.get("content", ""))

        # 3. 检索企业
        companies = self.retrieve_companies(article.get("content", ""), theses)

        # 4. 生成内容
        content = self.generate_content(article, theses, companies)

        # 5. 质量检查
        quality = self.quality_check(content)

        return {
            "status": "success" if quality["passed"] else "needs_review",
            "article": article,
            "matched_theses": theses,
            "related_companies": companies,
            "generated_content": content,
            "quality_check": quality
        }


# Dify 工作流 DSL 配置
DIFY_WORKFLOW_DSL = {
    "name": "WF-B: 文章加工",
    "description": "将老板转发的文章加工为松禾品牌内容",
    "version": "1.0.0",
    "nodes": [
        {
            "id": "start",
            "type": "start",
            "title": "开始",
            "data": {
                "variables": [
                    {"name": "article_url", "type": "string", "label": "文章链接"},
                    {"name": "additional_note", "type": "string", "label": "附加说明", "default": ""}
                ]
            }
        },
        {
            "id": "http_fetch",
            "type": "http-request",
            "title": "获取文章内容",
            "data": {
                "method": "GET",
                "url": "{{article_url}}",
                "timeout": 30
            }
        },
        {
            "id": "kb_thesis",
            "type": "knowledge-retrieval",
            "title": "检索论点框架",
            "data": {
                "dataset_id": "{{thesis_framework_dataset_id}}",
                "query": "{{http_fetch.content}}",
                "top_k": 3
            }
        },
        {
            "id": "kb_portfolio",
            "type": "knowledge-retrieval",
            "title": "检索被投企业",
            "data": {
                "dataset_id": "{{portfolio_dataset_id}}",
                "query": "{{http_fetch.content}} {{kb_thesis.result}}",
                "top_k": 3
            }
        },
        {
            "id": "llm_generate",
            "type": "llm",
            "title": "生成内容",
            "data": {
                "model": {
                    "provider": "zhipuai",
                    "name": "glm-4-flash",
                    "mode": "chat"
                },
                "prompt": {
                    "system": "{{system_prompt}}",
                    "user": "{{user_prompt_template}}"
                },
                "variables": {
                    "article_title": "{{http_fetch.title}}",
                    "article_url": "{{article_url}}",
                    "article_content": "{{http_fetch.content}}",
                    "matched_theses": "{{kb_thesis.result}}",
                    "related_companies": "{{kb_portfolio.result}}",
                    "additional_note": "{{additional_note}}"
                }
            }
        },
        {
            "id": "llm_check",
            "type": "llm",
            "title": "质量检查",
            "data": {
                "model": {
                    "provider": "zhipuai",
                    "name": "glm-4-flash",
                    "mode": "chat"
                },
                "prompt": {
                    "system": "你是一个内容质量审核员。检查文章是否符合品牌规范。",
                    "user": "请检查以下文章：\n\n{{llm_generate.text}}"
                }
            }
        },
        {
            "id": "end",
            "type": "end",
            "title": "结束",
            "data": {
                "outputs": [
                    {"name": "title", "value": "{{llm_generate.title}}"},
                    {"name": "content", "value": "{{llm_generate.text}}"},
                    {"name": "quality_report", "value": "{{llm_check.text}}"}
                ]
            }
        }
    ],
    "edges": [
        {"source": "start", "target": "http_fetch"},
        {"source": "http_fetch", "target": "kb_thesis"},
        {"source": "kb_thesis", "target": "kb_portfolio"},
        {"source": "kb_portfolio", "target": "llm_generate"},
        {"source": "llm_generate", "target": "llm_check"},
        {"source": "llm_check", "target": "end"}
    ]
}


if __name__ == "__main__":
    # 示例用法
    workflow = WFBWorkflow(dify_api_key="your-api-key")

    result = workflow.run(
        article_url="https://example.com/article",
        additional_note="重点突出 Clinical 效率"
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
