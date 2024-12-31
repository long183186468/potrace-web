# 剪纸图案转矢量图工具

一个专业的剪纸图片矢量化工具，可以将传统剪纸作品、窗花图案等位图转换为高质量的矢量图形。

## 功能特点

- 支持多种输入格式：PNG、JPG、JPEG、BMP、PBM、PGM、PPM、PNM
- 支持多种输出格式：SVG、DXF、PDF、EPS
- 实时预览转换效果
- 可调整的转换参数：
  - 黑白阈值
  - 噪点过滤
  - 角度阈值
  - 优化容差
- 自定义输出颜色
- 支持轮廓线提取

## 技术栈

- 后端：Python + Flask
- 前端：HTML + CSS + JavaScript
- 矢量化：Potrace 算法
- 部署：Docker（可选）

## 快速开始

1. 克隆仓库：
```bash
git clone https://github.com/long183186468/potrace-web.git
cd potrace-web
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python app.py
```

4. 打开浏览器访问：`http://localhost:5000`

## 使用说明

1. 上传图片：点击或拖放图片到上传区域
2. 选择输出格式：SVG、DXF、PDF 或 EPS
3. 调整参数：
   - 黑白阈值：决定图像转换为黑白时的界限值
   - 噪点过滤：过滤小于指定面积的区域
   - 角度阈值：控制曲线拟合时的角度阈值
   - 优化容差：控制路径优化的精度
4. 设置输出颜色和是否只保留轮廓线
5. 点击"生成并下载"获取结果文件

## 部署说明

### 使用 Docker 部署

1. 构建镜像：
```bash
docker build -t potrace-web .
```

2. 运行容器：
```bash
docker run -p 5000:5000 potrace-web
```

### 传统部署

1. 安装系统依赖：
```bash
# Ubuntu/Debian
apt-get update
apt-get install -y potrace python3-dev

# CentOS/RHEL
yum install -y potrace python3-devel
```

2. 安装 Python 依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python app.py
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License 