import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np

# ==============================
# UI 组件
# ==============================

def render_sidebar_controls(current_filename, file_settings, save_settings_func):
    """渲染侧边栏控制组件"""
    st.sidebar.markdown("### 🖼️ 显示选项")
    rotate_key = f"rotate_{current_filename}"

    # 初始化控件状态：从缓存中获取当前文件的设置（如果存在）
    if rotate_key not in st.session_state:
        # 第一次访问此文件，从缓存加载默认值
        st.session_state[rotate_key] = file_settings.get(current_filename, {}).get("rotate_ccw", False)

    rotate_ccw = st.sidebar.checkbox("逆时针旋转90°", key=rotate_key)

    # 更新并保存设置（仅当用户操作导致值改变时）
    new_rotate = st.session_state[rotate_key]
    # 获取当前文件在缓存中的旧值
    cached_rotate = file_settings.get(current_filename, {}).get("rotate_ccw", False)
    
    if cached_rotate != new_rotate:
        # 用户修改了设置，更新缓存并保存
        if current_filename not in file_settings:
            file_settings[current_filename] = {}
        file_settings[current_filename]["rotate_ccw"] = new_rotate
        save_settings_func(file_settings)

    # 色标范围
    st.sidebar.markdown("### 🎚️ 色标范围")
    use_manual_range = st.sidebar.checkbox("手动设置色标范围", value=False)
    placeholder_vmin_vmax = st.sidebar.empty()

    # 色带选择
    st.sidebar.markdown("### 🎨 色带选择")
    colormap_options = [
        "inferno", "gray", "magma", "jet", "coolwarm"
    ]

    # 初始化默认值（只在首次）
    if "global_colormap_select" not in st.session_state:
        st.session_state["global_colormap_select"] = "inferno"

    # 创建 selectbox，完全由 key 管理状态
    selected_cmap = st.sidebar.selectbox(
        "选择色带",
        options=colormap_options,
        key="global_colormap_select"
    )

    st.sidebar.markdown("### 📍 标注")
    annotate_extrema = st.sidebar.checkbox("在图中标注温度极值点", value=False)

    return rotate_ccw, use_manual_range, placeholder_vmin_vmax, selected_cmap, annotate_extrema

def render_file_navigation(file_count):
    """渲染文件导航栏"""
    if file_count <= 1:
        return

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

def render_statistics(max_val, min_val, avg_temp, center_temp, max_idx, min_idx):
    """渲染温度统计信息"""
    # st.subheader("📊 温度统计")
    st.write(f"**最高温**: {max_val:.2f} ℃ 位于 (x={max_idx[1]}, y={max_idx[0]})")
    st.write(f"**最低温**: {min_val:.2f} ℃ 位于 (x={min_idx[1]}, y={min_idx[0]})")
    st.write(f"**平均温度**: {avg_temp:.2f} ℃")
    st.write(f"**中心温度**: {center_temp:.2f} ℃")

def render_heatmap_image(fig, current_filename, rotate_ccw):
    """渲染热图图像及其文件名标题"""
    # === 2. 根据方向选择列比例 ===
    if rotate_ccw:
        # 竖图：用更窄的中间列
        cols = st.columns([0.2, 1.8, 0.2])
    else:
        # 横图：用更宽的中间列
        cols = st.columns([0.2, 3, 0.2])

    with cols[1]:  # 中间列
        # 添加文件名标题（小字号，居中）
        st.markdown(
            f'<div style="text-align: center; font-size: 14px; color: #555;">{current_filename}</div>',
            unsafe_allow_html=True
        )
        st.pyplot(fig)

def render_download_button(fig, current_file):
    """渲染下载按钮"""
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    st.download_button(
        "📥 下载热图 (PNG)",
        buf.getvalue(),
        file_name=f"{current_file.stem}_heatmap.png",
        mime="image/png"
    )

def render_histogram_and_stats(data):
    """渲染直方图和统计信息"""
    # 创建右栏
    right_col = st.columns([1])[0]
    with right_col:
        # 直方图
        # st.subheader("📈 温度分布直方图")
        fig_hist, ax_hist = plt.subplots(figsize=(4, 3))
        ax_hist.hist(data.flatten(), bins=50, color='skyblue', edgecolor='black')
        ax_hist.set_xlabel('温度 (℃)')
        ax_hist.set_ylabel('频次')
        st.pyplot(fig_hist)
        plt.close(fig_hist)  # 避免内存泄漏

        # 计算统计信息
        max_val = float(np.max(data))
        min_val = float(np.min(data))
        avg_temp = float(np.mean(data))
        center_temp = float(data[data.shape[0]//2, data.shape[1]//2])  # 中心点温度

        # 渲染统计信息
        render_statistics(max_val, min_val, avg_temp, center_temp, 
                         np.unravel_index(np.argmax(data), data.shape),
                         np.unravel_index(np.argmin(data), data.shape))

def add_annotations(ax, data, max_val, min_val, max_idx, min_idx):
    """在图像上添加温度极值标注"""
    current_h, current_w = data.shape

    # 图像标注
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