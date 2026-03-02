# 工具集参考

> **用途**: Orchestrator 工具集参考
> **基于**: orchestrator/tools/

---

## Git 工具

### 状态检查

```python
# orchestrator/tools/git_tools.py

def git_status() -> Dict[str, Any]:
    """获取仓库状态"""
    # 返回: { files: { modified, added, deleted, untracked }, has_changes }
```

### 差异查看

```python
def git_diff(staged: bool = False) -> str:
    """获取变更差异"""
    # staged=True 查看暂存区差异
```

### 提交操作

```python
def git_add(files: Optional[List[str]] = None) -> Dict[str, Any]:
    """添加文件到暂存区"""
    # files=None 添加所有文件

def git_commit(message: str) -> Dict[str, Any]:
    """提交变更"""

def git_push(remote: str = "origin", branch: Optional[str] = None) -> Dict[str, Any]:
    """推送到远程"""
```

### 便捷方法

```python
def git_quick_commit(message: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
    """快速提交: add + commit"""

def git_commit_and_push(message: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
    """提交并推送: add + commit + push"""
```

### 分支操作

```python
def git_branch() -> Dict[str, Any]:
    """获取分支信息"""
    # 返回: { current, branches }

def git_checkout(branch: str, create: bool = False) -> Dict[str, Any]:
    """切换分支"""
    # create=True 创建新分支
```

---

## 安全工具

### 敏感信息扫描

```bash
# API Key 扫描
grep -rn "API_KEY\|APIKEY\|api_key" --include="*.py" --include="*.ts" .

# 密码扫描
grep -rn "PASSWORD\|PASSWD\|password" --include="*.py" --include="*.ts" .

# 密钥扫描
grep -rn "SECRET\|PRIVATE_KEY\|secret" --include="*.py" --include="*.ts" .

# Token 扫描
grep -rn "TOKEN\|ACCESS_TOKEN\|token" --include="*.py" --include="*.ts" .
```

### 个人信息扫描

```bash
# 中国手机号
grep -rn "1[3-9][0-9]\{9\}" --include="*.py" --include="*.ts" .

# 邮箱
grep -rn "[\w.-]+@[\w.-]+\.\w+" --include="*.py" --include="*.ts" .

# 身份证
grep -rn "[0-9]\{17\}[0-9Xx]" --include="*.py" --include="*.ts" .
```

### 脱敏函数

```python
def mask_phone(phone: str) -> str:
    """手机号脱敏: 138****5678"""
    return phone[:3] + "****" + phone[-4:]

def mask_email(email: str) -> str:
    """邮箱脱敏: ex****le@domain.com"""
    parts = email.split("@")
    name = parts[0]
    return name[:2] + "****" + name[-2:] + "@" + parts[1]

def mask_id_card(id_card: str) -> str:
    """身份证脱敏: 110101********1234"""
    return id_card[:6] + "********" + id_card[-4:]

def mask_api_key(api_key: str) -> str:
    """API Key 脱敏: sk-****cdef"""
    return api_key[:3] + "****" + api_key[-4:]
```

---

## 测试工具

### pytest 命令

```bash
# 运行所有测试
pytest tests/

# 运行指定测试
pytest tests/test_module.py

# 显示详细输出
pytest tests/ -v

# 显示覆盖率
pytest tests/ --cov=orchestrator --cov-report=term-missing

# 只运行失败的测试
pytest tests/ --lf

# 并行运行
pytest tests/ -n auto
```

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest tests/ --cov=orchestrator --cov-report=html

# 查看 HTML 报告
open htmlcov/index.html
```

---

## 代码质量工具

### Ruff (Linter)

```bash
# 检查代码
ruff check .

# 检查并修复
ruff check . --fix

# 格式化代码
ruff format .
```

### MyPy (类型检查)

```bash
# 类型检查
mypy orchestrator/

# 忽略缺少的导入
mypy orchestrator/ --ignore-missing-imports
```

---

## 文件操作

### 创建目录

```python
from pathlib import Path

def ensure_dir(path: str) -> Path:
    """确保目录存在"""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
```

### 读写文件

```python
from pathlib import Path

def read_file(path: str) -> str:
    """读取文件"""
    return Path(path).read_text(encoding="utf-8")

def write_file(path: str, content: str) -> None:
    """写入文件"""
    Path(path).write_text(content, encoding="utf-8")
```

---

## 日志工具

```python
import logging

def setup_logging(level: str = "INFO") -> logging.Logger:
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger("orchestrator")
```

---

## 配置工具

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    app_name: str = "PineVC-PR Orchestrator"
    debug: bool = True

    # LLM 配置
    llm_provider: str = "claude_code_cli"
    llm_model: str = "claude-sonnet-4-6"

    # 路径配置
    workspace_path: str = "."

    # 日志配置
    log_level: str = "INFO"

    class Config:
        env_prefix = "ORCHESTRATOR_"
        env_file = ".env"

settings = Settings()
```

---

## 文档生成工具

### 生成文件名

```python
from datetime import datetime

def generate_doc_path(doc_type: str, feature: str) -> str:
    """生成文档路径"""
    date = datetime.now().strftime("%Y-%m-%d")
    return f"docs/{doc_type}/{date}-{feature}-{doc_type[:-1]}.md"

# 示例
# generate_doc_path("designs", "user-permission")
# → "docs/designs/2026-03-02-user-permission-design.md"
```

### 文档类型映射

| 类型 | 目录 | 文件后缀 |
|------|------|----------|
| 需求 | docs/requirements/ | -requirements.md |
| 设计 | docs/designs/ | -design.md |
| 规划 | docs/plans/ | -plan.md |
| 报告 | docs/reports/ | -report.md |
| ADR | docs/architecture/decisions/ | ADR-XXX-.md |

---

*此文档由 Orchestrator 定义*
