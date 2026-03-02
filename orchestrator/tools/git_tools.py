"""
Git 工具集

提供 Git 操作能力:
- git status/diff/log
- git add/commit/push
- 分支管理
"""

import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path


class GitTools:
    """Git 工具类"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    def _run_git(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """执行 git 命令"""
        cmd = ["git"] + args
        return subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=check,
            encoding="utf-8",
            errors="replace"  # 替换无法解码的字符
        )

    # === 只读操作 ===

    def status(self) -> Dict[str, Any]:
        """获取 git status"""
        result = self._run_git(["status", "--porcelain"])
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

        files = {
            "modified": [],
            "added": [],
            "deleted": [],
            "untracked": []
        }

        for line in lines:
            if not line:
                continue
            status = line[:2].strip()
            filepath = line[3:]

            if status == "M":
                files["modified"].append(filepath)
            elif status == "A":
                files["added"].append(filepath)
            elif status == "D":
                files["deleted"].append(filepath)
            elif status == "??":
                files["untracked"].append(filepath)

        return {
            "success": True,
            "files": files,
            "has_changes": bool(any(files.values()))
        }

    def diff(self, staged: bool = False) -> str:
        """获取 git diff"""
        args = ["diff"]
        if staged:
            args.append("--staged")
        result = self._run_git(args)
        return result.stdout

    def log(self, count: int = 10, oneline: bool = True) -> List[Dict[str, str]]:
        """获取 git log"""
        args = ["log", f"-{count}"]
        if oneline:
            args.append("--oneline")
        result = self._run_git(args)

        commits = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    commits.append({"hash": parts[0], "message": parts[1]})
        return commits

    def branch(self) -> Dict[str, Any]:
        """获取分支信息"""
        result = self._run_git(["branch", "-a"])
        lines = result.stdout.strip().split("\n")

        current = None
        branches = []

        for line in lines:
            line = line.strip()
            if line.startswith("* "):
                current = line[2:]
                branches.append(current)
            else:
                branches.append(line)

        return {
            "success": True,
            "current": current,
            "branches": branches
        }

    # === 写入操作 ===

    def add(self, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """git add"""
        if files is None:
            args = ["add", "."]  # nosec
        else:
            args = ["add"] + files

        try:
            self._run_git(args)
            return {"success": True, "message": f"Added {len(files) if files else 'all'} files"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}

    def commit(self, message: str) -> Dict[str, Any]:
        """git commit"""
        try:
            result = self._run_git(["commit", "-m", message])
            return {"success": True, "message": "Commit created", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}

    def push(self, remote: str = "origin", branch: Optional[str] = None) -> Dict[str, Any]:
        """git push"""
        args = ["push", remote]
        if branch:
            args.append(branch)

        try:
            result = self._run_git(args)
            return {"success": True, "message": "Push completed", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}

    def checkout(self, branch: str, create: bool = False) -> Dict[str, Any]:
        """git checkout"""
        args = ["checkout"]
        if create:
            args.append("-b")
        args.append(branch)

        try:
            result = self._run_git(args)
            return {"success": True, "message": f"Checked out {branch}", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}

    # === 便捷方法 ===

    def quick_commit(self, message: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """快速提交: add + commit"""
        add_result = self.add(files)
        if not add_result["success"]:
            return add_result

        return self.commit(message)

    def commit_and_push(self, message: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """提交并推送: add + commit + push"""
        commit_result = self.quick_commit(message, files)
        if not commit_result["success"]:
            return commit_result

        branch_info = self.branch()
        current_branch = branch_info.get("current", "main")

        return self.push(branch=current_branch)


# 全局实例
git = GitTools()


# === 工具函数 (供 Agent 调用) ===

def git_status() -> Dict[str, Any]:
    """获取仓库状态"""
    return git.status()


def git_diff(staged: bool = False) -> str:
    """获取变更差异"""
    return git.diff(staged)


def git_log(count: int = 10) -> List[Dict[str, str]]:
    """获取提交历史"""
    return git.log(count)


def git_add(files: Optional[List[str]] = None) -> Dict[str, Any]:
    """添加文件到暂存区"""
    return git.add(files)


def git_commit(message: str) -> Dict[str, Any]:
    """提交变更"""
    return git.commit(message)


def git_push(remote: str = "origin", branch: Optional[str] = None) -> Dict[str, Any]:
    """推送到远程"""
    return git.push(remote, branch)


def git_quick_commit(message: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
    """快速提交 (add + commit)"""
    return git.quick_commit(message, files)


def git_branch() -> Dict[str, Any]:
    """获取分支信息"""
    return git.branch()
