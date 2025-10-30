# 隐私政策分析器

> 基于PIPEDA框架和NLP技术的可解释隐私政策分析系统

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![spaCy](https://img.shields.io/badge/spaCy-3.7+-green.svg)](https://spacy.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 快速开始

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 下载spaCy模型
python -m spacy download en_core_web_sm

# 4. 运行示例
python demo_nlp_vs_simple.py
python analyze_policy.py example_privacy_policy.txt
```

---

## 📖 完整文档

**所有文档已整合到一个文件中**: 

### 👉 [完整项目文档.md](./完整项目文档.md)

该文档包含：
- ✅ 安装配置指南
- ✅ 详细使用教程
- ✅ 方法论详解（含文献引用）
- ✅ 代码结构说明
- ✅ 评估与基准测试
- ✅ 答辩要点和常见问题
- ✅ 完整的API文档

---

## 🎯 核心特点

- **基于文献**: 9篇学术文献支撑，每个方法都有理论依据
- **真实NLP**: 依存句法解析、命名实体识别、模式匹配
- **完全可解释**: 不是黑盒，每个决策都可追溯
- **风险量化**: 6因素风险评估模型
- **标准框架**: PIPEDA 10个公平信息原则

---

## 📦 项目结构

```
capestone/
├── 完整项目文档.md                    ⭐ 主要文档（所有内容）
├── README.md                          # 本文件
├── requirements.txt                   # Python依赖
│
├── privacy_analyzer_example.py        # 核心分析器（简洁版）
├── privacy_analyzer_with_citations.py # 核心分析器（带文献引用）
├── analyze_policy.py                  # 命令行工具
├── benchmark.py                       # 基准测试工具
├── demo_nlp_vs_simple.py             # NLP能力演示
│
├── example_privacy_policy.txt         # 示例隐私政策
├── example_privacy_policy_analysis.md # 示例分析报告
│
├── methodology_paper.tex              # LaTeX学术论文
├── METHODOLOGY_WITH_CITATIONS.md      # 详细方法论+引用
├── literature_review_and_methodology.md # 文献综述
│
├── .gitignore                         # Git忽略配置
└── Liture/                            # 参考文献PDF（8个）
```

---

## 💻 使用示例

### 命令行方式

```bash
# 基础分析
python analyze_policy.py policy.txt

# 生成Markdown报告
python analyze_policy.py policy.txt -o report.md -f markdown

# 显示详细信息
python analyze_policy.py policy.txt --verbose

# 仅显示摘要
python analyze_policy.py policy.txt --show-summary-only
```

### Python API方式

```python
from privacy_analyzer_example import PrivacyPolicyAnalyzer

# 初始化分析器
analyzer = PrivacyPolicyAnalyzer()

# 分析隐私政策
with open("policy.txt", "r") as f:
    results = analyzer.analyze(f.read())

# 生成报告
report = analyzer.generate_report(results)
print(report)
```

---

## 📊 分析示例

运行 `python analyze_policy.py example_privacy_policy.txt` 输出：

```
============================================================
📋 分析摘要
============================================================
分析段落数:     172
平均风险分数:   0.22
数据类型数量:   31
第三方数量:     84

PIPEDA类别分布:
  • 公开性: 72 个段落
  • 同意: 40 个段落
  • 个人访问权: 28 个段落
  • 限制使用、披露和保留: 13 个段落
  ...
============================================================
```

---

## 🔬 方法论简介

### PIPEDA 10个原则

1. **问责性** - 组织对个人信息的责任
2. **确定目的** - 收集信息的目的
3. **同意** - 获取用户同意的方式
4. **限制收集** - 仅收集必要信息
5. **限制使用** - 信息使用和共享
6. **准确性** - 信息准确性维护
7. **安全保障** - 技术和组织措施
8. **公开性** - 政策透明度
9. **个人访问权** - 用户查看、修改权利
10. **质疑合规性** - 投诉和救济机制

### NLP技术

- **依存句法解析**: 识别主谓宾关系
- **命名实体识别**: 提取组织、日期等
- **模式匹配**: 识别常见表述模式
- **风险评估**: 6因素量化模型

---

## 📚 文献支持

基于9篇学术文献：

1. LLM-Powered Interactive Privacy Policy Assessment
2. A Systematic Review of Privacy Policy Literature
3. An Empirical Study on Oculus VR Applications
4. CLEAR: Contextual LLM-Empowered Privacy Policy Analysis
5. Decoding the Privacy Policies of Assistive Technologies
6. Democratizing GDPR Compliance
7. Privacy Policy Compliance in Miniapps
8. Toward LLM-Driven GDPR Compliance Checking
9. PIPEDA Framework (官方文档)

详见 [完整项目文档.md - 文献支持章节](./完整项目文档.md#文献支持)

---

## 🧪 基准测试

```bash
# 创建标注模板
python benchmark.py --create-sample

# 运行评估
python benchmark.py sample_annotations.json
```

输出包括：
- 类别分类准确率
- 参数提取的精确率/召回率/F1
- 风险评分相关性

---

## 🎓 学术用途

### LaTeX论文

项目包含完整的LaTeX学术论文 (`methodology_paper.tex`)：

1. 访问 [Overleaf](https://overleaf.com)
2. 上传 `methodology_paper.tex`
3. 自动编译生成PDF
4. 修改作者信息后即可使用

### 方法论文档

- **带引用的方法论**: `METHODOLOGY_WITH_CITATIONS.md`
- **文献综述**: `literature_review_and_methodology.md`
- **完整文档**: `完整项目文档.md`

---

## 🤝 贡献

欢迎改进建议和代码贡献！

可以贡献的方向：
- 改进规则库
- 提供标注数据
- 报告Bug
- 完善文档

---

## 📄 许可证

MIT License

---

## 📞 获取帮助

- **安装问题**: 查看 [完整项目文档.md - 安装配置](./完整项目文档.md#安装配置)
- **使用问题**: 查看 [完整项目文档.md - 使用指南](./完整项目文档.md#使用指南)
- **方法问题**: 查看 [完整项目文档.md - 方法论详解](./完整项目文档.md#方法论详解)
- **答辩准备**: 查看 [完整项目文档.md - 答辩要点](./完整项目文档.md#答辩要点)

---

## ⭐ 核心命令速查

```bash
# 演示NLP能力
python demo_nlp_vs_simple.py

# 运行示例分析
python privacy_analyzer_example.py

# 分析隐私政策
python analyze_policy.py example_privacy_policy.txt

# 创建基准测试
python benchmark.py --create-sample

# 查看帮助
python analyze_policy.py --help
```

---

**详细文档请阅读**: [完整项目文档.md](./完整项目文档.md) ⭐

---

*最后更新: 2025年10月*
