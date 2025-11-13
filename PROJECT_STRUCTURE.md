# 📁 项目结构

```
privacy-policy-analyzer/
│
├── 📄 README.md                    # 项目主文档
├── 📄 requirements.txt             # Python依赖
├── 📄 RESTRUCTURE_PLAN.md          # 重构说明
│
├── 📂 src/                         # 源代码
│   ├── __init__.py
│   ├── analyzer.py                 # 主分析器 ⭐
│   ├── analyzer_with_docs.py       # 带文献引用版本
│   ├── srl_extractor.py            # SRL参数提取器 ⭐
│   └── semantic_analyzer.py        # 增强语义分析器
│
├── 📂 tools/                       # 命令行工具
│   ├── analyze.py                  # 分析工具 ⭐
│   ├── fetch_policy.py             # 爬虫工具
│   ├── compare_versions.py         # 版本对比 ⭐
│   └── benchmark.py                # 基准测试
│
├── 📂 docs/                        # 文档
│   ├── technical_brief_en.md       # 英文技术简报（给教授）⭐
│   ├── complete_guide_zh.md        # 完整中文指南 ⭐
│   ├── srl_improvements.md         # SRL改进报告
│   ├── noise_filtering.md          # 噪音过滤说明
│   ├── literature_review.md        # 文献综述
│   └── CORE_FILES.md               # 文件说明
│
├── 📂 data/                        # 数据文件
│   └── examples/
│       └── facebook_policy.txt     # 示例隐私政策
│
└── 📂 tests/                       # 测试（预留）
    └── __init__.py
```

## 🎯 核心文件说明

### 源代码 (src/)

1. **analyzer.py** - 主分析器
   - PIPEDA分类
   - 风险评分
   - 参数提取（集成SRL）
   - 噪音过滤

2. **srl_extractor.py** - 语义角色标注提取器
   - 提取数据类型、第三方、使用目的
   - 基于spaCy依存解析
   - 支持16个隐私相关动词

3. **semantic_analyzer.py** - 增强语义分析
   - 可选的深度语义分析

4. **analyzer_with_docs.py** - 带文献引用版本
   - 包含详细的学术引用
   - 用于论文写作

### 工具 (tools/)

1. **analyze.py** - 命令行分析工具
   ```bash
   python tools/analyze.py data/examples/facebook_policy.txt
   ```

2. **compare_versions.py** - 版本对比工具
   ```bash
   python tools/compare_versions.py policy_v1.txt policy_v2.txt
   ```

3. **fetch_policy.py** - 爬虫工具
   ```bash
   python tools/fetch_policy.py
   ```

4. **benchmark.py** - 基准测试
   ```bash
   python tools/benchmark.py annotations.json
   ```

### 文档 (docs/)

1. **technical_brief_en.md** - 英文技术简报
   - 向教授汇报用
   - 包含完整的技术架构、原理、结果

2. **complete_guide_zh.md** - 完整中文指南
   - 详细的使用教程
   - 方法论详解
   - 答辩要点

3. **srl_improvements.md** - SRL改进报告
   - 语义角色标注的效果分析
   - 与基础方法的对比

4. **noise_filtering.md** - 噪音过滤原理
   - spaCy如何识别干扰内容
   - 过滤规则详解

5. **literature_review.md** - 文献综述
   - 9篇学术文献总结
   - 方法论基础

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. 分析隐私政策
```bash
python tools/analyze.py data/examples/facebook_policy.txt
```

### 3. 对比两个版本
```bash
python tools/compare_versions.py old_policy.txt new_policy.txt
```

## 📊 项目统计

- **总代码行数**: ~2000行
- **核心模块**: 4个
- **工具脚本**: 4个
- **文档**: 6个
- **支持的PIPEDA类别**: 10个
- **识别的隐私动词**: 16个

## ✨ 重构改进

### 之前 (17个混乱的文件)
```
privacy_analyzer_example.py
privacy_analyzer_with_citations.py
srl_analyzer.py
enhanced_semantic_analyzer.py
analyze_policy.py
fetch_facebook_policy.py
policy_version_comparator.py
...
```

### 现在 (清晰的目录结构)
```
src/analyzer.py
src/srl_extractor.py
tools/analyze.py
tools/compare_versions.py
docs/technical_brief_en.md
...
```

### 改进点
✅ 代码和工具分离  
✅ 文件命名简洁  
✅ 符合Python标准  
✅ 便于扩展维护  
✅ 专业化程度提升  
