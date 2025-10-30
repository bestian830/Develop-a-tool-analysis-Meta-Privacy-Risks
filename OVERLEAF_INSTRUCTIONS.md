# 如何在Overleaf中使用这个LaTeX文档

## 📄 文件说明

已创建文件：**`methodology_paper.tex`**

这是一个完整的IEEE会议格式学术论文，包含：
- ✅ 完整的方法论描述
- ✅ 文献引用
- ✅ 系统架构说明
- ✅ 算法伪代码
- ✅ 评估方法
- ✅ 结果讨论
- ✅ 参考文献

## 🚀 在Overleaf中使用

### 方法1: 直接上传

1. 访问 https://www.overleaf.com/
2. 登录你的账号
3. 点击 **"New Project"** → **"Upload Project"**
4. 上传 `methodology_paper.tex` 文件
5. Overleaf会自动编译生成PDF

### 方法2: 新建项目并粘贴

1. 在Overleaf创建新项目：**"New Project"** → **"Blank Project"**
2. 删除默认的 `main.tex` 内容
3. 将 `methodology_paper.tex` 的内容复制粘贴进去
4. 点击 **"Recompile"** 生成PDF

## 📝 需要自定义的部分

在提交前，请修改以下内容：

### 1. 作者信息（第15-20行）
```latex
\author{\IEEEauthorblockN{Your Name}          % 改成你的名字
\IEEEauthorblockA{\textit{Department of Computer Science} \\  % 你的系
\textit{University Name}\\                    % 你的大学
City, Country \\                              % 城市、国家
email@example.com}                            % 你的邮箱
}
```

### 2. Acknowledgment（第530行左右）
```latex
The author thanks [Your Supervisor/Advisor] for guidance...
This work was conducted as part of [Course/Program Name]...
```

### 3. 参考文献（第535-570行）
如果你有完整的文献信息，替换为：
```latex
\bibitem{llm-assessment} 
作者名. "完整标题". 会议/期刊名, 卷号(期号), 页码, 年份.
```

## 📊 文档结构

```
1. Abstract (摘要)
2. Introduction (引言)
   - 问题背景
   - 现有方法的局限
   - 本文贡献

3. Related Work (相关工作)
   - 隐私政策分析方法
   - 法律框架
   - NLP技术
   - 风险评估

4. Methodology (方法论) ⭐ 核心部分
   - 系统架构
   - 文本预处理
   - 参数提取
   - PIPEDA分类
   - 风险评估模型
   - 解释生成

5. Implementation (实现)
   - 技术栈
   - 核心算法
   - 代码示例

6. Evaluation (评估)
   - 评估指标
   - 人工基准测试
   - 基准测试框架

7. Results (结果)
   - 示例分析
   - 类别分布
   - 与现有方法对比

8. Discussion (讨论)
   - 优势
   - 局限性
   - 未来工作

9. Conclusion (结论)

10. References (参考文献)
```

## 🎨 文档特点

### IEEE会议格式
- 双栏排版
- 专业学术风格
- 符合国际会议标准

### 包含的元素
- ✅ 数学公式（风险评估模型）
- ✅ 算法伪代码
- ✅ 表格（规则、对比）
- ✅ 代码示例（Python）
- ✅ 列表和引用

## 🔧 可选优化

### 添加图表
如果你想添加流程图或架构图：

```latex
% 在preamble添加
\usepackage{tikz}
\usetikzlibrary{shapes,arrows}

% 在正文中
\begin{figure}[htbp]
\centering
\includegraphics[width=3in]{pipeline.png}
\caption{Analysis Pipeline}
\label{fig:pipeline}
\end{figure}
```

### 添加更多表格
```latex
\begin{table}[htbp]
\caption{Your Table Title}
\begin{center}
\begin{tabular}{|c|c|}
\hline
\textbf{Column 1} & \textbf{Column 2} \\
\hline
Data 1 & Data 2 \\
\hline
\end{tabular}
\end{center}
\end{table}
```

## 📖 使用BibTeX（可选）

如果你想使用BibTeX管理参考文献：

### 1. 创建 `references.bib` 文件：
```bibtex
@inproceedings{llm-assessment,
  title={You Don't Need a University Degree to Comprehend Data Protection This Way: LLM-Powered Interactive Privacy Policy Assessment},
  author={Author Name},
  booktitle={Conference Name},
  year={2024}
}

@article{systematic-review,
  title={A Systematic Review of Privacy Policy Literature},
  author={Author Name},
  journal={Journal Name},
  year={2023}
}
```

### 2. 在 `.tex` 文件末尾替换 `\begin{thebibliography}` 为：
```latex
\bibliographystyle{IEEEtran}
\bibliography{references}
```

## ⚡ 快速编译测试

在Overleaf中：
1. 上传文件后会自动编译
2. 如果有错误，查看右侧的 **"Logs and output files"**
3. 常见错误：缺少包 → Overleaf通常会自动安装

## 📄 导出PDF

编译成功后：
1. 点击顶部的 **"Download PDF"** 按钮
2. 或者点击 **"Submit"** 直接提交（如果是在线提交系统）

## 💡 进阶技巧

### 改变文档类型
如果需要其他格式：

```latex
% 改为期刊格式
\documentclass[journal]{IEEEtran}

% 改为ACM格式
\documentclass[sigconf]{acmart}

% 改为标准文章
\documentclass[12pt]{article}
```

### 添加行号（用于审阅）
```latex
\usepackage{lineno}
\linenumbers
```

### 添加TODO标记
```latex
\usepackage{todonotes}
% 在正文中
\todo{需要补充这部分内容}
```

## ✅ 提交前检查清单

- [ ] 修改了作者信息
- [ ] 修改了Acknowledgment
- [ ] 检查了所有公式和符号
- [ ] 检查了参考文献格式
- [ ] 通读全文，修正语法错误
- [ ] 确保所有表格和图片都有caption
- [ ] 检查页数是否符合要求
- [ ] 导出PDF并检查格式

## 🆘 常见问题

### Q: 编译失败怎么办？
A: 查看Logs，通常是：
- 缺少 `\end{...}` 标签
- 特殊字符没有转义（如 `&`, `%`, `_`）
- 公式环境错误

### Q: 如何调整页边距？
A: 添加：
```latex
\usepackage[margin=1in]{geometry}
```

### Q: 如何改变字体大小？
A: 在 `\documentclass` 中：
```latex
\documentclass[conference,12pt]{IEEEtran}
```

### Q: 参考文献如何排序？
A: IEEE格式默认按引用顺序。如果要字母序：
```latex
\bibliographystyle{IEEEtranS}  % S = sorted
```

## 📞 获取帮助

- Overleaf文档: https://www.overleaf.com/learn
- LaTeX Stack Exchange: https://tex.stackexchange.com/
- IEEE模板: https://www.ieee.org/conferences/publishing/templates.html

---

## 🎓 论文写作建议

1. **Abstract**: 150-250词，概述问题、方法、结果
2. **Introduction**: 清晰说明动机和贡献
3. **Related Work**: 诚实对比，指出差异
4. **Methodology**: 详细到可重现
5. **Results**: 客观展示，不夸大
6. **Discussion**: 坦诚局限性，提出未来方向

Good luck with your submission! 🚀


