# 准备 Google Translate API
import pysrt
from googletrans import Translator

translator = Translator()


def translate_srt(srt_filename, translated_filename):
    print(f"翻译字幕进行中...")
    # 读取原始的 SRT 文件
    subs = pysrt.open(srt_filename, encoding='utf-8')

    # 翻译每个字幕段落的文本
    for sub in subs:
        original_text = sub.text
        translated_text = translator.translate(original_text, dest='zh-CN').text
        sub.text = translated_text

    # 生成翻译后的 SRT 文件
    subs.save(translated_filename, encoding='utf-8')
    print(f"翻译字幕成功，翻译字幕文件：{translated_filename}")
