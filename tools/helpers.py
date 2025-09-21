# 使用 ffmpeg-python 替换视频中的音频
import hashlib


def calculate_md5(file_path):
    """计算给定文件的MD5值"""
    md5_hash = hashlib.md5()  # 创建MD5对象
    with open(file_path, "rb") as f:  # 以二进制模式打开文件
        for chunk in iter(lambda: f.read(4096), b""):  # 分块读取文件
            md5_hash.update(chunk)  # 更新MD5对象
    return md5_hash.hexdigest()  # 返回十六进制的MD5值
