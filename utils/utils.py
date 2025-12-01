import json
import streamlit as st
# 使用绝对导入
from config.config import SETTINGS_FILE  # 从 config 包的 config.py 模块导入

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