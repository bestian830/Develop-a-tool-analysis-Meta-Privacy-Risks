# 如何将文献综述转换为PDF

## ✅ 已完成的工作

我已经将 `LITERATURE_METHODS_SUMMARY.md` 转换为一个美观的HTML文件：
- **文件名**: `LITERATURE_METHODS_SUMMARY.html`
- **包含**: 完整目录、所有内容、美观样式

## 🖨️ 将HTML转换为PDF的方法

### 方法1: 使用浏览器打印（推荐 - 最简单）

1. **打开HTML文件**
   - 双击 `LITERATURE_METHODS_SUMMARY.html`
   - 或者拖放到浏览器（Chrome/Safari/Firefox）

2. **打印为PDF**
   - Mac: `Command + P`
   - 在打印对话框中选择 **"Save as PDF"** 或 **"另存为PDF"**
   - 建议设置:
     - 页面: A4
     - 边距: 默认
     - 背景图形: 开启（保留样式）
   - 保存为: `LITERATURE_METHODS_SUMMARY.pdf`

✅ **优点**: 
- 无需安装额外软件
- 保留所有格式和样式
- 中文显示完美

### 方法2: 使用在线工具

**推荐网站**:
1. **Markdown to PDF**
   - https://www.markdowntopdf.com/
   - 上传 `LITERATURE_METHODS_SUMMARY.md`
   - 下载生成的PDF

2. **CloudConvert**
   - https://cloudconvert.com/md-to-pdf
   - 支持中文
   - 质量高

### 方法3: 安装LaTeX后使用Pandoc（高级）

如果你需要专业排版，可以安装MacTeX：

```bash
# 安装MacTeX (大约4GB，需要时间)
brew install --cask mactex

# 安装后，运行:
cd /Users/meng/Desktop/CODE/capestone
pandoc LITERATURE_METHODS_SUMMARY.md -o LITERATURE_METHODS_SUMMARY.pdf \
  --pdf-engine=xelatex \
  -V CJKmainfont="PingFang SC" \
  -V geometry:margin=1in \
  -V fontsize=11pt \
  --toc \
  --toc-depth=2 \
  -N \
  --metadata title="文献方法论综合总结"
```

## 📄 当前可用的文件

### HTML版本（已生成）✅
- **文件**: `LITERATURE_METHODS_SUMMARY.html`
- **优点**: 
  - 可以在浏览器中查看
  - 可以直接打印为PDF
  - 包含完整目录
  - 样式美观

### Markdown版本（原始）
- **文件**: `LITERATURE_METHODS_SUMMARY.md`
- **优点**: 
  - 可以编辑
  - 纯文本格式
  - 70+页内容

## 🎯 推荐步骤（最快）

### 5分钟内完成：

1. **打开HTML**
   ```bash
   open LITERATURE_METHODS_SUMMARY.html
   ```
   （或者双击文件）

2. **浏览器打印**
   - Command + P
   - 目标: Save as PDF
   - 保存

3. **完成！** 
   你现在有了一个专业的PDF文档 ✅

## 📊 PDF预期效果

- ✅ 完整的70+页内容
- ✅ 自动生成的目录（2级）
- ✅ 所有代码示例保留格式
- ✅ 所有表格正确显示
- ✅ 中英文混排正确
- ✅ 章节编号清晰
- ✅ 可复制文本

## 🔧 如果需要修改PDF样式

编辑生成的HTML文件，在 `<head>` 部分添加自定义CSS：

```html
<style>
body {
    max-width: 900px;
    margin: 0 auto;
    padding: 2em;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.6;
}
code {
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
}
pre {
    background-color: #f5f5f5;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
}
</style>
```

然后重新打印为PDF。

## 💡 提示

### 打印设置优化
- **缩放**: 100%（不要缩小）
- **页眉页脚**: 可以添加页码
- **颜色**: 彩色（保留代码高亮）
- **双面**: 根据需要选择

### 文件大小
- HTML: ~500KB
- PDF: 预计 2-5MB（取决于字体嵌入）

## ✅ 验证清单

生成PDF后，检查：
- [ ] 目录完整，可以点击跳转（如果支持）
- [ ] 所有代码块格式正确
- [ ] 表格显示完整
- [ ] 中文字符显示正常
- [ ] 页面边距合适
- [ ] 章节分页合理

---

**如果遇到问题**，请告诉我具体的错误信息，我可以帮你解决！


