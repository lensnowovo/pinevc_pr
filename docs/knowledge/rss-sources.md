# 医健行业 RSS 信息源清单

> 用于 n8n RSS 采集工作流 | 更新: 2026-03-02

## 核心信息源 (推荐)

### 🏢 监管与政策

| 来源 | RSS 地址 | 更新频率 | 优先级 |
|------|----------|----------|--------|
| NMPA 官网 | https://www.nmpa.gov.cn/directory/web/nmpa/xxgk/ggtg/qitaqita/rss.xml | 每日 | P0 |
| CDE 官网 | https://www.cde.org.cn/main/news/queryNormalList/rss | 每日 | P0 |
| 国家卫健委 | http://www.nhc.gov.cn/xcs/yqfkdt/gzbd/rss.xml | 每日 | P1 |

### 📰 行业媒体

| 来源 | RSS 地址 | 更新频率 | 优先级 |
|------|----------|----------|--------|
| 动脉网 | https://www.vbdata.cn/rss | 每日多次 | P0 |
| 亿欧大健康 | https://www.iyiou.com/rss/health | 每日 | P0 |
| 健康界 | https://www.cn-healthcare.com/rss | 每日 | P1 |
| 医药经济报 | https://www.yyjjb.com.cn/rss | 每周 | P1 |
| 药明康德公众号 | (需通过 n8n 微信采集) | 每日 | P0 |

### 🌍 国际信息源

| 来源 | RSS 地址 | 更新频率 | 优先级 |
|------|----------|----------|--------|
| FierceBiotech | https://www.fiercebiotech.com/rss.xml | 每日 | P1 |
| BioSpace | https://www.biospace.com/rss | 每日 | P2 |
| STAT News | https://www.statnews.com/rss | 每日 | P1 |
| Endpoints News | https://endpts.com/feed/ | 每日 | P1 |

### 💰 投融资信息

| 来源 | RSS 地址 | 更新频率 | 优先级 |
|------|----------|----------|--------|
| 投中网大健康 | https://www.chinaventure.com.cn/rss/health | 每日 | P1 |
| 36氪出海 | https://36kr.com/rss出海 | 每日 | P2 |
| 动脉橙产业图谱 | (需 API 接入) | 每周 | P1 |

---

## 备用信息源

### 学术期刊

| 来源 | RSS 地址 | 说明 |
|------|----------|------|
| Nature Medicine | https://www.nature.com/nm/rss.xml | 顶级医学期刊 |
| NEJM | https://www.nejm.org/rss | 新英格兰医学杂志 |
| Lancet | https://www.thelancet.com/rss | 柳叶刀 |

### 企业公告

| 来源 | 获取方式 | 说明 |
|------|----------|------|
| 港交所公告 | https://www.hkexnews.hk/rss | 上市公司公告 |
| 上交所公告 | http://www.sse.com.cn/rss | A股公告 |

---

## 关键词过滤配置

### 高优先级关键词 (必采集)

```yaml
must_have:
  - "创新药"
  - "ADC"
  - "双抗"
  - "细胞治疗"
  - "基因治疗"
  - "AI制药"
  - "IND"
  - "NDA"
  - "获批"
  - "License-out"
  - "融资"
```

### 排除关键词

```yaml
exclude:
  - "招聘"
  - "会议通知"
  - "培训班"
  - "广告"
```

### 论点关联关键词

```yaml
thesis_mapping:
  clinical:
    - "临床试验"
    - "IND"
    - "患者入组"
    - "CDE"
    - "突破性疗法"
  discovery:
    - "靶点"
    - "First-in-class"
    - "新模态"
    - "AI药物设计"
  engineering:
    - "CMC"
    - "规模化生产"
    - "GMP"
    - "质量控制"
  ai:
    - "AI制药"
    - "深度学习"
    - "AlphaFold"
    - "生成式AI"
```

---

## n8n RSS 采集配置

### 推荐采集频率

| 信息源类型 | 频率 | Cron 表达式 |
|------------|------|-------------|
| 监管政策 | 每日 1 次 | `0 9 * * *` |
| 行业媒体 | 每 4 小时 | `0 */4 * * *` |
| 国际信息 | 每日 2 次 | `0 9,21 * * *` |
| 投融资 | 每日 1 次 | `0 10 * * *` |

### 数据存储格式

```json
{
  "id": "uuid",
  "title": "文章标题",
  "url": "原文链接",
  "source": "来源名称",
  "published_at": "2026-03-02T10:00:00Z",
  "collected_at": "2026-03-02T10:05:00Z",
  "content": "正文内容",
  "summary": "摘要",
  "keywords": ["关键词1", "关键词2"],
  "thesis_tags": ["clinical", "discovery"],
  "priority": "high",
  "status": "pending"
}
```

---

## 注意事项

1. **微信文章采集**: 需要配置代理或使用第三方服务
2. **反爬虫处理**: 部分 RSS 源需要设置 User-Agent
3. **内容去重**: 使用 URL 或标题做唯一性判断
4. **速率限制**: 避免过于频繁请求被封禁

---

*本文档为 n8n 采集配置参考*
