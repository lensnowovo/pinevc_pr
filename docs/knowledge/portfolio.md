# 被投企业信息库

> 知识库核心数据 | 最后更新: 2026-03-02

## 使用说明

本文档存储松禾医健团队被投企业的关键信息，用于内容生成时自动关联和引用。

---

## 企业列表

### 🏢 示例企业 1: 康宁杰瑞

```yaml
id: company_001
name: "康宁杰瑞制药"
short_name: "康宁杰瑞"
description: "专注于双特异性抗体和 ADC 药物研发的创新药企"

# 论点相关性 (1=低, 2=中, 3=高)
thesis_relevance:
  clinical: 3      # Clinical - 临床转化
  discovery: 3     # Discovery - 创新来源
  engineering: 2   # Engineering - 工程验证
  ai: 1            # AI 赋能

# 赛道标签
sectors:
  - "双特异性抗体"
  - "ADC"
  - "肿瘤免疫"

# 当前阶段
stage: "Phase III"

# 亮点 (用于引用)
highlights:
  - "全球领先的 PD-L1/CTLA-3 双抗平台"
  - "KN046 多项 III 期临床进行中"
  - "与先声药业达成战略合作"

# 引用话术模板
quote_template: |
  松禾早期布局的康宁杰瑞，其全球领先的双抗平台已进入 III 期临床，
  印证了我们对中国创新药临床转化能力的判断。
```

---

### 🏢 示例企业 2: 荣昌生物

```yaml
id: company_002
name: "荣昌生物制药"
short_name: "荣昌生物"
description: "拥有 ADC 和抗体融合蛋白双重技术平台的创新药企"

thesis_relevance:
  clinical: 3
  discovery: 3
  engineering: 3
  ai: 1

sectors:
  - "ADC"
  - "抗体融合蛋白"
  - "自身免疫"
  - "肿瘤"

stage: "商业化"

highlights:
  - "维迪西妥(RC48) 已获批上市"
  - "泰它西普(RC18) 全球首个 BLyS/APRIL 双靶点药物"
  - "ADC 药物海外授权 Seagen，交易额 26 亿美元"

quote_template: |
  荣昌生物的 ADC 药物海外授权创下 26 亿美元交易记录，
  展现了中国创新药在 Discovery 和 Engineering 两个维度的全球竞争力。
```

---

### 🏢 示例企业 3: 华辉安健

```yaml
id: company_003
name: "华辉安健生物科技"
short_name: "华辉安健"
description: "专注于乙肝和丁肝创新药开发的生物科技公司"

thesis_relevance:
  clinical: 3
  discovery: 2
  engineering: 2
  ai: 1

sectors:
  - "传染病"
  - "乙肝"
  - "丁肝"

stage: "Phase II"

highlights:
  - "HH-003 抗丁肝抗体全球进度领先"
  - "乙肝功能性治愈创新疗法"
  - "与 Gilead 达成合作协议"

quote_template: |
  华辉安健在丁肝领域的突破，体现了中国创新药在临床需求导向下的精准布局。
```

---

### 🏢 示例企业 4: 晶泰科技

```yaml
id: company_004
name: "晶泰科技"
short_name: "晶泰科技"
description: "以 AI 驱动药物研发的科技公司"

thesis_relevance:
  clinical: 1
  discovery: 3
  engineering: 2
  ai: 3        # AI 核心相关

sectors:
  - "AI 制药"
  - "计算化学"
  - "晶型预测"

stage: "成长期"

highlights:
  - "AI 晶型预测准确率超过 95%"
  - "与多家 MNC 药企合作"
  - "自主研发管线快速推进"

quote_template: |
  晶泰科技正在用 AI 重塑药物发现流程，将传统需要数月的晶型筛选工作缩短到数周，
  是 AI 加速创新药研发的典型代表。
```

---

### 🏢 示例企业 5: 纽福斯生物

```yaml
id: company_005
name: "纽福斯生物"
short_name: "纽福斯"
description: "中国领先的基因治疗公司，专注眼科遗传病"

thesis_relevance:
  clinical: 3
  discovery: 2
  engineering: 2
  ai: 1

sectors:
  - "基因治疗"
  - "眼科"
  - "罕见病"

stage: "Phase I/II"

highlights:
  - "中国首个眼科基因治疗临床"
  - "NR082 获 FDA 孤儿药认定"
  - "武汉基地获得 GMP 认证"

quote_template: |
  纽福斯在眼科基因治疗领域率先实现临床突破，展现了中国创新药在
  Clinical 转化方面的效率和执行力。
```

---

## 企业-论点映射表

| 企业 | Clinical | Discovery | Engineering | AI | 推荐引用场景 |
|------|----------|-----------|-------------|-----|-------------|
| 康宁杰瑞 | ★★★ | ★★★ | ★★ | ★ | 双抗、ADC、临床进展 |
| 荣昌生物 | ★★★ | ★★★ | ★★★ | ★ | ADC、商业化、出海 |
| 华辉安健 | ★★★ | ★★ | ★★ | ★ | 传染病、临床效率 |
| 晶泰科技 | ★ | ★★★ | ★★ | ★★★ | AI 制药、创新技术 |
| 纽福斯 | ★★★ | ★★ | ★★ | ★ | 基因治疗、临床突破 |

> ★★★ = 高相关，优先引用
> ★★ = 中相关，适合补充
> ★ = 低相关，背景提及

---

## 关键词-企业映射

### 按关键词快速查找

| 关键词/主题 | 推荐企业 |
|------------|----------|
| ADC | 康宁杰瑞、荣昌生物 |
| 双抗 | 康宁杰瑞 |
| AI 制药 | 晶泰科技 |
| 基因治疗 | 纽福斯 |
| 乙肝/丁肝 | 华辉安健 |
| 出海/License-out | 荣昌生物 |
| 商业化 | 荣昌生物 |
| 临床效率 | 康宁杰瑞、纽福斯、华辉安健 |
| First-in-class | 康宁杰瑞、荣昌生物 |

---

## 数据维护规范

### 更新频率
- **每季度**: 更新企业阶段、近期动态
- **重大事件**: 及时更新 (融资、获批、合作等)
- **年度复盘**: 重新评估论点相关性

### 质量检查
- 引用前核对信息准确性
- 保持简称一致性
- 避免引用敏感信息

---

*本文档为知识库核心，需要根据实际情况填写和更新*
