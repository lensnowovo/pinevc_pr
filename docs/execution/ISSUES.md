# 问题与阻塞记录

> 执行者维护 | 最后更新: 2026-03-01

## 问题状态说明

- 🆕 新建 - 待评估
- 🔄 处理中 - 正在解决
- ⬆️ 已升级 - 等待决策
- ✅ 已解决
- ❌ 已关闭 (无效/取消)

---

## 活跃问题

### ISSUE-001: Docker 未安装

#### 元信息
- 状态: 🆕
- 类型: [BLOCKER] 阻塞
- 影响: 高
- 关联任务: TASK-001
- 发现时间: 2026-03-01
- 发现者: Executor

#### 问题描述
执行 TASK-001 Dify 本地部署时，发现系统未安装 Docker。
- `docker --version` 返回 "command not found"
- `docker-compose --version` 返回 "command not found"

#### 解决方案
安装 Docker Desktop for Windows:

1. **下载 Docker Desktop**
   - 访问: https://www.docker.com/products/docker-desktop/
   - 或使用 winget: `winget install Docker.DockerDesktop`

2. **系统要求**
   - Windows 10/11 64-bit
   - 启用 WSL 2 或 Hyper-V
   - 至少 8GB RAM (推荐 16GB)

3. **安装步骤**
   ```powershell
   # 方法1: 使用 winget (推荐)
   winget install Docker.DockerDesktop

   # 方法2: 手动下载安装
   # 下载后运行安装程序，重启电脑
   ```

4. **安装后验证**
   ```powershell
   docker --version
   docker-compose --version
   docker run hello-world
   ```

#### 需要支持
- 用户确认是否可以安装 Docker Desktop
- 确认系统是否满足要求 (WSL2/Hyper-V)

---

## 已解决问题

(暂无)

---

## 问题模板

```markdown
## ISSUE-001: [问题标题]

### 元信息
- 状态: 🆕 / 🔄 / ⬆️ / ✅ / ❌
- 类型: [TECH] 技术 / [REQ] 需求 / [BLOCKER] 阻塞
- 影响: 高 / 中 / 低
- 关联任务: TASK-xxx
- 发现时间: YYYY-MM-DD
- 发现者: Executor

### 问题描述
[清晰描述问题现象]

### 尝试方案
[已尝试的解决方案]

### 需要支持
[需要什么帮助]

### 解决记录
- YYYY-MM-DD: [解决步骤]
```

---

*发现问题立即记录，解决后更新状态*
