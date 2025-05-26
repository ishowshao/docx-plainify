# 更新日志

## [1.0.0] - 2025-05-27

### 新增功能
- 🎉 初始版本发布
- 📄 支持 DOCX 文件到 YAML 格式的转换
- 🏗️ 识别并转换文档结构元素：
  - 段落 (paragraphs)
  - 标题 (headings) 
  - 列表 (lists) - 包括自动合并连续列表项
  - 表格 (tables)
- 🖼️ 可选的图像描述生成功能（使用 OpenAI GPT-4o）
- 🛠️ 完整的命令行接口
- 📝 自动清理列表标记
- 🔧 健壮的错误处理和日志记录

### 技术特性
- 使用 `python-docx` 进行 DOCX 解析
- 使用 `PyYAML` 生成结构化输出
- 使用 `langchain` 和 OpenAI API 进行图像描述
- 使用 `click` 构建命令行界面

### 文档
- 📚 完整的 README 文档
- 🎯 项目需求文档 (PRD)
- 📋 示例输出文件
- 🧪 基础单元测试

### 安装和使用
```bash
pip install -e .
docx-plainify document.docx
``` 