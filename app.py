import asyncio
import os
import time

from dotenv import load_dotenv

from tools.add_srt import add_srt, transform_ass
from tools.dubbing_srt import dubbing_srt
from tools.helpers import calculate_md5
from tools.replace_audio import replace_audio_ffmpeg_python
from tools.translate_srt import translate_srt
from tools.video_to_mp3 import extract_audio
from tools.whisperx_srt import convert_audio_to_srt

# 加载 .env 文件
load_dotenv()

# 输入视频，一般只需要修改这个
input_video = os.getenv('INPUT_VIDEO')
add_video_subtitle = int(os.getenv('ADD_VIDEO_SUBTITLE', 0))

if not os.path.exists(input_video):
    print('视频不存在：' + input_video)
    exit()
video_id = calculate_md5(input_video)
prefix = 'result/' + video_id

os.makedirs(prefix, exist_ok=True)

# 步骤1-提取视频的音频
time1 = 0
output_audio = prefix + '/source.mp3'
if not os.path.exists(output_audio):
    start_time = time.time()
    extract_audio(input_video, output_audio)
    time1 = time.time() - start_time

# 步骤2-将视频音频进行语音识别，提取字幕
time2 = 0
srt_file = prefix + "/source.srt"
if not os.path.exists(srt_file):
    start_time = time.time()
    convert_audio_to_srt(output_audio, srt_file)
    time2 = time.time() - start_time

# 步骤3-将字幕文件翻译成中文
time3 = 0
translated_filename = prefix + '/translated.srt'
if not os.path.exists(translated_filename):
    start_time = time.time()
    translate_srt(srt_file, translated_filename)
    time3 = time.time() - start_time

# 步骤4-给字幕配音
time4 = 0
translated_mp3 = prefix + '/translated.mp3'
if not os.path.exists(translated_mp3):
    start_time = time.time()
    asyncio.run(dubbing_srt(translated_filename, translated_mp3))
    time4 = time.time() - start_time

# 步骤5-使用翻译后的音频替换原始音频
time5 = 0
output_video_file = prefix + '/target.mp4'  # 最终输出的视频文件
if not os.path.exists(output_video_file):
    start_time = time.time()
    replace_audio_ffmpeg_python(input_video, translated_mp3, output_video_file)
    time5 = time.time() - start_time

# 步骤6-字幕格式转换
time6 = 0
target_srt = os.path.splitext(output_video_file)[0] + '.srt'
target_ass = os.path.splitext(output_video_file)[0] + '.ass'
if not os.path.exists(target_ass):
    start_time = time.time()
    transform_ass(translated_filename, target_srt, target_ass)
    time6 = time.time() - start_time

# 步骤7-添加字幕
time7 = 0
srt_video = prefix + '/target_srt.mp4'
if add_video_subtitle and not os.path.exists(srt_video):
    start_time = time.time()
    add_srt(output_video_file, target_ass, srt_video)
    time7 = time.time() - start_time

print(f'步骤1-提取音频耗时：{time1}')
print(f'步骤2-提取字幕耗时：{time2}')
print(f'步骤3-翻译字幕耗时：{time3}')
print(f'步骤4-字幕配音耗时：{time4}')
print(f'步骤5-视频音频替换耗时：{time5}')
print(f'步骤6-字幕格式转换耗时：{time6}')
print(f'步骤7-添加字幕耗时：{time7}')
print(f'总耗时：{time1 + time2 + time3 + time4 + time5 + time6 + time7}')
