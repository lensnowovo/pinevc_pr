# PineVC-PR 部署指南

本目录包含 PineVC-PR 系统 (Dify + n8n) 的 Docker Compose 部署配置。

## 快速开始

### 前置要求

- Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)
- Docker Compose v2.0+
- 至少 8GB 可用内存
- 至少 20GB 可用磁盘空间

### Windows 用户

```powershell
# 1. 配置环境变量
copy .env.example .env
notepad .env  # 编辑并填入 API Key

# 2. 启动服务
start.bat start

# 3. 查看状态
start.bat status
```

### Linux/Mac 用户

```bash
# 1. 配置环境变量
cp .env.example .env
vim .env  # 编辑并填入 API Key

# 2. 添加执行权限
chmod +x start.sh

# 3. 启动服务
./start.sh start

# 4. 查看状态
./start.sh status
```

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **Dify Web** | http://localhost:3000 | Dify 管理界面 |
| **Dify API** | http://localhost:5001 | Dify API 端点 |
| **n8n** | http://localhost:5678 | n8n 工作流界面 |
| **Weaviate** | http://localhost:8080/v1/meta | 向量数据库状态 |

## 环境变量配置

编辑 `.env` 文件配置以下关键参数：

```bash
# 必填 - 至少配置一个 LLM API
OPENAI_API_KEY=sk-xxx           # OpenAI API Key
ANTHROPIC_API_KEY=sk-ant-xxx    # Claude API Key

# 建议修改 - 生产环境安全
DB_PASSWORD=your-secure-password
REDIS_PASSWORD=your-secure-password
DIFY_SECRET_KEY=32-char-secret-key-here

# 可选 - n8n 认证
N8N_AUTH_ACTIVE=true
N8N_AUTH_USER=admin
N8N_AUTH_PASSWORD=your-password
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `start` | 启动所有服务 |
| `stop` | 停止所有服务 |
| `restart` | 重启所有服务 |
| `status` | 查看服务状态 |
| `logs [service]` | 查看日志 (可指定服务) |
| `down` | 停止并删除容器 (保留数据) |
| `reset` | 完全重置 (删除所有数据) |

### 示例

```bash
# 查看所有日志
./start.sh logs

# 只看 Dify API 日志
./start.sh logs dify-api

# 只看 n8n 日志
./start.sh logs n8n
```

## 服务架构

```
┌─────────────────────────────────────────────────────────────┐
│                    PineVC-PR Docker 网络                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Dify 服务组                                         │   │
│  │  ├── dify-web    (端口 3000)  前端界面              │   │
│  │  ├── dify-api    (端口 5001)  API 服务              │   │
│  │  ├── dify-worker            后台任务处理            │   │
│  │  ├── postgres               数据库                  │   │
│  │  ├── redis                  缓存                    │   │
│  │  └── weaviate    (端口 8080) 向量数据库             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  n8n 服务                                            │   │
│  │  └── n8n          (端口 5678) 工作流自动化           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 首次使用

### 1. Dify 初始化

1. 访问 http://localhost:3000
2. 设置管理员账号和密码
3. 配置模型提供商 (Settings → Model Providers)
4. 添加 OpenAI 或 Anthropic API Key

### 2. 创建知识库

在 Dify 中创建以下知识库：

1. **thesis-framework** - 年度论点框架
2. **portfolio** - 被投企业信息
3. **brand-guidelines** - 品牌规范

### 3. n8n 初始化

1. 访问 http://localhost:5678
2. 创建所有者账户
3. 开始创建工作流

### 4. n8n 连接 Dify

在 n8n 中使用 HTTP Request 节点调用 Dify API：

```
POST http://dify-api:5001/v1/workflows/run
Headers:
  Authorization: Bearer {your-api-key}
  Content-Type: application/json
Body:
  {
    "inputs": {},
    "user": "n8n-automation"
  }
```

## 故障排除

### 服务启动失败

```bash
# 检查日志
docker-compose logs dify-api
docker-compose logs n8n

# 重启单个服务
docker-compose restart dify-api
```

### 端口冲突

如果默认端口被占用，编辑 `docker-compose.yml` 修改端口映射：

```yaml
services:
  dify-web:
    ports:
      - "3001:3000"  # 改为 3001
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 状态
docker-compose ps postgres

# 查看 PostgreSQL 日志
docker-compose logs postgres
```

### 重置所有数据

```bash
# ⚠️ 警告：这将删除所有数据
./start.sh reset
# 或
docker-compose down -v
```

## 数据备份

### 备份数据卷

```bash
# 导出 PostgreSQL 数据
docker exec pinevc-postgres pg_dump -U postgres dify > backup_$(date +%Y%m%d).sql

# 导出 n8n 工作流
docker cp pinevc-n8n:/home/node/.n8n ./n8n_backup
```

### 恢复数据

```bash
# 恢复 PostgreSQL
cat backup_20260302.sql | docker exec -i pinevc-postgres psql -U postgres dify

# 恢复 n8n
docker cp ./n8n_backup pinevc-n8n:/home/node/.n8n
docker-compose restart n8n
```

## 生产环境建议

1. **修改所有默认密码**
2. **启用 HTTPS** (使用反向代理如 Nginx/Caddy)
3. **配置定期备份**
4. **设置资源限制**
5. **启用日志轮转**

## 参考链接

- [Dify 官方文档](https://docs.dify.ai/)
- [n8n 官方文档](https://docs.n8n.io/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
