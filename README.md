# PineVC-PR

松禾资本医健团队 PR 自动化系统 - 全媒体品牌中央厨房

## 项目定位

将 PR 执行工作升级为品牌战略指挥，通过 AI + 自动化工作流，实现 1 人团队 = 20 人全媒体公关效果。

## 核心功能

1. **老板转发文章智能加工** - 每日 3-5 篇，自动生成 PR 内容
2. **热点监控内容生成** - 主动发现行业热点，生成论点驱动内容
3. **社群早报推送** - 今日/本周医药大事（规划中）

## 年度核心论点 (2026)

**CDE + AI**：中国创新药的竞争力 = Discovery × Clinical × Engineering，AI 是加速器

- **C (Clinical)** - 临床转化能力
- **D (Discovery)** - 创新技术来源
- **E (Engineering)** - 工程化验证能力
- **AI** - 各环节的智能加速

## 技术架构

- **工作流引擎**: Dify (自托管)
- **LLM**: Claude (主力) / GPT-4 (备选)
- **知识库**: RAG + 向量数据库
- **分发渠道**: 微信公众号 (MVP) → 多平台扩展

详见 [架构文档](docs/architecture/ARCHITECTURE.md)

## 开发进度

详见 [路线图](docs/planning/ROADMAP.md) 和 [当前冲刺](docs/planning/SPRINT.md)

## 目录结构

```
pinevc-pr/
├── docs/                   # 文档中心
│   ├── architecture/       # 架构文档
│   ├── planning/           # 规划文档
│   ├── execution/          # 执行文档
│   └── knowledge/          # 知识库
├── src/                    # 源代码
│   ├── workflows/          # Dify 工作流导出
│   ├── prompts/            # Prompt 模板
│   ├── scripts/            # 工具脚本
│   └── config/             # 配置文件
├── assets/                 # 资源文件
└── archive/                # 归档
```

## 协作模式

本项目采用多角色协作模式，通过 Git 同步：

- **架构师** - 总体设计、技术决策
- **规划师** - 任务拆解、进度跟踪
- **执行者** - 代码实现、部署测试

详见 [协作协议](docs/architecture/ARCHITECTURE.md#协作协议)

## 快速开始

```bash
# 克隆项目
git clone <repo-url>
cd pinevc-pr

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入配置

# 查看当前任务
cat docs/planning/SPRINT.md
```

## 参考文档

- [松禾自动化PR愿景](松禾自动化PR愿景.pdf)
- [PitchBook 中国生物医药报告](q1-2026-pitchbook-analyst-note-the-chinese-biopharma-landscape-where-new-assets-are-born.pdf)
