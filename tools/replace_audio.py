# 使用 ffmpeg-python 替换视频中的音频
import subprocess


def replace_audio_ffmpeg_python(video_path, audio_path, output_path):
    print('替换原始音频进行中...')
    # ffmpeg命令
    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-i', video_path,
        '-i', audio_path,
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_path
    ]

    # 执行ffmpeg命令
    subprocess.run(ffmpeg_command, check=True)
    print(f"替换原始音频成功，成功输出视频：{output_path}")
