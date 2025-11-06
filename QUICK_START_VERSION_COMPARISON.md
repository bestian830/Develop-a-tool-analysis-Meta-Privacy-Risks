# 版本对比工具 - 快速开始指南

## 🚀 如何运行脚本

### 方法1: 使用命令行（推荐）

```bash
# 基本用法
python policy_version_comparator.py 旧版本文件.txt 新版本文件.txt

# 示例：对比我们提供的示例文件
python policy_version_comparator.py example_policy_v1.txt example_policy_v2.txt

# 指定输出文件名
python policy_version_comparator.py example_policy_v1.txt example_policy_v2.txt -o my_report.md

# 同时生成JSON格式的详细数据
python policy_version_comparator.py example_policy_v1.txt example_policy_v2.txt --json
```

### 方法2: 在Python代码中使用

```python
from policy_version_comparator import PolicyVersionComparator

# 创建对比器
comparator = PolicyVersionComparator()

# 读取两个版本
with open("example_policy_v1.txt", encoding="utf-8") as f:
    old_text = f.read()

with open("example_policy_v2.txt", encoding="utf-8") as f:
    new_text = f.read()

# 执行对比
result = comparator.compare_versions(old_text, new_text)

# 生成报告
comparator.generate_comparison_report(result, "my_comparison.md")

# 访问对比数据
print(f"风险变化: {result['risk_change']['risk_change']:.2%}")
print(f"新增数据类型: {result['summary_changes']['data_types']['added']}")
```

---

## 📁 项目文件说明

### 核心文件：
- `policy_version_comparator.py` - 版本对比工具（主程序）
- `privacy_analyzer_example.py` - 隐私政策分析器（依赖）

### 示例文件：
- `example_policy_v1.txt` - 示例隐私政策版本1（2024年1月）
- `example_policy_v2.txt` - 示例隐私政策版本2（2024年6月）

### 文档：
- `VERSION_COMPARISON_GUIDE.md` - 详细使用指南
- `QUICK_START_VERSION_COMPARISON.md` - 本文档

### 输出文件：
- `version_comparison_report.md` - 生成的对比报告

---

## 📊 输出报告解读

运行脚本后会看到这样的终端输出：

```
📊 对比摘要:
================================================================================
风险变化: 14.29% → 8.75% (-5.54%)

新增数据类型: 2
新增第三方: 2
新增用户权利: 3
删除的用户权利: 1
```

**说明：**
- **风险变化**: 负数表示风险降低，正数表示风险增加
- **新增数据类型**: 新版本收集了哪些额外的数据
- **新增第三方**: 新版本与哪些新的第三方共享数据
- **新增/删除用户权利**: 用户权利的变化

---

## 📄 生成的报告内容

报告文件（`version_comparison_report.md`）包含：

### 1. 整体风险评估
```
旧版本平均风险: 14.29%
新版本平均风险: 8.75%
风险变化:       -5.54%
✅ 新版本的隐私风险降低或保持不变
```

### 2. 关键信息变化摘要
- ➕ 新增的数据类型、第三方、用户权利等
- ➖ 删除的内容

### 3. PIPEDA类别详细变化
按10个原则分类显示：
- 新增段落
- 删除段落
- 修改段落
- 参数变化

### 4. 总结与建议
自动生成的合规建议，例如：
- ⚠️ 风险警告
- 📊 数据收集提醒
- ✅ 改进建议

---

## 🔍 示例报告分析

查看生成的 `version_comparison_report.md`，你会看到：

### ✅ 好的变化：
- 新增用户权利：`correct`, `export`, `withdraw`
- 新增安全措施：`HTTPS`, `authentication`, `firewalls`
- 整体风险下降 5.54%

### ⚠️  需要关注的变化：
- 删除了用户权利：`delete`（可能违反GDPR）
- 新增第三方：`TikTok`（需要审查数据共享协议）
- 数据保留期限变更：30天 → 无限期/5年

---

## 🎯 实际使用场景

### 场景1: 审查公司政策更新
```bash
# 对比公司本季度的政策变化
python policy_version_comparator.py \
    company_policy_2024Q1.txt \
    company_policy_2024Q2.txt \
    -o Q1_vs_Q2_report.md
```

### 场景2: 分析竞品政策
```bash
# 对比自己和竞争对手的政策
python policy_version_comparator.py \
    our_policy.txt \
    competitor_policy.txt \
    -o competitor_analysis.md
```

### 场景3: 学术研究
```bash
# 研究某公司多年的政策演变
python policy_version_comparator.py \
    facebook_2020.txt \
    facebook_2024.txt \
    --json \
    -o facebook_evolution.md
```

---

## 💡 理解对比机制

### 为什么不用简单的diff？

**问题：**
```
旧版本: "We collect your email address"
新版本: "Your email is gathered by us"
```

- ❌ **传统diff**: 认为完全不同（100%变化）
- ✅ **我们的工具**: 识别为同一条款（语义相同）

### 工作原理：

1. **文本相似度计算**
   - 使用算法计算两段文本的相似度（0-100%）
   - 相似度 ≥ 60% 认为是同一条款

2. **参数级对比**
   - 即使文本相似，也检查提取的参数是否变化
   - 例如：数据类型、第三方、用户权利

3. **智能匹配**
   - 自动找到最佳匹配的段落对
   - 识别新增、删除、修改三种情况

---

## 🛠️ 故障排除

### 问题1: 找不到模块
```
ModuleNotFoundError: No module named 'spacy'
```
**解决：**
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

### 问题2: 文件编码错误
```
UnicodeDecodeError: 'utf-8' codec can't decode...
```
**解决：**
确保你的隐私政策文件是UTF-8编码。如果是其他编码，用文本编辑器转换。

### 问题3: 报告内容为空
**可能原因：**
- 两个文件内容完全相同
- 文件格式不正确

**检查：**
```bash
# 查看文件内容
cat example_policy_v1.txt
cat example_policy_v2.txt
```

---

## 📈 进阶技巧

### 批量对比多个版本

```python
from policy_version_comparator import PolicyVersionComparator
import os

comparator = PolicyVersionComparator()
versions = ["v1.txt", "v2.txt", "v3.txt", "v4.txt"]

for i in range(len(versions) - 1):
    with open(versions[i]) as f1, open(versions[i+1]) as f2:
        old = f1.read()
        new = f2.read()

    result = comparator.compare_versions(old, new)
    comparator.generate_comparison_report(
        result,
        f"comparison_{i+1}_to_{i+2}.md"
    )
    print(f"✅ 完成: {versions[i]} vs {versions[i+1]}")
```

### 提取关键指标

```python
result = comparator.compare_versions(old_text, new_text)

# 获取风险变化
risk_delta = result['risk_change']['risk_change']
if risk_delta > 0:
    print(f"⚠️  风险增加了 {risk_delta:.2%}")

# 获取新增的敏感数据类型
new_data = result['summary_changes']['data_types']['added']
sensitive = ['biometric', 'location', 'financial', 'health']
if any(s in ' '.join(new_data) for s in sensitive):
    print("⚠️  新增敏感数据收集！")

# 检查用户权利是否减少
removed_rights = result['summary_changes']['user_rights']['removed']
if removed_rights:
    print(f"❌ 删除的权利: {', '.join(removed_rights)}")
```

---

## 📚 相关命令

```bash
# 查看帮助信息
python policy_version_comparator.py --help

# 分析单个政策（不对比）
python analyze_policy.py example_policy_v1.txt

# 运行准确性测试
python benchmark.py

# 演示NLP vs 简单规则
python demo_nlp_vs_simple.py
```

---

## 🎓 给教授演示时的建议

### 演示流程：

1. **展示两个版本的原始文件**
   ```bash
   cat example_policy_v1.txt
   cat example_policy_v2.txt
   ```

2. **运行对比工具**
   ```bash
   python policy_version_comparator.py example_policy_v1.txt example_policy_v2.txt
   ```

3. **解释终端输出**
   - 风险变化
   - 关键信息摘要

4. **打开生成的报告**
   ```bash
   open version_comparison_report.md
   # 或者在Windows上: notepad version_comparison_report.md
   ```

5. **强调技术亮点**
   - "不是简单的文本diff，而是语义理解"
   - "基于PIPEDA框架分类对比"
   - "自动识别风险变化并给出建议"

---

## 📞 需要帮助？

如果遇到问题：
1. 检查 `VERSION_COMPARISON_GUIDE.md` 详细文档
2. 查看示例文件的格式
3. 确保所有依赖已安装
4. 检查文件编码是否为UTF-8

**祝你使用愉快！** 🎉
