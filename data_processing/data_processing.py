import numpy as np
from pathlib import Path

# ==============================
# 固定参数
# ==============================
from config.config import HEIGHT, WIDTH, EXPECTED_SIZE

def load_thermal_data(file_path):
    with open(file_path, "rb") as f:
        raw_bytes = f.read()

    if len(raw_bytes) != EXPECTED_SIZE:
        raise ValueError(f"文件大小错误！应为 {EXPECTED_SIZE} 字节，实际 {len(raw_bytes)} 字节。")
    else:
        data = np.frombuffer(raw_bytes, dtype=np.float32).reshape((HEIGHT, WIDTH))
        return data

def get_extrema_info(data):
    max_val = float(np.max(data))
    max_idx = np.unravel_index(np.argmax(data), data.shape)
    min_val = float(np.min(data))
    min_idx = np.unravel_index(np.argmin(data), data.shape)
    return max_val, min_val, max_idx, min_idx

def apply_transformations(data, rotate_ccw):
    if rotate_ccw:
        data = np.rot90(data, k=1)
    return data

def get_dynamic_figsize(data, rotate_ccw):
    current_h, current_w = data.shape
    scale = 0.06

    # 根据方向微调缩放（可选）
    if rotate_ccw:
        scale = 0.05  # 竖图稍小一点
    else:
        scale = 0.06  # 横图稍大

    fig_width = min(current_w * scale, 10.0)  # 最大 10 英寸宽
    fig_height = min(current_h * scale, 8.0)  # 最大 8 英寸高
    return fig_width, fig_height