import subprocess


def extract_audio(input_video, output_audio):
    try:
        print(f"提取音频进行中...")
        # ffmpeg命令
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_video,
            '-y',
            '-vn',
            '-q:a', '5',  # 适中的音频质量
            '-acodec', 'libmp3lame',
            output_audio
        ]

        # 执行ffmpeg命令
        subprocess.run(ffmpeg_command, check=True)
        print(f"提取音频成功，已提取到文件：{output_audio}")

    except Exception as e:
        print(f"提取音频失败，原因：{str(e)}")
