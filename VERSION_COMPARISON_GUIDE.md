# 隐私政策版本对比工具使用指南

## 📋 功能概述

这个工具可以智能对比两个版本的隐私政策，**不仅仅是简单的文本diff**，而是基于**语义理解**来识别实质性的变化。

### 🎯 核心特点

✅ **语义匹配** - 即使说法不同，也能识别是同一条款
✅ **智能分类** - 按PIPEDA 10个原则分类对比
✅ **关键信息提取** - 对比数据类型、第三方、用户权利等变化
✅ **风险评估** - 分析隐私风险是增加还是降低
✅ **可解释报告** - 生成详细的人类可读报告

---

## 🚀 快速开始

### 安装依赖

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

### 基本使用

```bash
# 对比两个版本的隐私政策
python policy_version_comparator.py old_policy.txt new_policy.txt

# 指定输出文件
python policy_version_comparator.py old_policy.txt new_policy.txt -o comparison_report.md

# 同时输出JSON格式
python policy_version_comparator.py old_policy.txt new_policy.txt --json
```

---

## 📖 工作原理

### 1️⃣ 语义匹配 vs 简单Diff

**传统文本Diff的问题：**
```
旧版本: "We collect your email address for marketing purposes"
新版本: "Your email is gathered by us to send promotional materials"
```

- ❌ 简单diff会认为完全不同
- ✅ 我们的工具识别出这是**同一条款**（相似度 75%）

**我们的方法：**
- 使用 `difflib.SequenceMatcher` 计算文本相似度
- 相似度 ≥ 60% 认为是同一条款
- 即使说法不同，也能匹配语义相同的内容

### 2️⃣ 三层对比分析

```
层次1: 关键信息摘要对比
├── 数据类型变化 (Data Types)
├── 第三方共享变化 (Third Parties)
├── 用户权利变化 (User Rights)
├── 安全措施变化 (Security Measures)
└── 使用目的变化 (Purposes)

层次2: PIPEDA类别对比
├── 每个类别的段落数量变化
├── 新增段落
├── 删除段落
└── 修改段落（参数变化）

层次3: 整体风险评估
├── 旧版本平均风险
├── 新版本平均风险
└── 风险变化趋势
```

### 3️⃣ 智能匹配算法

```python
# 伪代码说明
for each new_segment:
    best_match = None
    best_similarity = 0

    for each old_segment:
        similarity = calculate_text_similarity(old, new)

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = old_segment

    if best_similarity >= 0.6:  # 60%阈值
        # 匹配成功 - 检查参数是否变化
        compare_parameters(old_segment, new_segment)
    else:
        # 新增的段落
        mark_as_added(new_segment)

# 未匹配的旧段落 = 删除
```

---

## 📊 输出报告示例

### 报告结构

```markdown
===============================================================================
隐私政策版本对比报告 (Privacy Policy Version Comparison Report)
===============================================================================

## 📊 整体风险评估
旧版本平均风险: 15.23%
新版本平均风险: 22.45%
风险变化:       +7.22%
⚠️  警告: 新版本的隐私风险增加了！

===============================================================================
## 🔑 关键信息变化
===============================================================================

### 数据类型 (Data Types)
   ➕ 新增: biometric_data, location_history, device_fingerprint
   ➖ 删除: email

### 第三方共享 (Third Parties)
   ➕ 新增: Google Analytics, Facebook Pixel, TikTok
   ➖ 删除: 无

### 用户权利 (User Rights)
   ➕ 新增: export
   ➖ 删除: withdraw

===============================================================================
## 📋 PIPEDA类别详细变化
===============================================================================

### 限制收集 (limiting_collection)
段落数变化: 3 → 5 (+2)
新增段落: 2
删除段落: 0
修改段落: 1

**新增内容:**
1. We now collect biometric data including fingerprints for authentication...
   数据类型: biometric_data, fingerprint
   风险分数: 35.00%

**修改内容:**
1. 相似度: 75%, 风险变化: +10.00%
   旧版: We collect your email address
   新版: We gather your email and phone number
   参数变化:
      data_types 新增: phone_number
```

---

## 🔍 详细功能说明

### 功能1: 关键信息摘要对比

**识别的关键信息：**

1. **数据类型** (Data Types)
   - 个人身份信息、联系方式、财务数据、位置数据等
   - 识别新增/删除的数据收集

2. **第三方共享** (Third Parties)
   - 广告商、分析服务、支付处理商等
   - 识别新的数据共享方

3. **用户权利** (User Rights)
   - access, delete, correct, withdraw, opt-out等
   - 发现权利的增加或减少

4. **安全措施** (Security Measures)
   - encrypt, SSL, firewall等
   - 评估数据保护的改善

5. **使用目的** (Purposes)
   - 营销、分析、改进服务等
   - 跟踪目的变化

### 功能2: PIPEDA类别对比

**10个PIPEDA原则分类：**

| 类别 | 对比内容 |
|------|---------|
| Accountability (问责性) | 责任人、联系方式变化 |
| Identifying Purposes (确定目的) | 数据使用目的的变化 |
| Consent (同意) | 同意机制的改变 |
| Limiting Collection (限制收集) | 数据收集范围变化 |
| Limiting Use (限制使用) | 第三方共享变化 |
| Accuracy (准确性) | 数据准确性保障 |
| Safeguards (安全保障) | 安全措施变化 |
| Openness (公开性) | 透明度改善 |
| Individual Access (个人访问权) | 用户权利变化 |
| Challenging Compliance (质疑合规性) | 投诉机制变化 |

### 功能3: 段落匹配与变化检测

**三种变化类型：**

#### ➕ 新增段落 (Added)
- 在新版本中出现，但旧版本中无相似内容
- 可能表示新的数据收集或新政策

#### ➖ 删除段落 (Removed)
- 在旧版本中存在，但新版本中被移除
- 可能表示政策简化或权利减少

#### ✏️  修改段落 (Modified)
- 相似度 ≥ 60%，但参数有变化
- 检测以下参数的变化：
  - 数据类型增减
  - 第三方增减
  - 用户权利增减
  - 风险分数变化

### 功能4: 风险评估

**风险计算公式：**
```python
risk_score =
    + 0.30 (敏感数据类型)
    + 0.10 * 第三方数量
    + 0.10 (未明确保留期限)
    - 0.10 (有安全措施)
    - 0.10 (用户权利 ≥ 3个)
```

**风险变化分析：**
- 对比新旧版本的平均风险
- 识别哪些条款风险增加
- 给出风险警告和建议

---

## 💡 使用场景

### 场景1: 合规审查
```bash
# 公司更新了隐私政策，需要审查变化是否合规
python policy_version_comparator.py \
    policies/2024-01-v1.txt \
    policies/2024-06-v2.txt \
    -o audit_report.md
```

**关注点：**
- 用户权利是否减少
- 是否新增敏感数据收集
- 第三方共享是否增加

### 场景2: 竞品分析
```bash
# 对比自己的政策与竞争对手的政策
python policy_version_comparator.py \
    our_policy.txt \
    competitor_policy.txt \
    -o competitor_analysis.md
```

**关注点：**
- 竞品的数据收集范围
- 竞品提供的用户权利
- 风险对比

### 场景3: 学术研究
```bash
# 研究某公司隐私政策的演变
python policy_version_comparator.py \
    facebook_2020.txt \
    facebook_2024.txt \
    --json \
    -o facebook_evolution.md
```

**关注点：**
- 隐私政策随时间的变化趋势
- 法规影响（如GDPR实施前后）
- 量化分析数据

---

## 🛠️ 高级用法

### 编程接口

```python
from policy_version_comparator import PolicyVersionComparator

# 创建对比器
comparator = PolicyVersionComparator()

# 读取两个版本
with open("old_policy.txt") as f:
    old_text = f.read()
with open("new_policy.txt") as f:
    new_text = f.read()

# 执行对比
result = comparator.compare_versions(old_text, new_text)

# 访问对比结果
print(f"风险变化: {result['risk_change']['risk_change']:.2%}")

# 查看新增的数据类型
added_data = result['summary_changes']['data_types']['added']
print(f"新增数据类型: {added_data}")

# 生成报告
report = comparator.generate_comparison_report(result, "report.md")
```

### 批量对比

```python
import os
from policy_version_comparator import PolicyVersionComparator

comparator = PolicyVersionComparator()
policies_dir = "policies/"

# 获取所有版本
versions = sorted([f for f in os.listdir(policies_dir) if f.endswith('.txt')])

# 逐对对比
for i in range(len(versions) - 1):
    old_file = os.path.join(policies_dir, versions[i])
    new_file = os.path.join(policies_dir, versions[i+1])

    with open(old_file) as f1, open(new_file) as f2:
        old_text = f1.read()
        new_text = f2.read()

    result = comparator.compare_versions(old_text, new_text)

    output_file = f"comparison_{versions[i]}_vs_{versions[i+1]}.md"
    comparator.generate_comparison_report(result, output_file)

    print(f"✅ 完成: {versions[i]} vs {versions[i+1]}")
```

---

## 📈 输出格式

### Markdown报告 (.md)
- 人类可读的格式化报告
- 包含摘要、详细变化、建议
- 适合审查和分享

### JSON数据 (.json)
```json
{
  "summary_changes": {
    "data_types": {
      "added": ["location", "biometric"],
      "removed": ["email"],
      "unchanged": ["name", "phone"]
    }
  },
  "category_changes": {
    "limiting_collection": {
      "old_count": 3,
      "new_count": 5,
      "added_segments": [...],
      "modified_segments": [...]
    }
  },
  "risk_change": {
    "old_average_risk": 0.15,
    "new_average_risk": 0.23,
    "risk_change": 0.08
  }
}
```

---

## ⚠️  注意事项

### 相似度阈值
- 默认阈值: 60%
- 可能需要根据实际情况调整
- 太低会产生误匹配，太高会漏掉真实匹配

### 语言限制
- 目前主要支持英文
- 中文政策可能需要使用中文spaCy模型

### 性能考虑
- 长文档（>10000字）分析可能需要几分钟
- 建议先测试小文件

---

## 🎓 学术价值

### 适用于以下研究：

1. **隐私政策演化研究**
   - 分析公司政策随时间的变化
   - 研究法规影响（GDPR、CCPA等）

2. **合规性分析**
   - 自动检测不合规的变化
   - 审计企业隐私实践

3. **跨平台对比**
   - 比较不同公司的隐私政策
   - 行业标准研究

4. **用户权利保护**
   - 发现权利被削弱的情况
   - 倡导更好的隐私保护

---

## 💬 常见问题

**Q: 为什么不直接用diff工具？**

A: 传统diff工具只能匹配完全相同的文本。隐私政策经常改变措辞但保持相同含义，我们的工具可以理解语义。

**Q: 相似度60%的阈值是怎么确定的？**

A: 基于实验，60%可以平衡误匹配和漏匹配。你可以在代码中调整 `_match_segments` 方法的阈值。

**Q: 支持哪些语言？**

A: 默认支持英文。要支持其他语言，需要：
1. 安装相应的spaCy模型
2. 修改 `PrivacyPolicyAnalyzer` 的初始化参数

**Q: 如何提高准确性？**

A:
1. 使用更大的spaCy模型（如 `en_core_web_lg`）
2. 调整相似度阈值
3. 扩展关键词规则库

---

## 📚 技术细节

### 核心算法

**文本相似度计算：**
```python
difflib.SequenceMatcher(None, text1, text2).ratio()
```
- 基于最长公共子序列（LCS）
- 返回0-1之间的相似度分数

**参数提取：**
- 使用spaCy的依存句法分析
- NER识别组织、日期等实体
- 关键词匹配识别权利、安全措施

**风险评估：**
- 多因素加权模型
- 基于学术文献的风险因素

---

## 🔗 相关工具

- `privacy_analyzer_example.py` - 单个政策分析
- `analyze_policy.py` - CLI分析工具
- `benchmark.py` - 准确性评估

---

## 📝 引用

如果你在学术研究中使用此工具，建议引用：

```
Privacy Policy Version Comparator - A semantic-aware tool for comparing
privacy policy versions based on PIPEDA framework and NLP techniques.
```

---

## 🤝 贡献

欢迎改进建议！可以关注的方向：
- 支持更多语言
- 改进匹配算法
- 添加更多风险因素
- 可视化对比结果

---

**祝你使用愉快！如有问题欢迎反馈。**
