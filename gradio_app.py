import asyncio
import os
import time
from datetime import datetime

import gradio as gr
from dotenv import load_dotenv

from tools.add_srt import transform_ass, add_srt
from tools.dubbing_srt import dubbing_srt
from tools.helpers import calculate_md5
from tools.replace_audio import replace_audio_ffmpeg_python
from tools.translate_srt import translate_srt
from tools.video_to_mp3 import extract_audio
from tools.whisperx_srt import convert_audio_to_srt

os.environ["no_proxy"] = "localhost,127.0.0.1,::1"

# 加载 .env 文件
load_dotenv()

choices = ['生成中文配音视频（速度一般）', '仅提取中文字幕（速度较快）', '生成中文配音视频+中文字幕（速度最慢）']
concurrency_limit = int(os.getenv('CONCURRENCY_LIMIT', 3))


def info_report(output_text, info):
    info = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {info}'
    print(info)
    output_text.append(info)
    return gr.update(value='\n'.join(output_text), lines=min(len(output_text) + 1, 20)), gr.update(
        visible=False), gr.update(visible=False)


# 定义一个模拟命令执行的生成器函数
def execute_command(input_video, type):
    output_text = []
    try:
        if type == choices[0]:
            skip_step = [7]
        elif type == choices[1]:
            skip_step = [4, 5, 7]
        else:
            skip_step = []
        if not os.path.exists(input_video):
            yield info_report(output_text, '视频不存在：' + input_video)
            return
        video_id = calculate_md5(input_video)
        yield info_report(output_text, f'视频ID为：{video_id}')
        prefix = 'result/' + video_id

        os.makedirs(prefix, exist_ok=True)

        # 步骤1-提取视频的音频
        time1 = 0
        output_audio = prefix + '/source.mp3'
        if not os.path.exists(output_audio):
            start_time = time.time()
            yield info_report(output_text, f'提取音频进行中...')
            extract_audio(input_video, output_audio)
            yield info_report(output_text, f"提取音频成功")
            time1 = time.time() - start_time

        # 步骤2-将视频音频进行语音识别，提取字幕
        time2 = 0
        srt_file = prefix + "/source.srt"
        if not os.path.exists(srt_file):
            start_time = time.time()
            yield info_report(output_text, f"提取字幕进行中...")
            convert_audio_to_srt(output_audio, srt_file)
            yield info_report(output_text, f"提取字幕成功")
            time2 = time.time() - start_time

        # 步骤3-将字幕文件翻译成中文
        time3 = 0
        translated_filename = prefix + '/translated.srt'
        if not os.path.exists(translated_filename):
            start_time = time.time()
            yield info_report(output_text, f"翻译字幕进行中...")
            translate_srt(srt_file, translated_filename)
            yield info_report(output_text, f"翻译字幕成功")
            time3 = time.time() - start_time

        # 步骤4-给字幕配音
        time4 = 0
        translated_mp3 = prefix + '/translated.mp3'
        if not os.path.exists(translated_mp3) and 4 not in skip_step:
            start_time = time.time()
            yield info_report(output_text, f"字幕配音进行中...")
            asyncio.run(dubbing_srt(translated_filename, translated_mp3))
            yield info_report(output_text, f"字幕配音成功")
            time4 = time.time() - start_time

        # 步骤5-使用翻译后的音频替换原始音频
        time5 = 0
        output_video_file = prefix + '/target.mp4'  # 最终输出的视频文件
        if not os.path.exists(output_video_file) and 5 not in skip_step:
            start_time = time.time()
            yield info_report(output_text, f"替换原始音频进行中...")
            replace_audio_ffmpeg_python(input_video, translated_mp3, output_video_file)
            yield info_report(output_text, f"替换原始音频成功")
            time5 = time.time() - start_time

        # 步骤6-字幕格式转换
        time6 = 0
        target_srt = os.path.splitext(output_video_file)[0] + '.srt'
        target_ass = os.path.splitext(output_video_file)[0] + '.ass'
        if not os.path.exists(target_ass):
            start_time = time.time()
            yield info_report(output_text, f"字幕格式转换进行中...")
            transform_ass(translated_filename, target_srt, target_ass)
            yield info_report(output_text, f"字幕格式转换成功")
            time6 = time.time() - start_time

        # 步骤7-添加字幕
        time7 = 0
        srt_video = prefix + '/target_srt.mp4'
        if 7 not in skip_step:
            target_mp4 = output_video_file
            output_video_file = srt_video
            if not os.path.exists(output_video_file):
                start_time = time.time()
                yield info_report(output_text, f"添加字幕进行中...")
                add_srt(target_mp4, target_ass, output_video_file)
                yield info_report(output_text, f"添加字幕成功")
                time7 = time.time() - start_time

        yield info_report(output_text, f'步骤1-提取音频耗时：{time1}')
        yield info_report(output_text, f'步骤2-提取字幕耗时：{time2}')
        yield info_report(output_text, f'步骤3-翻译字幕耗时：{time3}')
        yield info_report(output_text, f'步骤4-字幕配音耗时：{time4}')
        yield info_report(output_text, f'步骤5-视频音频替换耗时：{time5}')
        yield info_report(output_text, f'步骤6-字幕格式转换耗时：{time6}')
        yield info_report(output_text, f'步骤7-添加字幕耗时：{time7}')
        yield info_report(output_text, f'总耗时：{time1 + time2 + time3 + time4 + time5 + time6 + time7}')
        if type == choices[1]:
            yield gr.update(value='\n'.join(output_text), lines=min(len(output_text) + 1, 20)), gr.update(
                value=target_srt, visible=True), gr.update(
                visible=False)
        else:
            yield gr.update(value='\n'.join(output_text), lines=min(len(output_text) + 1, 20)), gr.update(
                value=target_srt, visible=True), gr.update(
                value=output_video_file, visible=True)
    except BaseException as e:
        yield info_report(output_text, f'处理异常，报错信息：{str(e)}')


# 创建 Gradio Interface，指定多输出
demo = gr.Interface(
    concurrency_limit=concurrency_limit,
    title='视频音频自动翻译与配音工具',
    description='<div style="text-align: center;">视频音频自动翻译与配音工具，目前仅支持将英文视频翻译成中文视频，后续有需要会持续改进...</div>',
    fn=execute_command,  # 调用的函数
    inputs=[
        gr.Video(label='原始视频文件输入'),
        gr.Radio(choices, value=choices[0], label='处理类型')
    ],
    outputs=[  # 输出组件类型
        gr.Textbox(label="处理信息输出", lines=1),  # 文本框显示执行状态
        gr.File(label="SRT字幕文件下载"),  # 显示保存的视频
        gr.Video(label="目标视频输出"),  # 显示保存的视频
    ],
    flagging_mode='never',
)

# 启动 Gradio
demo.launch(server_name='0.0.0.0', server_port=7860, share=False)
