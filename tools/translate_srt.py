# 准备 Google Translate API
import math
import os

import pysrt
import requests
from dotenv import load_dotenv
from googletrans import Translator

# 加载 .env 文件
load_dotenv()

translator = Translator()
api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('OPENAI_BASE_URL')
model = os.getenv('OPENAI_MODEL')
translate_type = os.getenv('TRANSLATE_TYPE')
translate_batch_size = int(os.getenv('TRANSLATE_BATCH_SIZE', 20))


def ai_translate_text(text):
    url = base_url + "/chat/completions"
    # Set up the headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Create the data payload for the request
    data = {
        "model": model,  # Specify the model you want to use
        "messages": [
            {
                "role": "user",
                "content": f'请将以下 SRT 字幕内容精确翻译成中文。请保持字幕编号、时间戳和格式完全不变。翻译应准确传达原文意思，符合中文的表达习惯，语言自然流畅，语境和风格一致。只需提供翻译结果，不要添加任何旁白或说明。字幕内容如下：{text}'
            }
        ],
        'stream': False,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f'大模型翻译异常：{response.text}')
        exit()


def translate_srt(srt_filename, translated_filename):
    print(f"翻译字幕进行中...")
    if translate_type == 'openai':
        with open(srt_filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        batch_size = translate_batch_size
        batch_size *= 4  # 每4行为一个字幕
        batch_srt = ''
        batch_srt_data = []
        times = math.ceil(len(lines) / batch_size)
        for i, line in enumerate(lines, start=1):
            batch_srt += line
            if i % batch_size == 0:
                batch_srt = ai_translate_text(batch_srt).strip()
                batch_srt_data.append(batch_srt)
                batch_srt = ''
                print(f'大语言模型翻译进度：{len(batch_srt_data)}/{times}')

        if batch_srt:
            batch_srt = ai_translate_text(batch_srt).strip()
            batch_srt_data.append(batch_srt)
            print(f'大语言模型翻译进度：{len(batch_srt_data)}/{times}')
        # 翻译结果写入目标文件
        with open(translated_filename, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(batch_srt_data))
    else:
        # 读取原始的 SRT 文件
        subs = pysrt.open(srt_filename, encoding='utf-8')

        # 翻译每个字幕段落的文本
        times = len(subs)
        i = 1
        for sub in subs:
            original_text = sub.text
            translated_text = translator.translate(original_text, dest='zh-CN').text
            sub.text = translated_text
            print(f'谷歌翻译进度：{i}/{times}')
            i += 1

        # 生成翻译后的 SRT 文件
        subs.save(translated_filename, encoding='utf-8')

    print(f"翻译字幕成功，翻译字幕文件：{translated_filename}")
