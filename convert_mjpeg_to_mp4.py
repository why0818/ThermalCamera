import os
import subprocess
from pathlib import Path

# ====== 配置区 ======
input_folder = r"D:\Users\why\Documents\DCIM"  # 替换为你的 .mjpeg 所在文件夹
# ===================

def convert_mjpeg_to_mp4():
    folder = Path(input_folder)
    if not folder.exists():
        print(f"❌ 输入文件夹不存在: {input_folder}")
        return

    # 查找所有 .mjpeg 文件（不区分大小写）
    mjpeg_files = list(folder.glob("*.mjpeg")) + list(folder.glob("*.MJPG")) + list(folder.glob("*.MJPEG"))
    
    if not mjpeg_files:
        print("📭 没有找到 .mjpeg 文件")
        return

    print(f"🔍 找到 {len(mjpeg_files)} 个 .mjpeg 文件，开始转换...\n")

    success_count = 0
    for mjpeg_file in sorted(mjpeg_files):
        mp4_file = mjpeg_file.with_suffix('.mp4')

        # 如果 mp4 已存在，跳过（避免重复）
        if mp4_file.exists():
            print(f"⏭️  跳过（已存在）: {mp4_file.name}")
            continue

        print(f"🔄 正在转换: {mjpeg_file.name} → {mp4_file.name}")

        # 调用 ffmpeg
        cmd = [
            'ffmpeg',
            '-i', str(mjpeg_file),
            '-c:v', 'libx264',      # 使用 H.264 编码（通用）
            '-preset', 'fast',      # 编码速度/压缩比权衡
            '-crf', '23',           # 视频质量（18~28，越小越好）
            '-pix_fmt', 'yuv420p',  # 兼容性（确保能在浏览器/手机播放）
            str(mp4_file)
        ]

        try:
            # 静默运行（不显示 ffmpeg 的 verbose 输出）
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(f"✅ 成功: {mp4_file.name}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"❌ 失败: {mjpeg_file.name}（FFmpeg 错误）")
        except FileNotFoundError:
            print("❗ 错误: 未找到 ffmpeg。请确保 ffmpeg 已安装并加入系统 PATH。")
            return

    print(f"\n🎉 完成！成功转换 {success_count}/{len(mjpeg_files)} 个文件。")

if __name__ == "__main__":
    convert_mjpeg_to_mp4()