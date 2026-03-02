"""
文件操作工具

提供文件读写能力:
- 读取文件
- 写入文件
- 列出目录
- 搜索文件
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class FileTools:
    """文件工具类"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)

    def read_file(self, filepath: str) -> Dict[str, Any]:
        """读取文件内容"""
        try:
            full_path = self.base_path / filepath
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "success": True,
                "content": content,
                "path": str(full_path),
                "size": len(content)
            }
        except FileNotFoundError:
            return {"success": False, "error": f"File not found: {filepath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """写入文件"""
        try:
            full_path = self.base_path / filepath

            # 确保目录存在
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "success": True,
                "message": f"File written: {filepath}",
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_dir(self, dirpath: str = ".", pattern: str = "*") -> List[Dict[str, Any]]:
        """列出目录内容"""
        try:
            full_path = self.base_path / dirpath
            items = []

            for item in sorted(full_path.glob(pattern)):
                items.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.base_path)),
                    "is_dir": item.is_dir(),
                    "is_file": item.is_file(),
                    "size": item.stat().st_size if item.is_file() else None
                })

            return items
        except Exception as e:
            return [{"error": str(e)}]

    def exists(self, filepath: str) -> bool:
        """检查文件是否存在"""
        full_path = self.base_path / filepath
        return full_path.exists()

    def search_files(self, pattern: str, dirpath: str = ".") -> List[str]:
        """搜索文件"""
        try:
            full_path = self.base_path / dirpath
            matches = []

            for item in full_path.rglob(pattern):
                # 排除常见的不需要的目录
                rel_path = str(item.relative_to(self.base_path))
                if any(skip in rel_path for skip in ["__pycache__", ".git", "node_modules", ".venv"]):
                    continue
                matches.append(rel_path)

            return matches[:100]  # 限制结果数量
        except Exception as e:
            return [f"Error: {e}"]

    def create_dir(self, dirpath: str) -> Dict[str, Any]:
        """创建目录"""
        try:
            full_path = self.base_path / dirpath
            full_path.mkdir(parents=True, exist_ok=True)
            return {"success": True, "message": f"Directory created: {dirpath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_file(self, filepath: str) -> Dict[str, Any]:
        """删除文件"""
        try:
            full_path = self.base_path / filepath
            if full_path.is_file():
                full_path.unlink()
                return {"success": True, "message": f"File deleted: {filepath}"}
            else:
                return {"success": False, "error": f"Not a file: {filepath}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# 全局实例
files = FileTools()


# === 工具函数 (供 Agent 调用) ===

def read_file(filepath: str) -> Dict[str, Any]:
    """读取文件"""
    return files.read_file(filepath)


def write_file(filepath: str, content: str) -> Dict[str, Any]:
    """写入文件"""
    return files.write_file(filepath, content)


def list_dir(dirpath: str = ".", pattern: str = "*") -> List[Dict[str, Any]]:
    """列出目录"""
    return files.list_dir(dirpath, pattern)


def file_exists(filepath: str) -> bool:
    """检查文件是否存在"""
    return files.exists(filepath)


def search_files(pattern: str, dirpath: str = ".") -> List[str]:
    """搜索文件"""
    return files.search_files(pattern, dirpath)


def create_dir(dirpath: str) -> Dict[str, Any]:
    """创建目录"""
    return files.create_dir(dirpath)
