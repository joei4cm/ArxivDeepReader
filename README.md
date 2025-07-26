# ArXiv Deep Reader

一个优雅的ArXiv论文深度阅读和管理系统，支持自动检测和展示论文内容。

## 功能特性

- 🔍 **自动检测**: 智能扫描AI目录中的论文文件夹
- 📖 **深度解析**: 支持HTML格式的论文深度分析页面
- 📄 **文档管理**: 自动分类和展示PDF、报告等附件
- 🎨 **美观界面**: 使用Tailwind CSS构建的现代化UI
- 🔄 **自动更新**: 通过脚本自动更新论文元数据

## 目录结构

```
ArxivDeepReader/
├── index.html              # 主页面
├── update_metadata.py      # 元数据自动更新脚本
├── update_metadata.bat     # Windows批处理脚本
├── requirements.txt        # Python依赖
├── README.md              # 说明文档
└── AI/                    # 论文目录
    ├── 2412.19255v2/      # 论文文件夹
    │   ├── *.html         # 深度解析页面
    │   ├── *.pdf          # 原文PDF
    │   └── *.pdf          # 其他报告文档
    └── 2507.11851v1/
        ├── *.html
        ├── *.pdf
        └── *.pdf
```

## 快速开始

### 1. 添加新论文

在 `AI/` 目录下创建新的论文文件夹，文件夹名称应包含论文ID（如 `2412.19255v2`）：

```
AI/
└── 新论文ID/
    ├── 论文ID.html     # 深度解析页面（必需）
    ├── 论文ID.pdf      # 原文PDF
    └── 其他文档.pdf     # 可选的报告、分析文档
```

### 2. 自动更新元数据

#### 方法一：使用批处理脚本（推荐）
双击运行 `update_metadata.bat`

#### 方法二：手动运行Python脚本
```bash
# 安装依赖
pip install -r requirements.txt

# 运行更新脚本
python update_metadata.py
```

### 3. 查看结果
在浏览器中打开 `index.html` 查看更新后的论文列表。

## 元数据自动提取

更新脚本会自动从HTML文件中提取以下信息：

- **标题**: 从 `<title>` 或 `<h1>` 标签提取
- **描述**: 从meta描述或首段文字提取
- **分类**: 基于内容关键词智能分类
- **标签**: 根据论文主题自动生成
- **样式**: 自动分配颜色主题和渐变

### 支持的分类

- 🔵 **KV缓存优化**: 内存和缓存相关技术
- 🟢 **推理加速**: 多令牌预测、并行计算
- 🟣 **模型训练**: 训练优化、微调技术
- 🟠 **推理能力**: 逻辑推理、思维链
- 🩷 **多模态**: 视觉理解、跨模态融合
- 🔷 **模型架构**: 架构设计、注意力机制
- ⚫ **AI研究**: 通用AI技术研究

## 文件类型识别

系统会自动识别和分类不同类型的文件：

- 📖 **HTML文件**: 深度解析页面（优先显示）
- 📄 **PDF文件**: 根据文件名智能分类
  - 📊 研究报告（包含"报告"或"report"）
  - 🔧 技术报告（包含"tech"或"技术"）
  - 📊 分析报告（包含"分析"或"analysis"）
  - 📄 原文PDF（其他PDF文件）
- 📎 **其他文档**: Markdown、文本文件等

## 自定义配置

### 修改分类规则

编辑 `update_metadata.py` 中的 `categorize_content` 方法来自定义分类逻辑：

```python
def categorize_content(self, content_text: str, title: str) -> tuple:
    # 添加新的关键词匹配规则
    if 'your_keyword' in content_text.lower():
        return ('自定义分类', 'color', ['标签1', '标签2'], ['color1', 'color2'], 'gradient')
```

### 手动编辑元数据

也可以直接编辑 `index.html` 中的 `paperMetadata` 对象来手动调整论文信息。

## 故障排除

### 常见问题

1. **Python未安装**: 请安装Python 3.7+
2. **依赖安装失败**: 手动运行 `pip install beautifulsoup4 lxml`
3. **HTML解析错误**: 检查HTML文件格式是否正确
4. **元数据未更新**: 确保 `index.html` 中存在 `paperMetadata` 对象

### 调试模式

运行脚本时会显示详细的处理信息，包括：
- 发现的论文文件夹
- 提取的元数据信息
- 更新状态

## 技术栈

- **前端**: HTML5, Tailwind CSS, JavaScript
- **后端脚本**: Python 3.7+
- **依赖库**: BeautifulSoup4, lxml
- **样式框架**: Tailwind CSS CDN

## 许可证

本项目采用 MIT 许可证。