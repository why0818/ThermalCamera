import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 使用绝对导入
from config.config import set_chinese_font, HEIGHT, WIDTH, EXPECTED_SIZE, DEFAULT_FOLDER
from utils.utils import load_settings, save_settings
from data_processing.data_processing import load_thermal_data, get_extrema_info, apply_transformations, get_dynamic_figsize
from ui_components.ui_components import (
    render_sidebar_controls,
    render_file_navigation,
    render_heatmap_image,
    render_download_button,
    add_annotations,
    render_histogram_and_stats  # 新增
)

# ==============================
# 页面配置
# ==============================
st.set_page_config(page_title="热成像RAW查看器", layout="wide")
# st.title("🌡️ 热成像 RAW 文件热图查看器")

# ==============================
# 初始化会话状态（含持久化配置）
# ==============================
if "file_list" not in st.session_state:
    st.session_state.file_list = []

if "file_settings" not in st.session_state:
    st.session_state.file_settings = load_settings()

# ==============================
# 侧边栏：文件夹路径
# ==============================
st.sidebar.header("📁 文件夹设置")
input_folder = st.sidebar.text_input("请输入包含 .raw 文件的文件夹路径", value=DEFAULT_FOLDER)

# 扫描文件夹
folder_path = Path(input_folder)
if folder_path.is_dir():
    raw_files = sorted(folder_path.glob("*.raw"))
    st.session_state.file_list = raw_files
else:
    st.session_state.file_list = []
    st.sidebar.error("❌ 路径无效或不是文件夹")

file_count = len(st.session_state.file_list)
if file_count > 0:
    st.sidebar.success(f"找到 {file_count} 个 .raw 文件")
    # 默认显示最后一张（最新）图片
    if "current_index" not in st.session_state:
        st.session_state.current_index = file_count - 1
else:
    st.sidebar.info("未找到 .raw 文件")

# ==============================
# 主内容区
# ==============================
if file_count == 0:
    st.info("👈 请在左侧输入有效的文件夹路径，包含 .raw 文件。")
    st.markdown("### ℹ️ 文件格式要求：")
    st.write("- 二进制文件，`float32` 格式")
    st.write("- 固定尺寸：120 行 × 160 列（76,800 字节）")
else:
    current_idx = st.session_state.current_index
    current_file = st.session_state.file_list[current_idx]
    current_filename = current_file.name

    # 初始化该文件的设置（如果不存在）
    if current_filename not in st.session_state.file_settings:
        st.session_state.file_settings[current_filename] = {
            "rotate_ccw": False  # 逆时针旋转90度
        }

    # 渲染侧边栏控制
    rotate_ccw, use_manual_range, placeholder_vmin_vmax, selected_cmap, annotate_extrema = \
        render_sidebar_controls(current_filename, st.session_state.file_settings, save_settings)

    # 渲染文件导航（在主区域上方）
    render_file_navigation(file_count)

    # ==============================
    # 绘图
    # ==============================
    try:
        data = load_thermal_data(current_file)
        data = apply_transformations(data, rotate_ccw)
        max_val, min_val, max_idx, min_idx = get_extrema_info(data)

        # 计算全局5%和95%分位数（用于默认色标范围）
        vmin_default_global = float(np.percentile(data, 1))
        vmax_default_global = float(np.percentile(data, 99))

        if use_manual_range:
            vmin, vmax = placeholder_vmin_vmax.slider(
                "色标温度范围 (℃)",
                min_value=min_val,
                max_value=max_val,
                value=(vmin_default_global, vmax_default_global),
                step=0.1
            )
        else:
            vmin, vmax = vmin_default_global, vmax_default_global

        # === 1. 动态 figsize（保持像素比例）===
        fig_width, fig_height = get_dynamic_figsize(data, rotate_ccw)

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        im = ax.imshow(data, cmap=selected_cmap, interpolation="nearest", vmin=vmin, vmax=vmax, aspect='equal')
        plt.colorbar(im, ax=ax, shrink=0.8)
        ax.axis('off')  # 隐藏坐标轴，更干净

        # 图像标注
        if annotate_extrema:
            add_annotations(ax, data, max_val, min_val, max_idx, min_idx)

        # 创建双栏布局
        left_col, right_col = st.columns([5, 3])

        with left_col:
            # 渲染热图
            render_heatmap_image(fig, current_filename, rotate_ccw)
            # 渲染下载按钮
            render_download_button(fig, current_file)

        with right_col:
            # 渲染直方图和统计信息
            render_histogram_and_stats(data)

    except Exception as e:
        st.error(f"处理文件时出错：{e}")
        st.exception(e)
    
