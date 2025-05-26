# docx-plainify

Convert .docx files to structured YAML format for AI processing.

## 项目概述

docx-plainify 是一个专门设计的工具，用于将 Microsoft Word (.docx) 文件转换为结构化的 YAML 格式，使文档内容更易于被人工智能（AI）模型读取、理解和处理。

## 核心功能

- 📄 **文本提取**: 从 .docx 文件中提取所有可读的文本内容
- 🏗️ **结构识别**: 识别并转换文档中的结构化元素：
  - 段落 (paragraphs)
  - 标题 (headings) 
  - 列表 (lists) - 包括嵌套列表
  - 表格 (tables)
- 🖼️ **图像处理**: 可选的图像描述生成功能，使用多模态大语言模型
- 📝 **YAML 输出**: 保留原始文档结构的 YAML 格式输出

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone <repository-url>
cd docx-plainify

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装项目
pip install -e .
```

## 使用方法

### 基本用法

```bash
# 基本转换
docx-plainify document.docx

# 指定输出文件
docx-plainify document.docx -o output.yaml

# 启用详细日志
docx-plainify document.docx -v
```

### 图像描述功能

要启用图像描述功能，您需要配置 Azure OpenAI 环境变量：

```bash
# 配置 Azure OpenAI 环境变量
export AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
export AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
export AZURE_OPENAI_API_VERSION=2024-02-15-preview

# 启用图像描述
docx-plainify document.docx --describe-images
```

### 命令行选项

```
Usage: docx-plainify [OPTIONS] INPUT_FILE

Options:
  -o, --output PATH       输出 YAML 文件路径
  --describe-images       使用 LLM 生成图像描述（需要 Azure OpenAI 配置）
  --api-key TEXT          已弃用：请使用 Azure OpenAI 环境变量
  -v, --verbose           启用详细日志
  --version               显示版本信息
  --help                  显示帮助信息
```

## 输出格式

转换后的 YAML 文件包含以下结构化元素：

### 段落
```yaml
- type: paragraph
  text: "这是一个普通段落的文本内容。"
```

### 标题
```yaml
- type: heading
  text: "文档主标题"
  level: 1
```

### 列表（包括嵌套列表）
```yaml
- type: list
  items:
    - text: "列表项一"
    - text: "列表项二"
      children:
        - text: "子列表项 A"
        - text: "子列表项 B"
```

### 表格
```yaml
- type: table
  rows:
    - 姓名: "张三"
      职责: "产品经理"
      备注: "负责需求"
    - 姓名: "李四"
      职责: "UI设计师"
      备注: "设计原型"
```

### 图像描述
```yaml
- type: image
  name: "chart.png"
  description: "一张柱状图，显示一月至六月的销售额稳步增长。"
```

## 技术架构

- **DOCX 解析**: 使用 `python-docx` 库
- **YAML 生成**: 使用 `PyYAML` 库
- **图像描述**: 使用 `langchain` 和 Azure OpenAI 模型
- **命令行接口**: 使用 `click` 库

## 项目结构

```
docx-plainify/
├── docx_plainify/
│   ├── __init__.py
│   ├── cli.py              # 命令行接口
│   ├── converter.py        # 核心转换器
│   ├── image_processor.py  # 图像处理模块
│   └── list_processor.py   # 列表处理模块
├── doc/
│   └── prd.yaml           # 项目需求文档
├── requirements.txt       # 项目依赖
├── setup.py              # 安装配置
└── README.md             # 项目说明
```

## 环境变量

- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI 服务端点
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Azure OpenAI 部署名称
- `AZURE_OPENAI_API_VERSION`: Azure OpenAI API 版本

## 错误处理

工具包含健壮的错误处理机制：

- 文件读取错误处理
- API 调用失败处理
- 不支持的 DOCX 元素处理
- 详细的日志输出（DEBUG, INFO, WARNING, ERROR 级别）

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的 DOCX 到 YAML 转换
- 支持图像描述生成
- 完整的命令行接口