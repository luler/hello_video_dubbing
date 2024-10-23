import os
import time

from snowflake import SnowflakeGenerator

from tools.add_srt import add_srt
from tools.dubbing_srt import dubbing_srt
from tools.replace_audio import replace_audio_ffmpeg_python
from tools.translate_srt import translate_srt
from tools.video_to_mp3 import extract_audio
from tools.whisperx_srt import convert_audio_to_srt

# 输入视频，一般只需要修改这个
input_video = 'test.mp4'

gen = SnowflakeGenerator(1)
prefix = 'result/' + str(next(gen))
os.makedirs(prefix, exist_ok=True)
output_audio = prefix + '/source.mp3'

# 提取视频的音频
start_time = time.time()
extract_audio(input_video, output_audio)
time1 = time.time() - start_time

# 将视频音频进行语音识别，提取字幕
start_time = time.time()
srt_file = prefix + "/source.srt"
convert_audio_to_srt(output_audio, srt_file)
time2 = time.time() - start_time

# 将字幕文件翻译成中文
start_time = time.time()
translated_filename = prefix + '/translated.srt'
translate_srt(srt_file, translated_filename)
time3 = time.time() - start_time

# 给字幕配音
start_time = time.time()
translated_mp3 = prefix + '/translated.mp3'
dubbing_srt(translated_filename, translated_mp3)
time4 = time.time() - start_time

# 使用翻译后的音频替换原始音频
start_time = time.time()
output_video_file = prefix + '/target.mp4'  # 最终输出的视频文件
replace_audio_ffmpeg_python(input_video, translated_mp3, output_video_file)
time5 = time.time() - start_time

# 添加字幕
start_time = time.time()
srt_video = prefix + '/target_srt.mp4'
add_srt(output_video_file, translated_filename, srt_video)
time6 = time.time() - start_time

print('步骤1-提取音频耗时：' + time1)
print('步骤2-提取字幕耗时：' + time2)
print('步骤3-翻译字幕耗时：' + time3)
print('步骤4-字幕配音耗时：' + time4)
print('步骤5-视频音频替换耗时：' + time5)
print('步骤6-添加字幕耗时：' + time6)
