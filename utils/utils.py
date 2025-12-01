import json
import streamlit as st
# 使用绝对导入
from config.config import SETTINGS_FILE  # 从 config 包的 config.py 模块导入

def load_settings():
    """从 JSON 文件加载配置"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                print(f"DEBUG: Loaded settings from {SETTINGS_FILE}: {settings}")  # 调试输出
                return settings
        except Exception as e:
            st.warning(f"⚠️ 配置文件加载失败，使用默认设置: {e}")
            return {}
    else:
        print(f"DEBUG: Settings file {SETTINGS_FILE} does not exist, returning empty dict")  # 调试输出
        return {}

def save_settings(settings):
    """将配置保存到 JSON 文件"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        print(f"DEBUG: Saved settings to {SETTINGS_FILE}: {settings}")  # 调试输出
    except Exception as e:
        st.error(f"❌ 无法保存配置: {e}")