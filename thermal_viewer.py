import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from pathlib import Path
import json
import os
import matplotlib
import platform

# ==============================
# 中文支持
# ==============================
def set_chinese_font():
    system = platform.system()
    if system == "Windows":
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    elif system == "Darwin":
        matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang HK', 'DejaVu Sans']
    else:
        matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False

set_chinese_font()

# ==============================
# 配置文件路径（与脚本同目录）
# ==============================
SETTINGS_FILE = Path(__file__).parent / "thermal_settings.json"

def load_settings():
    """从 JSON 文件加载配置"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"⚠️ 配置文件加载失败，使用默认设置: {e}")
            return {}
    return {}

def save_settings(settings):
    """将配置保存到 JSON 文件"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"❌ 无法保存配置: {e}")

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
DEFAULT_FOLDER = r"D:\Users\why\Documents\DCIM"
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
# 固定参数
# ==============================
HEIGHT, WIDTH = 120, 160
EXPECTED_SIZE = HEIGHT * WIDTH * 4

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

    # ==============================
    # 🛠️ 显示选项（只保留逆时针旋转）
    # ==============================
    st.sidebar.markdown("### 🖼️ 显示选项")
    rotate_key = f"rotate_{current_filename}"

    # 初始化控件状态
    if rotate_key not in st.session_state:
        st.session_state[rotate_key] = st.session_state.file_settings[current_filename]["rotate_ccw"]

    rotate_ccw = st.sidebar.checkbox("逆时针旋转90°", key=rotate_key)

    # 更新并保存设置
    new_rotate = st.session_state[rotate_key]
    if st.session_state.file_settings[current_filename]["rotate_ccw"] != new_rotate:
        st.session_state.file_settings[current_filename]["rotate_ccw"] = new_rotate
        save_settings(st.session_state.file_settings)


    # ==============================
    # 色标范围设置
    # ==============================
    st.sidebar.markdown("### 🎚️ 色标范围")
    use_manual_range = st.sidebar.checkbox("手动设置色标范围", value=False)
    placeholder_vmin_vmax = st.sidebar.empty()

    # ==============================
    # 侧边栏：全局色带选择（非持久化）
    # ==============================
    st.sidebar.markdown("### 🎨 色带选择")
    # colormap_options = [
    #     "inferno", "plasma", "magma", "viridis", "cividis",
    #     "jet", "hot", "coolwarm", "RdYlBu", "gray"
    # ]

    colormap_options = [
        "inferno", "gray", "magma", "jet", "coolwarm"
    ]

    # 初始化默认值（只在首次）
    if "global_colormap_select" not in st.session_state:
        st.session_state.global_colormap_select = "inferno"

    # 创建 selectbox，完全由 key 管理状态
    selected_cmap = st.sidebar.selectbox(
        "选择色带",
        options=colormap_options,
        key="global_colormap_select"
    )


    st.sidebar.markdown("### 📍 标注")
    annotate_extrema = st.sidebar.checkbox("在图中标注温度极值点", value=False)

    # ==============================
    # 文件导航栏（上一个 | [第N张 / 跳转输入 + 按钮] | 下一个）
    # ==============================
    if file_count > 1:
        nav_col1, nav_col2, nav_col3 = st.columns([1, 4.2, 1])
        
        # 左：上一个
        with nav_col1:
            if st.session_state.current_index > 0:
                if st.button("⬅️ 上一个", key="prev_file", use_container_width=True):
                    st.session_state.current_index -= 1
                    st.rerun()
            else:
                st.button("⬅️ 上一个", key="prev_file_disabled", use_container_width=True, disabled=True)

        # 中：居中区域 —— 文字 + 输入 + 跳转按钮 在同一行
        with nav_col2:
            current_display = st.session_state.current_index + 1
            
            # 使用子列：文字 | 输入框 | 按钮
            _, sub_col1, sub_col2, sub_col3, _ = st.columns([3, 2, 1, 1.5, 3])
            
            with sub_col1:
                st.markdown(f"""
                    <div style="
                        display: flex; 
                        justify-content: center; 
                        align-items: center; 
                        height: 40px;
                        font-size: 15px;
                        white-space: nowrap;
                    ">
                        第 {current_display} 张 / 共 {file_count} 张
                    </div>
                """, unsafe_allow_html=True)
            
            with sub_col2:
                jump_to = st.number_input(
                    "跳转到第 N 张",
                    min_value=1,
                    max_value=file_count,
                    value=current_display,
                    step=1,
                    label_visibility="collapsed"
                )
            
            with sub_col3:
                if st.button("跳转", key="jump_button", use_container_width=True):
                    st.session_state.current_index = jump_to - 1
                    st.rerun()

        # 右：下一个
        with nav_col3:
            if st.session_state.current_index < file_count - 1:
                if st.button("下一个 ➡️", key="next_file", use_container_width=True):
                    st.session_state.current_index += 1
                    st.rerun()
            else:
                st.button("下一个 ➡️", key="next_file_disabled", use_container_width=True, disabled=True)

    # ==============================
    # 绘图
    # ==============================
    try:
        with open(current_file, "rb") as f:
            raw_bytes = f.read()

        if len(raw_bytes) != EXPECTED_SIZE:
            st.error(f"文件大小错误！应为 {EXPECTED_SIZE} 字节，实际 {len(raw_bytes)} 字节。")
        else:
            data = np.frombuffer(raw_bytes, dtype=np.float32).reshape((HEIGHT, WIDTH))

            # 应用旋转（逆时针90度 = np.rot90(data, k=1)）
            if rotate_ccw:
                data = np.rot90(data, k=1)

            max_val = float(np.max(data))
            min_val = float(np.min(data))
            max_idx = np.unravel_index(np.argmax(data), data.shape)
            min_idx = np.unravel_index(np.argmin(data), data.shape)

            # 计算全局5%和95%分位数（用于默认色标范围）
            vmin_default_global = np.percentile(data, 1)
            vmax_default_global = np.percentile(data, 99)

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
            current_h, current_w = data.shape
            scale = 0.06

            # 根据方向微调缩放（可选）
            if rotate_ccw:
                scale = 0.05  # 竖图稍小一点
            else:
                scale = 0.06  # 横图稍大

            fig_width = min(current_w * scale, 10.0)  # 最大 10 英寸宽
            fig_height = min(current_h * scale, 8.0)  # 最大 8 英寸高

            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            cmap_to_use = st.session_state.get("global_colormap_select", "inferno")
            im = ax.imshow(data, cmap=cmap_to_use, interpolation="nearest", vmin=vmin, vmax=vmax, aspect='equal')
            plt.colorbar(im, ax=ax, shrink=0.8)
            ax.axis('off')  # 隐藏坐标轴，更干净

            # 图像标注
            if annotate_extrema:
                current_h, current_w = data.shape  # ✅ 关键：用当前图像尺寸！

                # --- 最高温 ---
                y_max, x_max = max_idx  # 注意：max_idx 是基于旋转后的 data 的！
                ax.plot(x_max, y_max, 'g+', markersize=10, markeredgewidth=2)
                
                # 垂直方向（y 轴）
                if y_max <= current_h // 2:
                    text_y_max = min(y_max + 5, current_h - 1)
                    va_max = 'bottom'
                else:
                    text_y_max = max(y_max - 5, 0)
                    va_max = 'top'
                
                # 水平方向（x 轴）
                if x_max < 10:
                    text_x_max = x_max + 5
                    ha_max = 'left'
                elif x_max > current_w - 10:
                    text_x_max = x_max - 5
                    ha_max = 'right'
                else:
                    text_x_max = x_max
                    ha_max = 'center'
                
                ax.text(text_x_max, text_y_max, f'{max_val:.1f}℃', color='green', fontsize=12,
                        ha=ha_max, va=va_max, weight='bold')

                # --- 最低温 ---
                y_min, x_min = min_idx
                ax.plot(x_min, y_min, 'g+', markersize=10, markeredgewidth=2)
                
                # 垂直方向
                if y_min <= current_h // 2:
                    text_y_min = min(y_min + 5, current_h - 1)
                    va_min = 'bottom'
                else:
                    text_y_min = max(y_min - 5, 0)
                    va_min = 'top'
                
                # 水平方向
                if x_min < 10:
                    text_x_min = x_min + 5
                    ha_min = 'left'
                elif x_min > current_w - 10:
                    text_x_min = x_min - 5
                    ha_min = 'right'
                else:
                    text_x_min = x_min
                    ha_min = 'center'
                
                ax.text(text_x_min, text_y_min, f'{min_val:.1f}℃', color='green', fontsize=12,
                        ha=ha_min, va=va_min, weight='bold')

            # === 2. 根据方向选择列比例 ===
            if rotate_ccw:
                # 竖图：用更窄的中间列
                cols = st.columns([1, 1.8, 1])
            else:
                # 横图：用更宽的中间列
                cols = st.columns([1, 3, 1])

            with cols[1]:  # 中间列
                # 添加文件名标题（小字号，居中）
                st.markdown(
                    f'<div style="text-align: center; font-size: 14px; color: #555;">{current_filename}</div>',
                    unsafe_allow_html=True
                )
                st.pyplot(fig)

            # 温度统计
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**最高温**: {max_val:.2f} ℃ 位于 (x={max_idx[1]}, y={max_idx[0]})")
            with c2:
                st.write(f"**最低温**: {min_val:.2f} ℃ 位于 (x={min_idx[1]}, y={min_idx[0]})")
                
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            st.download_button(
                "📥 下载热图 (PNG)",
                buf.getvalue(),
                file_name=f"{current_file.stem}_heatmap.png",
                mime="image/png"
            )

    except Exception as e:
        st.error(f"处理文件时出错：{e}")
        st.exception(e)