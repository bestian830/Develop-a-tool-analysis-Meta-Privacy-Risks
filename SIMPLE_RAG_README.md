# 简化版 RAG 隐私政策分析器

> 使用 LLM + RAG 方法，专注于核心需求：**数据收集**和**活动-数据映射**

---

## 🎯 核心功能

### 只做3件事：
1. **提取数据类型** - 收集了哪些数据？
2. **提取活动场景** - 在什么情况下收集？
3. **建立映射关系** - 哪个活动使用了哪些数据？

### 输出示例

```markdown
## 数据-活动映射表

### 注册账号
**使用的数据**: 姓名、邮箱、手机号

### 浏览网站
**使用的数据**: IP地址、浏览记录、访问时间

### 购买商品
**使用的数据**: 收货地址、支付信息
```

---

## 🚀 快速开始（3步）

### 1. 安装依赖

```bash
# 基础版（只需要LLM）
pip install openai

# 可选：向量数据库增强
pip install chromadb
```

### 2. 设置API密钥

```bash
# DeepSeek（推荐，便宜）
export DEEPSEEK_API_KEY="sk-xxx"

# 或 OpenAI
export OPENAI_API_KEY="sk-xxx"

# 或 Claude
export ANTHROPIC_API_KEY="sk-xxx"
```

### 3. 运行分析

```bash
# 基础分析
python tools/simple_analyze.py policy.txt

# 生成报告
python tools/simple_analyze.py policy.txt -o report.md

# 使用不同LLM
python tools/simple_analyze.py policy.txt --llm openai
```

---

## 📖 使用示例

### 命令行方式

```bash
# 分析本地文件
python tools/simple_analyze.py data/examples/facebook_policy.txt

# 从URL抓取并分析
python tools/simple_analyze.py --url https://example.com/privacy

# 生成Markdown报告
python tools/simple_analyze.py policy.txt -o report.md -f markdown
```

### Python API方式

```python
from simple_rag_analyzer import SimpleRAGAnalyzer

# 初始化
analyzer = SimpleRAGAnalyzer(llm_provider="deepseek")

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
    print(f"  使用数据: {', '.join(mapping['data_types'])}")
```

### 交互式查询（向量数据库增强）

```python
from rag_with_vectordb import RAGAnalyzerWithVectorDB

# 初始化（需要安装chromadb）
analyzer = RAGAnalyzerWithVectorDB(
    llm_provider="deepseek",
    vectordb_type="chroma"
)

# 索引隐私政策
analyzer.index_policy(policy_text, policy_id="myapp_v1")

# 查询
result = analyzer.query("什么活动使用了位置数据？")
print(result['answer'])

# 或交互式查询
analyzer.interactive_query(policy_text)
# 然后可以不断输入问题查询
```

---

## 📊 与原系统对比

| 对比项 | 原系统 | 简化版 |
|--------|--------|--------|
| **代码量** | 6,200行 | 300行 |
| **依赖** | 15个包 | 1-2个包 |
| **分析方法** | NLP管道（spaCy+Transformer+SRL） | LLM提取 |
| **框架** | PIPEDA 10原则 + 6因素风险评估 | 数据-活动映射 |
| **成本** | 免费（本地） | ¥0.01-0.05/政策 |
| **速度** | 5-15秒 | 10-30秒 |
| **准确性** | 高 | 中高 |
| **可解释性** | 高（每步可追溯） | 中（LLM黑盒） |
| **适用场景** | 学术研究、合规审计 | 快速原型、简单应用 |

---

## 💰 成本

### DeepSeek（推荐）
- **单个政策**: ¥0.01-0.05
- **100个政策**: ¥1-5
- **1000个政策**: ¥10-50

### OpenAI GPT-4o-mini
- **单个政策**: $0.01-0.05
- **100个政策**: $1-5

### Claude 3.5 Sonnet
- **单个政策**: $0.05-0.20（较贵，质量高）

---

## 📂 文件结构

```
项目根目录/
├── src/
│   ├── simple_rag_analyzer.py      # 基础版分析器 ⭐
│   └── rag_with_vectordb.py        # 向量数据库增强版 ⭐
│
├── tools/
│   └── simple_analyze.py           # 命令行工具 ⭐
│
├── docs/
│   └── simplified_rag_approach.md  # 详细文档 ⭐
│
└── SIMPLE_RAG_README.md            # 本文件
```

---

## ✅ 优势

1. **极简代码** - 300行 vs 6,200行
2. **快速上手** - 无需NLP背景
3. **中文友好** - LLM天然支持多语言
4. **易于扩展** - 可添加向量数据库、缓存等
5. **灵活适配** - 容易调整提示词改变输出

---

## ❌ 局限性

1. **需要API** - 无法完全本地运行（有成本）
2. **黑盒性** - LLM提取过程不透明
3. **网络依赖** - 需要联网调用API
4. **一致性** - LLM输出可能有波动

---

## 🔧 扩展功能

### 1. 向量数据库集成

```bash
# 安装ChromaDB
pip install chromadb

# 使用增强版
python -c "
from rag_with_vectordb import RAGAnalyzerWithVectorDB
analyzer = RAGAnalyzerWithVectorDB(llm_provider='deepseek')
analyzer.interactive_query(open('policy.txt').read())
"
```

### 2. 批量分析

```python
from simple_rag_analyzer import SimpleRAGAnalyzer
from pathlib import Path

analyzer = SimpleRAGAnalyzer()

for policy_file in Path("policies/").glob("*.txt"):
    print(f"分析: {policy_file}")
    with open(policy_file) as f:
        results = analyzer.analyze(f.read())

    # 保存报告
    report = analyzer.generate_report(results)
    output_file = f"reports/{policy_file.stem}_report.md"
    with open(output_file, 'w') as f:
        f.write(report)
```

### 3. Web界面（Streamlit）

```bash
# 安装Streamlit
pip install streamlit

# 创建app.py
```

```python
import streamlit as st
from simple_rag_analyzer import SimpleRAGAnalyzer

st.title("🔍 隐私政策分析器")

policy_text = st.text_area("粘贴隐私政策文本:", height=300)

if st.button("开始分析"):
    analyzer = SimpleRAGAnalyzer()
    results = analyzer.analyze(policy_text)

    st.subheader("📊 数据类型")
    st.write(results['data_types'])

    st.subheader("🎯 活动场景")
    st.write(results['activities'])

    st.subheader("🔗 数据-活动映射")
    for m in results['mappings']:
        with st.expander(m['activity']):
            st.write("**使用的数据:**")
            st.write(m['data_types'])
            st.write("**原文片段:**")
            st.write(m['context'])
```

```bash
# 运行
streamlit run app.py
```

---

## 📝 输出格式

### JSON格式

```json
{
  "summary": {
    "total_chunks": 5,
    "total_data_types": 12,
    "total_activities": 8,
    "total_mappings": 10
  },
  "data_types": [
    "姓名", "邮箱", "手机号", "IP地址",
    "浏览记录", "位置信息", "支付信息"
  ],
  "activities": [
    "注册账号", "浏览网站", "购买商品",
    "发布内容", "使用位置服务"
  ],
  "mappings": [
    {
      "activity": "注册账号",
      "data_types": ["姓名", "邮箱", "手机号"],
      "context": "当您注册账号时...",
      "confidence": 0.8
    }
  ]
}
```

### Markdown格式

详见生成的报告文件，包含：
- 📊 分析摘要
- 📋 数据类型列表
- 🎯 活动场景列表
- 🔗 数据-活动映射表（核心）

---

## 🎯 使用场景

### ✅ 适合简化版

- 快速原型开发
- 小规模分析（<100个政策/月）
- 不需要严格的可解释性
- 个人项目、创业MVP

### ✅ 适合原系统

- 学术研究（需要方法论）
- 大规模分析（>1000个政策）
- 完全本地部署
- 监管合规审计

---

## 📚 相关文档

- [详细说明文档](./docs/simplified_rag_approach.md) - 完整方法论和扩展方案
- [原系统文档](./README.md) - 基于NLP的完整系统
- [向量数据库增强](./src/rag_with_vectordb.py) - 支持交互式查询

---

## ❓ 常见问题

### Q: 为什么要简化？
A: 原系统功能强大但复杂（6,200行代码，15个依赖）。简化版只保留核心功能（数据-活动映射），代码量减少95%，更易理解和维护。

### Q: 准确性如何？
A: LLM提取的准确性取决于模型质量。DeepSeek/GPT-4o-mini对于常见隐私政策准确率约80-90%，Claude 3.5可达90-95%。对于复杂法律术语可能需要人工校验。

### Q: 可以完全本地运行吗？
A: 简化版需要调用LLM API，无法完全本地。如需本地运行，请使用原系统或自建LLM（如Ollama + LLaMA）。

### Q: 成本会很高吗？
A: 使用DeepSeek，单个政策约¥0.01-0.05，100个政策约¥1-5，成本很低。可通过缓存机制进一步降低成本。

### Q: 如何提高准确性？
A:
1. 使用更好的模型（Claude > GPT-4o > DeepSeek）
2. 优化提示词（prompt engineering）
3. 添加少样本示例（few-shot learning）
4. 人工校验关键结果

---

## 🚀 立即开始

```bash
# 1分钟快速体验
pip install openai
export DEEPSEEK_API_KEY="sk-xxx"
python tools/simple_analyze.py data/examples/facebook_policy.txt
```

---

## 📞 技术支持

遇到问题？查看：
1. [详细文档](./docs/simplified_rag_approach.md)
2. [原项目README](./README.md)
3. 提Issue到GitHub仓库

---

**总结**: 如果你需要快速实现隐私政策分析，这个简化版是最佳选择！
