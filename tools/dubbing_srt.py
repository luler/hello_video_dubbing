import asyncio
import os

import edge_tts
import pysrt
from dotenv import load_dotenv
from pydub import AudioSegment

# 加载 .env 文件
load_dotenv()

edge_tts_voice = os.getenv('EDGE_TTS_VOICE', 'zh-CN-YunxiNeural')


# 读取并解析 SRT 文件
def srt_to_text_and_time(file_path):
    subs = pysrt.open(file_path)
    subtitles = []

    for sub in subs:
        start_time = sub.start.to_time()  # 获取开始时间
        end_time = sub.end.to_time()  # 获取结束时间
        text = sub.text
        subtitles.append((text, start_time, end_time))

    return subtitles


# 将字幕段落转换为语音并保存到单独的文件，使用 edge_tts (同步调用)
def text_to_speech_edge_sync(text, index, voice="zh-CN-YunxiNeural", rate="+0%", output_dir="temp_audio"):
    # 确保临时文件夹存在
    os.makedirs(output_dir, exist_ok=True)
    temp_audio_file = f"{output_dir}/temp_{index}.mp3"

    # 使用 asyncio.run() 来调用异步保存操作
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    asyncio.run(communicate.save(temp_audio_file))

    return temp_audio_file


# 计算时间差，返回毫秒
def time_difference(start, end):
    delta = (end.hour - start.hour) * 3600 + (end.minute - start.minute) * 60 + (end.second - start.second)
    delta = delta * 1000 + (end.microsecond - start.microsecond) / 1000  # 转换为毫秒
    return delta


# 根据时间调整音频播放速度
def adjust_audio_speed(audio_segment, target_duration_ms):
    current_duration_ms = len(audio_segment)

    if current_duration_ms > target_duration_ms:
        speed_factor = current_duration_ms / target_duration_ms
        audio_segment = audio_segment.speedup(playback_speed=speed_factor, crossfade=30, chunk_size=50)

    return audio_segment


# 合并语音文件并根据时间戳插入空白
def dubbing_srt(srt_file, output_mp3, rate="+0%"):
    print(f"字幕配音进行中...")
    # 读取并解析 SRT 文件
    subtitles = srt_to_text_and_time(srt_file)
    # 初始化空白音频
    combined = AudioSegment.silent(duration=0)
    last_end_time = 0  # 记录上一个字幕结束时间，单位毫秒

    for index, (text, start_time, end_time) in enumerate(subtitles):
        # 将字幕文本转为语音文件 (同步调用)
        temp_audio_file = text_to_speech_edge_sync(text, index, edge_tts_voice, rate)
        audio_segment = AudioSegment.from_mp3(temp_audio_file)

        # 计算当前段落开始时间与上一个段落结束时间的差值
        start_time_ms = (
                                start_time.hour * 3600 + start_time.minute * 60 + start_time.second) * 1000 + start_time.microsecond / 1000
        end_time_ms = (
                              end_time.hour * 3600 + end_time.minute * 60 + end_time.second) * 1000 + end_time.microsecond / 1000

        # 计算该字幕应该持续的时长
        subtitle_duration_ms = end_time_ms - start_time_ms

        # 调整音频片段播放速度
        audio_segment = adjust_audio_speed(audio_segment, subtitle_duration_ms)

        # 计算空白间隔的时长
        gap_duration = max(0, start_time_ms - last_end_time)  # 时间差，单位毫秒

        # 添加空白的间隔
        combined += AudioSegment.silent(duration=gap_duration)

        # 添加字幕音频
        combined += audio_segment

        # 更新最后一个字幕的结束时间
        last_end_time = start_time_ms + len(audio_segment)

        # 删除临时音频文件
        os.remove(temp_audio_file)

    # 保存最终的合成音频
    combined.export(output_mp3, format="mp3")
    print(f"字幕配音成功，配音文件已保存到：{output_mp3}")
