import asyncio
import math
import os

import edge_tts
import pysrt
from dotenv import load_dotenv
from pydub import AudioSegment

# 加载 .env 文件
load_dotenv()

edge_tts_voice = os.getenv('EDGE_TTS_VOICE', 'zh-CN-YunxiNeural')

# 设置代理
proxy = None
if os.getenv('https_proxy'):
    proxy = os.getenv('https_proxy')
if os.getenv('http_proxy'):
    proxy = os.getenv('http_proxy')

edge_tts_connect_timeout = int(os.getenv('EDGE_TTS_CONNECT_TIMEOUT', 20))
edge_tts_max_concurrency = int(os.getenv('EDGE_TTS_MAX_CONCURRENCY', 3))


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


# 将字幕段落转换为语音并保存到单独的文件
async def text_to_speech_edge(text, index, text_length, semaphore, voice="zh-CN-YunxiNeural", rate="+0%",
                              output_dir="temp_audio"):
    if not output_dir:
        output_dir = '.'
    async with semaphore:  # Limit concurrency here
        temp_audio_file = f"{output_dir}/temp_{index}.mp3"
        communicator = edge_tts.Communicate(text, voice=voice, rate=rate, proxy=proxy,
                                            connect_timeout=edge_tts_connect_timeout)
        await communicator.save(temp_audio_file)
        print(f'字幕配音进度：{index}/{text_length}')
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
        # print(speed_factor)
        if 1.2 <= speed_factor < 1.5:
            audio_segment = audio_segment.speedup(playback_speed=speed_factor, crossfade=30, chunk_size=50)
        elif speed_factor >= 1.5:
            audio_segment = audio_segment.speedup(playback_speed=speed_factor, crossfade=30, chunk_size=20)
        else:
            audio_segment = audio_segment.speedup(playback_speed=speed_factor)

    return audio_segment


# 合并语音文件并根据时间戳插入空白
async def dubbing_srt(srt_file, output_mp3, rate="+0%"):
    print(f"字幕配音进行中...")
    # 读取并解析 SRT 文件
    subtitles = srt_to_text_and_time(srt_file)
    # 初始化空白音频
    combined = AudioSegment.silent(duration=0)
    last_end_time = 0  # 记录上一个字幕结束时间，单位毫秒
    gap_duration1 = 0
    output_dir = os.path.dirname(srt_file)

    text_length = len(subtitles)
    semaphore = asyncio.Semaphore(edge_tts_max_concurrency)
    tasks = [
        text_to_speech_edge(text, index, text_length, semaphore, edge_tts_voice, rate, output_dir)
        for index, (text, _, _) in enumerate(subtitles)
    ]
    audio_files = await asyncio.gather(*tasks)

    for index, (text, start_time, end_time) in enumerate(subtitles):
        # 将字幕文本转为语音文件
        temp_audio_file = audio_files[index]
        audio_segment = AudioSegment.from_mp3(temp_audio_file)

        # 计算当前段落开始时间与上一个段落结束时间的差值
        start_time_ms = (
                                start_time.hour * 3600 + start_time.minute * 60 + start_time.second) * 1000 + start_time.microsecond / 1000
        end_time_ms = (
                              end_time.hour * 3600 + end_time.minute * 60 + end_time.second) * 1000 + end_time.microsecond / 1000
        # 计算当前字幕与下一个字幕的时间间隙，可用于配音时间调配
        next_gap_duration = 0
        if index + 1 < text_length:
            next_start_time = subtitles[index + 1][1]
            next_start_time_ms = (
                                         next_start_time.hour * 3600 + next_start_time.minute * 60 + next_start_time.second) * 1000 + next_start_time.microsecond / 1000
            next_gap_duration = next_start_time_ms - end_time_ms

        # 计算空白间隔的时长
        gap_duration2 = max(0, start_time_ms - last_end_time)  # 时间差，单位毫秒

        # 添加空白的间隔
        combined += AudioSegment.silent(duration=max(0, gap_duration1 + gap_duration2))

        # 计算该字幕应该持续的时长
        subtitle_duration_ms = end_time_ms - start_time_ms

        # 判断配音市场和字幕时长之间的差别进行不同处理
        current_duration_ms = len(audio_segment)
        if current_duration_ms <= subtitle_duration_ms + next_gap_duration:  # 将全部空隙占用
            gap_duration1 = subtitle_duration_ms - current_duration_ms
        else:
            # 需要调速，后续空隙截一半
            available_gap_duration = math.floor(next_gap_duration / 2)
            # 调整音频片段播放速度
            audio_segment = adjust_audio_speed(audio_segment, subtitle_duration_ms + available_gap_duration)
            current_duration_ms = len(audio_segment)
            # 多还少补
            gap_duration1 = 0 - (current_duration_ms - subtitle_duration_ms)

        # 添加字幕音频
        combined += audio_segment

        # 更新最后一个字幕的结束时间
        last_end_time = end_time_ms

        # 删除临时音频文件
        os.remove(temp_audio_file)

    # 保存最终的合成音频
    combined.export(output_mp3, format="mp3")
    print(f"字幕配音成功，配音文件已保存到：{output_mp3}")
