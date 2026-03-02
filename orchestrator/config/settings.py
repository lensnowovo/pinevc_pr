"""
Orchestrator 配置
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    app_name: str = "PineVC-PR Orchestrator"
    app_version: str = "0.1.0"
    debug: bool = True

    # LLM 配置
    # 使用 Claude Code CLI，无需额外配置 API Key
    llm_provider: str = "claude_code_cli"
    llm_model: str = "claude-sonnet-4-6"

    # 人类确认配置
    human_approval_timeout: int = 3600  # 1 小时超时

    # 重试配置
    max_retry_count: int = 3
    retry_delay: float = 1.0

    # 路径配置
    workspace_path: str = "."  # 项目根目录

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None

    class Config:
        env_prefix = "ORCHESTRATOR_"
        env_file = ".env"


# 全局配置实例
settings = Settings()
