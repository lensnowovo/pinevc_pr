# Git 推送指南

## 当前状态

本地仓库已初始化并完成首次提交。

## 手动推送步骤

如果自动推送失败，请手动执行：

```bash
# 进入项目目录
cd /d/0-Dev/Pinevc-pr

# 检查远程仓库
git remote -v

# 推送到 GitHub (选择一种方式)

# 方式 1: HTTPS (需要 Personal Access Token)
git push -u origin main

# 方式 2: 如果有代理
git config --global http.proxy http://127.0.0.1:7890
git push -u origin main

# 方式 3: 使用 SSH (需要配置 SSH Key)
git remote set-url origin git@github.com:lensnowovo/pinevc_pr.git
git push -u origin main
```

## 常见问题

### Q: 推送时提示 Connection reset
A: 网络问题，尝试：
1. 检查网络连接
2. 配置代理
3. 使用 VPN
4. 稍后重试

### Q: 推送时提示 Authentication failed
A: 需要配置认证：
1. GitHub Personal Access Token (HTTPS)
2. SSH Key (SSH)

### Q: 如何配置代理
```bash
# HTTP 代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

## 日常同步

```bash
# 开始工作前
git pull

# 完成工作后
git add .
git commit -m "type(scope): message"
git push
```

## 分支策略

- `main`: 稳定版本
- `develop`: 开发主分支
- `task/xxx`: 任务分支

---

*网络恢复后，执行 `git push -u origin main` 完成首次推送*
