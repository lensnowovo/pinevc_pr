# TASK-001: Dify 本地部署

## 元信息
- 状态: 🔴 待开始
- 优先级: P0
- 负责角色: Executor
- 预计工时: 2h
- 依赖: 无
- 创建时间: 2026-03-01

## 任务描述

在本地环境部署 Dify，确保服务可访问，为后续工作流开发提供基础。

## 验收标准

- [ ] Dify 服务正常运行 (docker ps 确认)
- [ ] Web 界面可访问 (http://localhost:3000)
- [ ] 能够创建简单的测试 Workflow
- [ ] 部署记录已更新到执行日志

## 执行指南

### Step 1: 环境准备
```bash
# 确认 Docker 已安装
docker --version
docker-compose --version

# 确认端口未被占用 (3000, 5001, 5432, 6379, 8080)
```

### Step 2: 获取 Dify
```bash
# 克隆 Dify 仓库
git clone https://github.com/langgenius/dify.git
cd dify/docker

# 复制环境变量
cp .env.example .env
```

### Step 3: 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 检查服务状态
docker-compose ps
```

### Step 4: 验证部署
```bash
# 访问 Web 界面
# 打开浏览器访问 http://localhost:3000

# 创建测试账号
# 创建一个简单的测试 Workflow 验证功能
```

## 技术要点

1. **端口冲突**: 如果默认端口被占用，修改 docker-compose.yml
2. **内存要求**: 建议至少 8GB RAM
3. **首次启动**: 首次启动可能需要 5-10 分钟拉取镜像
4. **数据持久化**: Dify 数据存储在 Docker volumes 中

## 输出物

- [ ] 部署日志: `docs/execution/logs/2026-03-01-dify-deploy.md`
- [ ] 配置备份: `src/config/dify/docker-compose.override.yml` (如有修改)
- [ ] 管理员账号记录 (保存在安全位置)

## 问题记录

(执行中遇到的问题记录在此)

## 完成记录

- 完成时间: (待填写)
- 实际工时: (待填写)
- 备注: (待填写)

---

*任务完成后更新状态为 🟢 已完成*
