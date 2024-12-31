# 剪纸图案转矢量图工具

一个专业的剪纸图片矢量化工具，完美还原红色剪纸艺术的细节与轮廓。

## 功能特点

- 支持多种图片格式输入（PNG、JPG、JPEG、BMP等）
- 实时预览转换效果
- 可调整的转换参数，精确控制输出效果
- 支持导出为SVG、EPS等矢量格式
- 专为剪纸艺术优化的转换算法
- 美观的用户界面和简单的操作流程

## 技术栈

### 后端
- Python 3.12
- Flask 3.0.0 - Web框架
- Pillow 10.1.0 - 图像处理
- python-magic 0.4.27 - 文件类型检测
- Gunicorn 21.2.0 - WSGI HTTP服务器

### 前端
- HTML5
- CSS3
- JavaScript
- Font Awesome - 图标库
- Paper Cut Font - 剪纸风格字体

### 系统依赖
- Potrace - 位图转矢量图工具
  - 版本要求：1.16 或更高
  - Ubuntu/Debian安装：`apt-get install potrace`
  - CentOS/RHEL安装：`yum install potrace`
  - macOS安装：`brew install potrace`
- libmagic - 文件类型检测库
  - Ubuntu/Debian安装：`apt-get install libmagic1`
  - CentOS/RHEL安装：`yum install file-libs`
  - macOS安装：`brew install libmagic`

## 快速开始

1. 克隆仓库
```bash
git clone https://github.com/long183186468/potrace-web.git
cd potrace-web
```

2. 安装系统依赖
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y potrace libmagic1

# CentOS/RHEL
sudo yum install -y potrace file-libs

# macOS
brew install potrace libmagic
```

3. 创建虚拟环境并安装Python依赖
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

4. 启动应用
```bash
python app.py
```

访问 http://localhost:5000 即可使用

## Docker部署

1. 构建镜像
```bash
docker build -t potrace-web .
```

2. 运行容器
```bash
docker run -d -p 5000:5000 potrace-web
```

## 使用说明

1. 上传图片：支持PNG、JPG、JPEG、BMP等格式
2. 调整参数：
   - 阈值：控制黑白转换的界限
   - 平滑度：控制曲线的平滑程度
   - 优化：控制路径优化级别
3. 预览效果：实时查看转换结果
4. 下载：选择所需的矢量格式下载

## 适用场景

- 传统剪纸作品数字化
- 窗花图案矢量化
- 民间艺术作品保存
- 新年装饰图案制作
- 剪纸艺术创作参考

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 致谢

本项目基于以下开源项目：

### Potrace

本项目使用了 [Potrace](http://potrace.sourceforge.net/) 作为核心的矢量化引擎。Potrace 是一个出色的位图描摹工具，由 Peter Selinger 开发。

- 官方网站：http://potrace.sourceforge.net/
- 开源协议：GPL
- 版本：1.16

Potrace 的主要特点：
- 高质量的轮廓线追踪
- 平滑的曲线生成
- 对称性保持
- 多种输出格式支持

感谢 Peter Selinger 和 Potrace 项目的所有贡献者，他们的工作使得本项目成为可能。

### 其他开源项目

- Flask：Web 应用框架
- Pillow：图像处理库
- Font Awesome：图标库

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

注意：本项目中使用的 Potrace 遵循 GPL 协议。在使用本项目时，请同时遵守 Potrace 的开源协议要求。 