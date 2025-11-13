# 简化版 RAG 隐私政策分析方案

## 📌 核心理念

**从复杂到简单**：使用 RAG (Retrieval-Augmented Generation) 方法，专注于核心需求：
1. **提取数据类型** - 收集了哪些数据？
2. **提取活动场景** - 在哪些场景下使用数据？
3. **建立映射关系** - 哪个活动使用了哪些数据？

---

## 🔄 新旧系统对比

| 维度 | 原系统（复杂版） | 新系统（简化版） |
|------|------------------|------------------|
| **核心方法** | NLP管道（spaCy + Transformer + SRL） | LLM提取（RAG） |
| **分析框架** | PIPEDA 10原则 | 数据-活动映射 |
| **风险评估** | 6因素加权模型 | ❌ 无（专注数据映射） |
| **代码复杂度** | 约6,200行Python | 约300行Python |
| **依赖项** | 15个（spaCy, Transformers等） | 2个（openai/anthropic） |
| **准确性** | 高（多层提取） | 中高（依赖LLM） |
| **成本** | 免费（本地）+ 可选LLM | 需要LLM API（低成本） |
| **速度** | 5-15秒/政策（本地） | 10-30秒/政策（API调用） |
| **可解释性** | 高（每步可追溯） | 中（LLM黑盒） |
| **适用场景** | 学术研究、合规检查 | 快速原型、简单应用 |

---

## 🏗️ 系统架构

### 简化版架构

```
输入隐私政策文本
    ↓
文档分块 (Chunking)
    ↓
LLM提取 (每块独立提取)
  - 数据类型
  - 活动场景
  - 数据-活动映射
    ↓
结果合并与去重
    ↓
输出结构化结果
```

### 可选：加入向量数据库（RAG增强）

```
输入隐私政策文本
    ↓
文档分块 + 向量化
    ↓
存储到向量数据库 (ChromaDB/FAISS)
    ↓
用户查询: "什么活动使用了位置数据？"
    ↓
向量检索相关段落
    ↓
LLM基于检索内容回答
    ↓
输出答案
```

---

## 💻 使用方法

### 基础使用

```bash
# 分析隐私政策
python tools/simple_analyze.py policy.txt

# 生成报告
python tools/simple_analyze.py policy.txt -o report.md

# 使用不同的LLM
python tools/simple_analyze.py policy.txt --llm openai
```

### Python API

```python
from simple_rag_analyzer import SimpleRAGAnalyzer

# 初始化
analyzer = SimpleRAGAnalyzer(llm_provider="deepseek")

# 分析
results = analyzer.analyze(policy_text)

# 输出结果
print(f"数据类型: {results['data_types']}")
print(f"活动场景: {results['activities']}")

# 查看映射
for mapping in results['mappings']:
    print(f"{mapping['activity']}: {mapping['data_types']}")
```

---

## 📊 输出示例

### 分析结果结构

```json
{
  "summary": {
    "total_chunks": 5,
    "total_data_types": 12,
    "total_activities": 8,
    "total_mappings": 10
  },
  "data_types": [
    "姓名", "邮箱", "手机号", "IP地址", "浏览记录",
    "收货地址", "支付信息", "发布内容"
  ],
  "activities": [
    "注册账号", "浏览网站", "购买商品", "发布内容",
    "客服咨询", "广告推送", "数据分析", "安全防护"
  ],
  "mappings": [
    {
      "activity": "注册账号",
      "data_types": ["姓名", "邮箱", "手机号"],
      "context": "当您注册账号时，我们会收集您的姓名、邮箱...",
      "confidence": 0.8
    },
    {
      "activity": "购买商品",
      "data_types": ["收货地址", "支付信息"],
      "context": "当您购买商品时，我们会收集...",
      "confidence": 0.8
    }
  ]
}
```

### Markdown报告示例

```markdown
# 隐私政策分析报告

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

**原文片段**: _当您注册账号时，我们会收集您的姓名、邮箱地址和手机号码..._

---

### 购买商品
**使用的数据**:
- 收货地址
- 支付信息

**原文片段**: _当您购买商品时，我们会收集您的收货地址和支付信息..._
```

---

## 🚀 可选增强：向量数据库集成

### 为什么需要向量数据库？

1. **大文档处理** - 隐私政策可能很长（>50KB）
2. **精准检索** - 只提取相关段落给LLM，降低成本
3. **交互式查询** - 支持用户提问（如："哪些活动使用了位置数据？"）

### 集成方案

#### 选项1: ChromaDB（推荐，简单易用）

```python
import chromadb
from chromadb.utils import embedding_functions

class RAGAnalyzerWithVectorDB(SimpleRAGAnalyzer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 初始化ChromaDB
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(
            name="privacy_policies",
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )

    def index_policy(self, policy_text: str, policy_id: str):
        """将隐私政策分块并索引到向量数据库"""
        chunks = self.chunk_policy(policy_text)

        # 添加到向量数据库
        self.collection.add(
            documents=chunks,
            ids=[f"{policy_id}_{i}" for i in range(len(chunks))],
            metadatas=[{"chunk_id": i, "policy_id": policy_id}
                      for i in range(len(chunks))]
        )

    def query(self, question: str, n_results: int = 3):
        """根据问题检索相关段落并回答"""
        # 向量检索
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results
        )

        # 合并检索到的段落
        context = "\n\n".join(results['documents'][0])

        # 用LLM回答
        prompt = f"""基于以下隐私政策内容回答问题：

问题: {question}

相关内容:
{context}

请简洁回答，并引用原文。
"""
        # 调用LLM...
        return self.extract_with_llm(prompt)
```

**使用示例**:

```python
analyzer = RAGAnalyzerWithVectorDB(llm_provider="deepseek")

# 索引隐私政策
analyzer.index_policy(policy_text, policy_id="facebook_v1")

# 查询
answer = analyzer.query("什么活动使用了位置数据？")
print(answer)
```

#### 选项2: FAISS（适合大规模，更快）

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class RAGAnalyzerWithFAISS(SimpleRAGAnalyzer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 初始化embedding模型
        self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        # FAISS索引
        self.index = None
        self.chunks = []

    def index_policy(self, policy_text: str):
        """索引隐私政策到FAISS"""
        chunks = self.chunk_policy(policy_text)
        self.chunks = chunks

        # 生成embeddings
        embeddings = self.encoder.encode(chunks)

        # 创建FAISS索引
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))

    def query(self, question: str, k: int = 3):
        """检索相关段落"""
        # 查询向量
        query_vec = self.encoder.encode([question])

        # 检索
        D, I = self.index.search(np.array(query_vec).astype('float32'), k)

        # 返回最相关的段落
        results = [self.chunks[i] for i in I[0]]
        return results
```

---

## 📦 依赖安装

### 基础版（仅LLM）

```bash
pip install openai        # DeepSeek/OpenAI
# 或
pip install anthropic     # Claude
```

### 增强版（加向量数据库）

```bash
# ChromaDB方案
pip install chromadb

# FAISS方案
pip install faiss-cpu sentence-transformers
```

---

## 💰 成本估算

### DeepSeek（推荐，低成本）

- **价格**: ¥1/百万tokens（输入）, ¥2/百万tokens（输出）
- **单个政策**: 约5,000 tokens → ¥0.01-0.05
- **100个政策**: 约¥1-5

### OpenAI GPT-4o-mini

- **价格**: $0.15/百万tokens（输入）, $0.6/百万tokens（输出）
- **单个政策**: 约$0.01-0.05
- **100个政策**: 约$1-5

### Claude 3.5 Sonnet

- **价格**: $3/百万tokens（输入）, $15/百万tokens（输出）
- **单个政策**: 约$0.05-0.20
- **100个政策**: 约$5-20

**建议**: 开发阶段使用DeepSeek，生产环境根据质量要求选择。

---

## ✅ 优势 vs ❌ 劣势

### ✅ 简化版优势

1. **极简代码** - 300行 vs 6,200行
2. **快速上手** - 无需NLP知识
3. **灵活扩展** - 容易添加新功能
4. **中文友好** - LLM天然支持多语言
5. **易于维护** - 无复杂规则库

### ❌ 简化版劣势

1. **需要API** - 无法完全本地运行
2. **成本** - 每次分析需付费（虽然很低）
3. **黑盒** - LLM提取过程不透明
4. **依赖网络** - API调用需联网
5. **一致性** - LLM输出可能有波动

---

## 🎯 使用建议

### 适合简化版的场景

- ✅ 原型开发、MVP
- ✅ 小规模分析（<100个政策/月）
- ✅ 对可解释性要求不高
- ✅ 需要快速迭代

### 适合原系统的场景

- ✅ 学术研究（需要方法论支撑）
- ✅ 大规模分析（>1000个政策）
- ✅ 完全本地部署（无API依赖）
- ✅ 高可解释性要求（监管审计）

---

## 🔧 扩展方向

### 1. 添加缓存机制

```python
import hashlib
import json

def analyze_with_cache(self, policy_text: str):
    # 计算文本哈希
    text_hash = hashlib.md5(policy_text.encode()).hexdigest()
    cache_file = f"cache/{text_hash}.json"

    # 检查缓存
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)

    # 分析并缓存
    results = self.analyze(policy_text)
    os.makedirs('cache', exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(results, f)

    return results
```

### 2. 批量分析

```python
def batch_analyze(self, policy_files: List[str], max_workers: int = 3):
    """并行分析多个隐私政策"""
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(self._analyze_file, policy_files)

    return list(results)
```

### 3. Web UI

```python
# 使用Streamlit快速构建UI
import streamlit as st

st.title("隐私政策分析器")

policy_text = st.text_area("粘贴隐私政策文本", height=300)

if st.button("分析"):
    analyzer = SimpleRAGAnalyzer()
    results = analyzer.analyze(policy_text)

    st.subheader("数据类型")
    st.write(results['data_types'])

    st.subheader("活动场景")
    st.write(results['activities'])

    st.subheader("数据-活动映射")
    for m in results['mappings']:
        st.write(f"**{m['activity']}**: {', '.join(m['data_types'])}")
```

---

## 📚 参考资料

- [DeepSeek API文档](https://platform.deepseek.com/api-docs/)
- [OpenAI API文档](https://platform.openai.com/docs)
- [ChromaDB文档](https://docs.trychroma.com/)
- [FAISS文档](https://github.com/facebookresearch/faiss)
- [RAG原理介绍](https://arxiv.org/abs/2005.11401)

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install openai

# 2. 设置API密钥
export DEEPSEEK_API_KEY="sk-xxx"

# 3. 运行分析
python tools/simple_analyze.py data/examples/facebook_policy.txt

# 4. 查看报告
cat simple_analysis_report.md
```

---

**总结**: 简化版适合快速原型和小规模应用，原系统适合学术研究和生产级部署。根据需求选择！
