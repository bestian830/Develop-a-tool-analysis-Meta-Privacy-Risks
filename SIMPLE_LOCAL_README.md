# 简化版隐私政策分析器 - 本地NLP版本

> 使用 spaCy 本地分析，无需 LLM API，完全免费

---

## 🎯 核心特点

### 与RAG版本的对比

| 特性 | 本地NLP版 | RAG版（LLM） |
|------|-----------|--------------|
| **运行方式** | ✅ 完全本地 | ❌ 需要API调用 |
| **成本** | ✅ 完全免费 | ❌ ¥0.01-0.05/政策 |
| **网络依赖** | ✅ 无需联网 | ❌ 需要联网 |
| **隐私性** | ✅ 数据不出本地 | ❌ 数据发送到API |
| **准确性** | 中等（依赖规则） | 高（LLM理解） |
| **中文支持** | 需要中文模型 | 天然支持 |
| **代码量** | 约500行 | 约300行 |

### 与原完整系统的对比

| 特性 | 本地NLP简化版 | 原完整系统 |
|------|--------------|------------|
| **代码量** | 500行 | 6,200行 |
| **功能** | 数据-活动映射 | PIPEDA分类+风险评估+映射 |
| **依赖** | spaCy (1个) | spaCy+Transformers+多个 (15个) |
| **输出** | 简洁映射表 | 完整分析报告 |
| **适用场景** | 快速分析 | 学术研究、合规审计 |

---

## 🚀 快速开始（3步）

### 1. 安装依赖

```bash
# 安装spaCy
pip install spacy

# 下载英文模型
python -m spacy download en_core_web_sm

# 可选：下载中文模型（如果分析中文政策）
python -m spacy download zh_core_web_sm
```

### 2. 运行分析

```bash
# 分析英文隐私政策
python tools/simple_local_analyze.py policy.txt

# 生成Markdown报告
python tools/simple_local_analyze.py policy.txt -o report.md

# 分析中文隐私政策
python tools/simple_local_analyze.py policy_cn.txt --model zh_core_web_sm
```

### 3. 查看结果

```markdown
# 隐私政策分析报告（本地NLP版本）

## 📊 分析摘要
- **数据类型**: 12 种
- **活动场景**: 8 个
- **数据-活动映射**: 10 条

## 🔗 数据-活动映射表

### 注册账号
**使用的数据**:
- 姓名
- 邮箱
- 手机号

### 浏览网站
**使用的数据**:
- IP地址
- 浏览记录
```

---

## 📖 工作原理

### 核心方法：spaCy NLP

```
隐私政策文本
    ↓
分段落
    ↓
spaCy NLP处理（词性标注、依存分析、NER）
    ↓
提取数据类型（从收集动词的宾语）
    ↓
提取活动场景（从"when you..."模式）
    ↓
建立映射（句子级共现关系）
    ↓
生成报告
```

### 提取技术

#### 1. 数据类型提取

**方法1：依存句法分析**
```python
# 找"collect"等动词的直接宾语
"We collect your email"
  → collect (动词) → email (宾语)
  → 提取: "email"
```

**方法2：名词短语识别**
```python
# 在收集上下文中的名词短语
"We collect personal information such as name, email"
  → 提取: "personal information", "name", "email"
```

**方法3：正则模式**
```python
# "such as X, Y, and Z" 模式
"data such as name, email, and phone number"
  → 提取: "name", "email", "phone number"
```

#### 2. 活动场景提取

**方法1：when/while/during模式**
```python
# 正则匹配
"when you register an account" → "register an account"
"while you browse the website" → "browse the website"
"during your purchase" → "your purchase"
```

**方法2：目的短语**
```python
# "for/to" 引导的目的
"We use data for marketing purposes" → "marketing purposes"
"We process data to improve services" → "improve services"
```

#### 3. 数据-活动映射

**句子级共现**
```python
原文: "When you register an account, we collect your name and email."

分析:
- 活动: "register an account"
- 数据: ["name", "email"]
- 映射: "register an account" → ["name", "email"]
```

---

## 💻 使用示例

### 命令行方式

```bash
# 基础分析
python tools/simple_local_analyze.py policy.txt

# 生成报告
python tools/simple_local_analyze.py policy.txt -o report.md

# 只显示摘要
python tools/simple_local_analyze.py policy.txt --show-summary-only

# 使用中文模型
python tools/simple_local_analyze.py policy_cn.txt --model zh_core_web_sm
```

### Python API方式

```python
from simple_local_analyzer import SimpleLocalAnalyzer

# 初始化
analyzer = SimpleLocalAnalyzer(model_name="en_core_web_sm")

# 读取隐私政策
with open("policy.txt", "r") as f:
    policy_text = f.read()

# 分析
results = analyzer.analyze(policy_text)

# 查看结果
print("数据类型:", results['data_types'])
print("活动场景:", results['activities'])

# 数据-活动映射
for mapping in results['mappings']:
    print(f"\n{mapping['activity']}:")
    print(f"  数据: {', '.join(mapping['data_types'])}")
    print(f"  出现次数: {mapping['occurrences']}")

# 生成报告
report = analyzer.generate_report(results)
print(report)
```

---

## 📊 输出格式

### 结果结构

```json
{
  "summary": {
    "total_segments": 172,
    "total_data_types": 31,
    "total_activities": 25,
    "total_mappings": 18
  },
  "data_types": [
    "name", "email", "phone number", "ip address",
    "browsing history", "location data", "payment information"
  ],
  "activities": [
    "register an account", "browse the website", "make a purchase",
    "use location services", "post content"
  ],
  "mappings": [
    {
      "activity": "register an account",
      "data_types": ["name", "email", "phone number"],
      "context": "When you register an account, we collect...",
      "occurrences": 5
    },
    {
      "activity": "browse the website",
      "data_types": ["ip address", "browsing history", "cookies"],
      "context": "While you browse the website, we automatically...",
      "occurrences": 8
    }
  ]
}
```

---

## 🔧 技术细节

### spaCy管道

```python
# spaCy处理流程
text → Tokenizer → Tagger → Parser → NER → Doc对象

# 我们使用的spaCy功能：
1. 词性标注 (POS Tagging) - 识别动词、名词
2. 依存句法分析 (Dependency Parsing) - 找主谓宾关系
3. 命名实体识别 (NER) - 识别组织、日期等
4. 名词短语识别 (Noun Chunks) - 提取完整短语
```

### 依存关系

```
句子: "We collect your email address"

依存树:
    collect (ROOT)
       ├── We (nsubj, 主语)
       └── address (dobj, 宾语)
              ├── your (poss, 所有格)
              └── email (compound, 复合词)

提取: "your email address" 完整名词短语
```

### 正则模式

```python
# 活动模式
when\s+(?:you|users?)\s+([^.,;]+)
while\s+(?:you|users?)\s+([^.,;]+)
during\s+(?:you|users?)\s+([^.,;]+)

# 列举模式
such\s+as\s+([^.,;]+)
including\s+([^.,;]+)
```

---

## ✅ 优势

1. **完全免费** - 无API成本
2. **本地运行** - 数据隐私安全
3. **无网络依赖** - 离线可用
4. **快速** - 本地处理，无网络延迟
5. **可控** - 规则透明，可调整

---

## ❌ 局限性

1. **准确性** - 依赖规则，不如LLM理解能力强
2. **复杂句式** - 对嵌套从句、长句处理较弱
3. **语义理解** - 无法理解隐含意思
4. **语言限制** - 每种语言需要单独的spaCy模型
5. **规则维护** - 需要手动调整规则和模式

---

## 📚 系统对比总结

### 三个版本对比

| 版本 | 代码量 | 成本 | 准确性 | 适用场景 |
|------|--------|------|--------|----------|
| **原完整系统** | 6,200行 | 免费 | 高 | 学术研究、合规审计 |
| **本地NLP简化版** | 500行 | 免费 | 中 | 快速分析、注重隐私 |
| **RAG版（LLM）** | 300行 | 低成本 | 高 | 快速原型、高准确性需求 |

### 选择建议

**选本地NLP版** 如果你：
- ✅ 不想花钱（完全免费）
- ✅ 注重数据隐私（本地运行）
- ✅ 无网络环境（离线可用）
- ✅ 需要可解释性（规则透明）

**选RAG版** 如果你：
- ✅ 追求高准确性（LLM理解强）
- ✅ 接受低成本（¥0.01/政策）
- ✅ 需要中文支持（LLM天然支持）
- ✅ 快速迭代（改prompt很简单）

**选原完整系统** 如果你：
- ✅ 学术研究（需要方法论支撑）
- ✅ 合规审计（需要PIPEDA分类）
- ✅ 大规模分析（>1000个政策）
- ✅ 风险评估（需要6因素模型）

---

## 🛠️ 扩展方向

### 1. 添加自定义规则

```python
# 在simple_local_analyzer.py中添加
self.custom_data_patterns = [
    r"(?:user|customer)\s+(?:id|identifier)",
    r"device\s+(?:fingerprint|signature)",
]
```

### 2. 支持更多语言

```bash
# 下载其他语言模型
python -m spacy download fr_core_news_sm  # 法语
python -m spacy download de_core_news_sm  # 德语
python -m spacy download es_core_news_sm  # 西班牙语
```

### 3. 提高准确性

- 使用更大的spaCy模型（`en_core_web_lg`）
- 添加更多正则模式
- 结合词向量相似度
- 添加后处理规则

---

## 📝 快速命令参考

```bash
# 分析
python tools/simple_local_analyze.py policy.txt

# 生成报告
python tools/simple_local_analyze.py policy.txt -o report.md

# 只看摘要
python tools/simple_local_analyze.py policy.txt --show-summary-only

# 中文分析
python tools/simple_local_analyze.py policy_cn.txt --model zh_core_web_sm

# 查看帮助
python tools/simple_local_analyze.py --help
```

---

## 🚀 立即开始

```bash
# 1分钟快速体验
pip install spacy
python -m spacy download en_core_web_sm
python tools/simple_local_analyze.py data/examples/facebook_policy.txt
```

---

**总结**: 如果你需要**完全免费、本地运行、注重隐私**的隐私政策分析，这个本地NLP版是最佳选择！
