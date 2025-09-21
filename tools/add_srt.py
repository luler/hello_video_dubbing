# 使用 ffmpeg-python 替换视频中的音频
import re
import subprocess

import pysrt


def wrap_text(text, max_length):
    """
    将字幕文本根据 max_length 自动换行
    """
    words = list(text)
    lines = []
    current_line = []

    for word in words:
        # 如果当前行加入这个单词后超出长度，先保存当前行
        current_line.append(word)
        if len(current_line) >= max_length:
            lines.append(''.join(current_line))
            current_line = []

    # 保存最后一行
    if current_line:
        lines.append(''.join(current_line))

    return '\n'.join(lines)


def process_srt_with_pysrt(input_file, output_file, max_length=30):
    """
    使用 pysrt 库读取 SRT 文件，对字幕文本超过 max_length 的行自动换行
    """
    # 读取 SRT 文件
    subs = pysrt.open(input_file, encoding='utf-8')

    # 处理每一条字幕
    for sub in subs:
        # 获取原始字幕文本
        original_text = sub.text
        # 去除原始文本中的多余换行符，并自动换行
        wrapped_text = wrap_text(original_text.replace('\n', ''), max_length)
        # 更新字幕文本
        sub.text = wrapped_text

    # 将处理后的字幕保存到新的文件中
    subs.save(output_file, encoding='utf-8')


def transform_ass(translated_srt, target_srt, target_ass):
    print('字幕格式转换进行中...')
    # 字幕太长换行处理
    process_srt_with_pysrt(translated_srt, target_srt)
    # 转换srt为ass格式，设定固定样式
    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-i', target_srt,
        target_ass
    ]
    subprocess.run(ffmpeg_command, check=True)
    # 替换ass样式
    with open(target_ass, 'r', encoding='utf-8') as f:
        content = f.read()

        # 使用正则表达式查找并替换Style行
    pattern = r"^Style: Default,.+$"  # 匹配以"Style: Default,"开头，以任意字符结尾的行
    new_style = 'Style: Default,SimSun,12,&H00ffff,&Hffffff,&H80000000,&H00000000,0,0,0,0,100,100,0,0,3,2,0,2,10,10,10,1'
    new_content = re.sub(pattern, new_style, content, flags=re.MULTILINE)

    with open(target_ass, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('字幕格式转换成功')


def add_srt(video_path, target_ass, output_path):
    print('添加字幕进行中...')
    # ffmpeg命令
    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-i', video_path,
        # '-vf', f"subtitles={target_srt}:force_style='FontSize=12'",
        '-vf', f"ass={target_ass}",
        '-c:a', 'copy',
        output_path
    ]

    # 执行ffmpeg命令
    subprocess.run(ffmpeg_command, check=True)
    print(f"添加字幕成功，输出视频：{output_path}")
