import matplotlib
import platform
from pathlib import Path

# ==============================
# 全局配置与常量
# ==============================

# 配置文件路径
SETTINGS_FILE = Path(__file__).parent.parent / "thermal_settings.json"

# 热图参数
HEIGHT, WIDTH = 120, 160
EXPECTED_SIZE = HEIGHT * WIDTH * 4
DEFAULT_FOLDER = r"D:\Users\why\Documents\DCIM"

# 可选色带
COLORMAP_OPTIONS = ["inferno", "gray", "magma", "jet", "coolwarm"]
DEFAULT_CMAP = "inferno"

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