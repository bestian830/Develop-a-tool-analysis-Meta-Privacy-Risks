# 项目核心文件说明

## 📂 文件结构

### 🔧 核心代码文件

1. **privacy_analyzer_example.py** - 主分析器（简洁版）
   - 核心隐私政策分析器
   - 集成SRL、噪音过滤、风险评分
   - 推荐日常使用

2. **privacy_analyzer_with_citations.py** - 带文献引用的分析器
   - 包含详细的文献引用注释
   - 用于学术展示

3. **srl_analyzer.py** - 语义角色标注分析器
   - 提取数据类型、第三方、目的等参数
   - 基于spaCy依存解析

4. **enhanced_semantic_analyzer.py** - 增强语义分析器
   - 更深入的语义分析
   - 可选组件

### 🛠️ 工具脚本

5. **analyze_policy.py** - 命令行分析工具
   - 使用方法: `python analyze_policy.py policy.txt`
   - 生成分析报告

6. **fetch_facebook_policy.py** - 网页爬虫
   - 自动抓取隐私政策
   - 用于版本追踪

7. **policy_version_comparator.py** - 版本对比工具
   - 对比不同版本的隐私政策
   - 识别语义差异

8. **benchmark.py** - 基准测试工具
   - 评估分析器准确性
   - 与人工标注对比

### 📄 文档文件

9. **README.md** - 项目主文档
   - 快速开始指南
   - 使用说明

10. **完整项目文档.md** - 完整中文文档
    - 详细的使用教程
    - 方法论解释
    - 答辩要点

11. **PROJECT_TECHNICAL_BRIEF.md** - 技术简报（英文）
    - 向教授汇报用
    - 完整的技术架构说明

12. **SRL_IMPROVEMENTS.md** - SRL改进报告
    - 语义角色标注的效果分析
    - 对比测试结果

13. **NOISE_FILTERING_EXPLANATION.md** - 噪音过滤原理
    - 如何过滤爬虫干扰内容
    - spaCy的作用

14. **literature_review_and_methodology.md** - 文献综述与方法论
    - 学术基础
    - 9篇文献总结

### 📊 数据文件

15. **example_privacy_policy.txt** - 示例隐私政策
    - Facebook隐私政策
    - 用于测试

16. **example_privacy_policy_analysis.md** - 示例分析报告
    - 完整的分析结果
    - 参考输出

17. **requirements.txt** - Python依赖
    - 需要安装的库

## 🎯 使用指南

### 快速分析隐私政策
```bash
python analyze_policy.py example_privacy_policy.txt
```

### 对比两个版本
```bash
python policy_version_comparator.py policy_v1.txt policy_v2.txt
```

### 抓取网页政策
```bash
python fetch_facebook_policy.py
```

## 📝 向教授展示的文档

1. **PROJECT_TECHNICAL_BRIEF.md** - 技术全貌（英文）
2. **SRL_IMPROVEMENTS.md** - 核心创新点
3. **NOISE_FILTERING_EXPLANATION.md** - 技术细节
4. **完整项目文档.md** - 完整中文文档

## ✅ 已删除的文件

- 测试脚本 (test_*.py)
- Demo脚本 (demo_*.py)
- 临时版本文件
- 重复的文档
- BERT相关文件（实验效果不佳）
