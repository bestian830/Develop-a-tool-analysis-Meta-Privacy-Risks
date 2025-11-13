# 隐私政策分析器

> 基于PIPEDA框架和NLP技术的可解释隐私政策分析系统

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![spaCy](https://img.shields.io/badge/spaCy-3.7+-green.svg)](https://spacy.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 快速开始

### 一键启动（推荐）

**macOS / Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

启动脚本会自动：
- ✅ 检查并安装所有依赖
- ✅ 同时启动后端和前端服务
- ✅ 显示访问地址

### 手动启动

如果需要分别启动：

**1. 启动后端：**
```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 启动API服务器
python run_api.py
```

**2. 启动前端（新终端）：**
```bash
cd frontend
npm install --legacy-peer-deps  # 首次运行
npm start
```

**访问地址：**
- 前端: http://localhost:3000
- 后端API: http://localhost:5001

### 公网访问（使用 ngrok）

如果需要通过公网访问应用（用于演示、移动设备测试等）：

**同时转发前端和后端（推荐）：**
```bash
./start_with_ngrok_both.sh
```

**只转发前端：**
```bash
./start_with_ngrok.sh
```

详细说明请查看：
- [ngrok 使用指南](./NGROK_GUIDE.md) - 完整使用说明
- [同时转发前后端指南](./NGROK_BOTH_GUIDE.md) - 快速上手指南

---

## 📖 完整文档

**项目采用模块化文档结构**:

### 📂 主要文档

- 👉 [完整项目文档 (中文)](./docs/complete_guide_zh.md) - 详细使用指南和方法论
- 👉 [技术简报 (英文)](./docs/technical_brief_en.md) - 向教授汇报用的技术全貌
- 📊 [项目结构说明](./PROJECT_STRUCTURE.md) - 文件组织说明

### 📚 技术文档

- [SRL改进报告](./docs/srl_improvements.md) - 语义角色标注效果分析
- [噪音过滤原理](./docs/noise_filtering.md) - 如何过滤爬虫干扰内容
- [文献综述](./docs/literature_review.md) - 学术基础和方法论依据

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
privacy-policy-analyzer/
├── README.md                       # 本文件
├── requirements.txt                # Python依赖
│
├── src/                           # 源代码
│   ├── analyzer.py                # 主分析器 ⭐
│   ├── srl_extractor.py           # SRL参数提取器
│   ├── semantic_analyzer.py       # 增强语义分析
│   └── analyzer_with_docs.py      # 带文献引用版本
│
├── tools/                         # 命令行工具
│   ├── analyze.py                 # 分析工具 ⭐
│   ├── compare_versions.py        # 版本对比 ⭐
│   ├── fetch_policy.py            # 爬虫工具
│   └── benchmark.py               # 基准测试
│
├── docs/                          # 文档
│   ├── technical_brief_en.md      # 英文技术简报
│   ├── complete_guide_zh.md       # 完整中文指南
│   ├── srl_improvements.md        # SRL改进报告
│   ├── noise_filtering.md         # 噪音过滤原理
│   └── literature_review.md       # 文献综述
│
└── data/                          # 数据
    └── examples/
        └── facebook_policy.txt    # 示例隐私政策
```

详见 [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)

---

## 💻 使用示例

### 命令行方式

```bash
# 基础分析（纯本地，免费）
python tools/analyze.py policy.txt

# 生成Markdown报告
python tools/analyze.py policy.txt -o report.md -f markdown

# LLM 增强模式（提高准确性，需要 API key）
python tools/analyze.py policy.txt --use-llm --llm-api-key "your-deepseek-key"

# 显示详细信息
python tools/analyze.py policy.txt --verbose

# 仅显示摘要
python tools/analyze.py policy.txt --show-summary-only
```

### Python API方式

```python
import sys
sys.path.insert(0, 'src')
from analyzer import PrivacyPolicyAnalyzer

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

运行 `python tools/analyze.py data/examples/facebook_policy.txt` 输出：

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

## 🚀 新功能：LLM 辅助增强 (可选)

现在支持使用大语言模型（LLM）辅助提取，提高准确性！

**特点：**
- ✅ **本地优先**：默认使用 spaCy + Transformer（免费）
- ✅ **可选增强**：需要时启用 LLM（低成本）
- ✅ **支持多个提供商**：DeepSeek（推荐）, OpenAI, Claude

**使用：**
```bash
export DEEPSEEK_API_KEY="sk-b0b770ea4c6c40aca383cdf5e5f6008e"
python tools/analyze.py policy.txt --use-llm
```

**成本：** 分析一个完整政策约 ¥0.01-0.05（DeepSeek）

详见：[LLM 集成指南](./docs/llm_integration.md) ⭐

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
# 分析隐私政策
python tools/analyze.py data/examples/facebook_policy.txt

# 对比两个版本
python tools/compare_versions.py policy_v1.txt policy_v2.txt

# 爬取隐私政策
python tools/fetch_policy.py

# 创建基准测试
python tools/benchmark.py --create-sample

# 查看帮助
python tools/analyze.py --help
```

---

**详细文档请阅读**:
- 中文: [docs/complete_guide_zh.md](./docs/complete_guide_zh.md) ⭐
- English: [docs/technical_brief_en.md](./docs/technical_brief_en.md) ⭐

---

*最后更新: 2025年10月*
