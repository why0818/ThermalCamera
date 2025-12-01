# 热成像RAW文件查看器与处理工具

## 项目概述

本项目是一个专为热成像数据设计的工具集，主要包含两个核心功能：

1. **热成像RAW文件可视化查看器**：基于Streamlit构建的Web应用，用于打开、查看和分析热成像RAW数据文件，支持实时调整显示参数。
2. **MJPEG到MP4转换工具**：用于批量将MJPEG格式的热成像视频文件转换为更通用的MP4格式。

## 功能特点

### 热成像RAW查看器

- 打开并可视化热成像RAW格式（float32）文件
- 支持调整显示参数：旋转、色标范围、色带选择
- 自动计算并可选标注温度极值点
- 文件导航功能，便于浏览多个热图文件
- 图像下载功能，支持保存热图为图片
- 配置持久化，保存用户偏好设置

### MJPEG到MP4转换工具

- 批量转换MJPEG/ MJPG视频文件为MP4格式
- 使用H.264编码，确保兼容性和压缩效率
- 跳过已存在的MP4文件，避免重复处理
- 提供详细的转换状态反馈

## 系统要求

- Windows 11（兼容Windows 10）
- Python 3.10+
- 对于MJPEG转换功能，需安装FFmpeg并添加到系统PATH

## 安装步骤

1. 克隆或下载本项目到本地

2. 安装Python依赖

```bash
cd d:\My_program\ThermalCamera
pip install -r requirements.txt
```

3. 安装FFmpeg（仅用于MJPEG转换功能）
   - 下载FFmpeg：[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - 解压并将bin目录添加到系统环境变量PATH中

## 使用说明

### 运行热成像RAW查看器

```bash
# 方法1：使用run.py启动（推荐）
python run.py

# 方法2：直接使用streamlit启动
streamlit run app.py
```

启动后，在浏览器中打开应用界面：
1. 在左侧输入包含RAW文件的文件夹路径
2. 使用提供的控件调整显示参数
3. 使用导航栏浏览不同的热图文件

### 使用MJPEG到MP4转换工具

1. 编辑`convert_mjpeg_to_mp4.py`文件，修改`input_folder`变量为你的MJPEG文件所在路径
2. 运行转换脚本

```bash
python convert_mjpeg_to_mp4.py
```

## 项目结构

```
ThermalCamera/
├── app.py                    # 热成像查看器主应用
├── run.py                    # 应用启动脚本
├── config/                   # 配置模块
│   ├── __init__.py
│   └── config.py             # 全局配置和常量
├── data_processing/          # 数据处理模块
│   ├── __init__.py
│   └── data_processing.py    # 热成像数据处理函数
├── ui_components/            # UI组件模块
│   ├── __init__.py
│   └── ui_components.py      # Streamlit UI组件
├── utils/                    # 工具函数模块
│   ├── __init__.py
│   └── utils.py              # 辅助功能函数
└── convert_mjpeg_to_mp4.py   # MJPEG到MP4转换工具
```

## 文件格式说明

### RAW文件格式
- 二进制文件，使用float32格式存储
- 固定尺寸：120行 × 160列（总计76,800字节）
- 直接映射为热图数据，数值代表温度值（摄氏度）

## 配置

- 全局配置位于`config/config.py`文件中
- 用户设置会保存在`thermal_settings.json`文件中（自动生成）

## 注意事项

1. 确保RAW文件格式正确（120x160，float32），否则可能无法正确加载
2. MJPEG转换功能依赖FFmpeg，请确保正确安装并配置
3. 首次使用时可能需要调整默认文件夹路径以匹配您的文件位置

## 许可证

本项目使用MIT许可证。