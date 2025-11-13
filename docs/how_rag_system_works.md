# RAG系统运行原理详解

## 📚 目录
- [核心概念](#核心概念)
- [完整流程](#完整流程)
- [实际运行示例](#实际运行示例)
- [关键代码解析](#关键代码解析)
- [与原系统对比](#与原系统对比)

---

## 核心概念

### 什么是RAG？

**RAG = Retrieval-Augmented Generation（检索增强生成）**

传统方法：
```
隐私政策 → NLP管道（spaCy+SRL+规则） → 结果
```

RAG方法：
```
隐私政策 → 分块 → LLM提取 → 结果
```

### 本系统的RAG实现

```
┌─────────────────────────────────────────────────────────┐
│                    输入隐私政策文本                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  步骤1: 文档分块        │
         │  chunk_policy()        │
         │  按段落分割，每块2000字 │
         └────────┬───────────────┘
                  │
                  ▼
         ┌────────────────────────┐
         │  步骤2: 逐块LLM提取     │
         │  extract_with_llm()    │
         │  提取：                 │
         │  - 数据类型             │
         │  - 活动场景             │
         │  - 数据-活动映射        │
         └────────┬───────────────┘
                  │
                  ▼
         ┌────────────────────────┐
         │  步骤3: 结果合并        │
         │  去重、归并相同活动     │
         └────────┬───────────────┘
                  │
                  ▼
         ┌────────────────────────┐
         │  步骤4: 生成报告        │
         │  Markdown/Text格式     │
         └────────────────────────┘
```

---

## 完整流程

### 阶段1: 初始化 (init)

```python
analyzer = SimpleRAGAnalyzer(llm_provider="deepseek")
```

**发生了什么：**
1. 读取环境变量 `DEEPSEEK_API_KEY`
2. 初始化OpenAI客户端（DeepSeek使用OpenAI SDK）
3. 设置模型为 `deepseek-chat`

**代码位置：** `simple_rag_analyzer.py:32-82`

---

### 阶段2: 文档分块 (Chunking)

```python
chunks = analyzer.chunk_policy(policy_text, chunk_size=2000)
```

**为什么要分块？**
- LLM有token限制（DeepSeek最多64K tokens）
- 分块可以并行处理（虽然当前是串行）
- 更精准的提取（每块专注一个主题）

**分块策略：**
```python
# 1. 按双换行符分割段落
paragraphs = policy_text.split('\n\n')

# 2. 将段落组合成约2000字符的块
current_chunk = []
for paragraph in paragraphs:
    if len(current_chunk) + len(paragraph) > 2000:
        chunks.append('\n\n'.join(current_chunk))
        current_chunk = [paragraph]
    else:
        current_chunk.append(paragraph)
```

**示例：**
```
原文（5000字）
    ↓
块1: 注册和登录（1800字）
块2: 数据收集（2100字）
块3: 数据共享（1100字）
```

**代码位置：** `simple_rag_analyzer.py:84-116`

---

### 阶段3: LLM提取 (核心)

```python
for chunk in chunks:
    result = analyzer.extract_with_llm(chunk)
```

**这是最核心的步骤！**

#### 3.1 构建提示词 (Prompt)

```python
prompt = f"""请分析以下隐私政策文本，提取：
1. **数据类型** (Data Types): 收集了哪些用户数据？
2. **活动场景** (Activities): 在哪些活动/场景下收集数据？
3. **数据-活动映射**: 每个活动使用了哪些数据？

要求：
- 使用简洁的中文关键词
- 数据类型示例：姓名、邮箱、位置、浏览记录
- 活动场景示例：注册账号、浏览内容、购买商品

请以JSON格式返回：
{{
  "data_types": ["数据类型1", "数据类型2"],
  "activities": ["活动1", "活动2"],
  "mappings": [
    {{
      "activity": "活动名称",
      "data_types": ["数据1", "数据2"],
      "context": "原文相关片段"
    }}
  ]
}}

隐私政策文本：
{chunk}
"""
```

#### 3.2 调用LLM API

**DeepSeek示例：**
```python
response = self.client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是隐私政策分析专家"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.1  # 降低随机性
)

result_text = response.choices[0].message.content
```

#### 3.3 解析LLM返回

```python
# LLM返回示例
"""
```json
{
  "data_types": ["姓名", "邮箱", "手机号"],
  "activities": ["注册账号", "找回密码"],
  "mappings": [
    {
      "activity": "注册账号",
      "data_types": ["姓名", "邮箱", "手机号"],
      "context": "当您注册账号时，我们会收集..."
    }
  ]
}
```
"""

# 提取JSON
json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
if json_match:
    result_text = json_match.group(1)

# 解析
result = json.loads(result_text)
```

**代码位置：** `simple_rag_analyzer.py:118-176`

---

### 阶段4: 结果合并

```python
# 合并所有块的结果
all_data_types = set()
all_activities = set()
all_mappings = []

for chunk_result in chunk_results:
    all_data_types.update(chunk_result['data_types'])
    all_activities.update(chunk_result['activities'])
    all_mappings.extend(chunk_result['mappings'])

# 归并相同活动的映射
activity_data_map = {}
for mapping in all_mappings:
    activity = mapping['activity']
    if activity not in activity_data_map:
        activity_data_map[activity] = {
            "data_types": set(),
            "contexts": []
        }
    activity_data_map[activity]["data_types"].update(mapping['data_types'])
    activity_data_map[activity]["contexts"].append(mapping['context'])
```

**去重逻辑：**
- 使用 `set()` 自动去重数据类型和活动
- 相同活动的数据类型会合并
- 保留多个上下文示例

**代码位置：** `simple_rag_analyzer.py:178-237`

---

### 阶段5: 生成报告

```python
report = analyzer.generate_report(results, output_format="markdown")
```

**Markdown格式示例：**
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

**原文片段**: _当您注册账号时，我们会收集您的姓名、邮箱地址..._

---

### 浏览网站
**使用的数据**:
- IP地址
- 浏览记录
- 访问时间

**原文片段**: _当您浏览我们的网站时，我们会自动收集..._
```

**代码位置：** `simple_rag_analyzer.py:239-299`

---

## 实际运行示例

### 示例1: 命令行运行

```bash
# 设置API密钥
export DEEPSEEK_API_KEY="sk-xxx"

# 运行
python tools/simple_analyze.py policy.txt
```

**控制台输出：**
```
📖 读取文件: policy.txt
   文本长度: 5432 字符

🔧 初始化分析器 (使用 deepseek)...

============================================================
📄 分析隐私政策...
   分成 3 个块
   处理第 1/3 块...
   处理第 2/3 块...
   处理第 3/3 块...
✅ 分析完成！

============================================================

# 隐私政策分析报告

## 📊 分析摘要
- **数据类型**: 12 种
- **活动场景**: 8 个
- **数据-活动映射**: 10 条

## 📋 收集的数据类型
- 姓名
- 邮箱
- 手机号
- IP地址
- 浏览记录
...

## 🔗 数据-活动映射表

### 注册账号
**使用的数据**:
- 姓名
- 邮箱
- 手机号

============================================================
📊 分析摘要
============================================================
数据类型:     12 种
活动场景:     8 个
数据-活动映射: 10 条
============================================================
```

---

### 示例2: Python API运行

```python
from simple_rag_analyzer import SimpleRAGAnalyzer

# 1. 初始化
analyzer = SimpleRAGAnalyzer(llm_provider="deepseek")

# 2. 准备隐私政策
policy_text = """
当您注册账号时，我们会收集您的姓名、邮箱地址和手机号码。
这些信息用于创建您的账户并验证身份。

当您浏览网站时，我们会自动收集您的IP地址、浏览器类型和访问时间。
这些信息帮助我们改进网站性能。
"""

# 3. 分析
results = analyzer.analyze(policy_text)

# 4. 查看结果
print("数据类型:", results['data_types'])
# 输出: ['姓名', '邮箱', '手机号', 'IP地址', '浏览器类型', '访问时间']

print("活动场景:", results['activities'])
# 输出: ['注册账号', '浏览网站']

# 5. 数据-活动映射
for mapping in results['mappings']:
    print(f"\n{mapping['activity']}:")
    print(f"  数据: {', '.join(mapping['data_types'])}")
    print(f"  原文: {mapping['context'][:50]}...")
```

**输出：**
```
数据类型: ['姓名', '邮箱', '手机号', 'IP地址', '浏览器类型', '访问时间']
活动场景: ['注册账号', '浏览网站']

注册账号:
  数据: 姓名, 邮箱, 手机号
  原文: 当您注册账号时，我们会收集您的姓名、邮箱地址和手机号码...

浏览网站:
  数据: IP地址, 浏览器类型, 访问时间
  原文: 当您浏览网站时，我们会自动收集您的IP地址、浏览器...
```

---

## 关键代码解析

### 核心函数调用链

```
main()
  └─> analyzer.analyze(policy_text)
       ├─> chunk_policy()           # 分块
       ├─> extract_with_llm()       # LLM提取（每块）
       │    ├─> 构建prompt
       │    ├─> client.chat.completions.create()
       │    └─> 解析JSON返回
       ├─> 合并结果（去重）
       └─> 返回结果字典

analyzer.generate_report(results)
  └─> _generate_markdown_report()   # 格式化输出
```

---

### LLM提取的魔法

**输入（Chunk）：**
```
当您注册账号时，我们会收集您的姓名、邮箱地址和手机号码。
这些信息用于创建您的账户并验证身份。
```

**Prompt：**
```
请分析以下隐私政策文本，提取：
1. 数据类型
2. 活动场景
3. 数据-活动映射

[JSON格式要求...]

隐私政策文本：
当您注册账号时，我们会收集...
```

**LLM返回：**
```json
{
  "data_types": ["姓名", "邮箱", "手机号"],
  "activities": ["注册账号"],
  "mappings": [
    {
      "activity": "注册账号",
      "data_types": ["姓名", "邮箱", "手机号"],
      "context": "当您注册账号时，我们会收集您的姓名、邮箱地址和手机号码。"
    }
  ]
}
```

**解析后的Python对象：**
```python
{
    "data_types": ["姓名", "邮箱", "手机号"],
    "activities": ["注册账号"],
    "mappings": [
        DataActivityMapping(
            activity="注册账号",
            data_types=["姓名", "邮箱", "手机号"],
            context="当您注册账号时...",
            confidence=0.8
        )
    ]
}
```

---

## 与原系统对比

### 原系统（复杂NLP管道）

```
隐私政策文本
    ↓
spaCy NLP处理（词性标注、依存分析）
    ↓
语义角色标注（SRL）- 提取主谓宾
    ↓
Transformer增强（NER模型）
    ↓
PIPEDA分类器（10个原则）
    ↓
6因素风险评估模型
    ↓
生成详细报告
```

**优点：**
- ✅ 完全本地运行（免费）
- ✅ 高可解释性（每步可追溯）
- ✅ 学术严谨（方法论支撑）

**缺点：**
- ❌ 代码复杂（6,200行）
- ❌ 依赖多（15个包）
- ❌ 难以修改

---

### 新系统（RAG简化）

```
隐私政策文本
    ↓
文档分块
    ↓
LLM提取（每块独立）
    ↓
结果合并去重
    ↓
生成报告
```

**优点：**
- ✅ 极简代码（300行）
- ✅ 快速上手（无需NLP知识）
- ✅ 中文友好（LLM天然支持）
- ✅ 易于修改（调整prompt即可）

**缺点：**
- ❌ 需要API（有成本，虽然很低）
- ❌ 黑盒性（LLM内部不透明）
- ❌ 网络依赖

---

## 数据流详解

### 输入 → 输出全流程

```
┌─────────────────────────────────────────────┐
│  输入: policy.txt (5000字隐私政策)           │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  分块: [Chunk1(2000字), Chunk2(2100字),     │
│         Chunk3(900字)]                      │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  Chunk1 → LLM                               │
│  返回: {data_types: [姓名,邮箱],            │
│         activities: [注册],                 │
│         mappings: [...]}                    │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  Chunk2 → LLM                               │
│  返回: {data_types: [IP,浏览记录],          │
│         activities: [浏览],                 │
│         mappings: [...]}                    │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  Chunk3 → LLM                               │
│  返回: {data_types: [地址,支付信息],        │
│         activities: [购买],                 │
│         mappings: [...]}                    │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  合并去重:                                  │
│  all_data_types = {姓名,邮箱,IP,浏览记录,   │
│                     地址,支付信息}          │
│  all_activities = {注册,浏览,购买}          │
│  mappings归并后 = 3条                       │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  输出: 分析报告                             │
│  - 摘要: 6种数据，3个活动，3条映射          │
│  - 详细的数据-活动映射表                    │
└─────────────────────────────────────────────┘
```

---

## 常见问题

### Q1: 为什么要分块？直接把整个文档给LLM不行吗？

**A:** 可以，但有问题：
1. **Token限制** - LLM有最大token限制
2. **成本** - 长文本更贵
3. **准确性** - 分块可以让LLM专注于局部信息
4. **并行** - 未来可以并行处理多个块

### Q2: 如果LLM返回的JSON格式错误怎么办？

**A:** 代码有容错处理：
```python
try:
    result = json.loads(result_text)
except:
    print("LLM返回格式错误，返回空结果")
    return {"data_types": [], "activities": [], "mappings": []}
```

### Q3: 不同的块可能提取重复信息怎么办？

**A:** 使用`set()`自动去重：
```python
all_data_types = set()
for chunk_result in results:
    all_data_types.update(chunk_result['data_types'])
# set会自动去除重复项
```

### Q4: 如何控制LLM提取的质量？

**A:** 通过调整prompt：
1. **明确要求** - "使用简洁关键词"
2. **提供示例** - "如：姓名、邮箱"
3. **降低temperature** - 设置为0.1（更确定性）
4. **JSON schema** - 明确输出格式

---

## 总结

### RAG系统的本质

**传统方法：**
- 写大量规则 → 解析文本 → 提取信息
- 需要NLP专业知识
- 代码复杂难维护

**RAG方法：**
- 构建prompt → 让LLM理解 → 提取信息
- 无需NLP知识
- 代码简单易改

### 核心优势

1. **简单** - 300行代码
2. **灵活** - 改prompt即可调整
3. **准确** - LLM理解能力强
4. **通用** - 支持多语言

### 使用建议

- **小规模项目** → 用RAG（简单快速）
- **大规模/学术** → 用原系统（严谨可控）
- **原型验证** → 用RAG先试试
- **生产部署** → 根据需求选择

---

**下一步：** 尝试运行系统，查看实际效果！
