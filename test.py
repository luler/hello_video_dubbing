import asyncio

from dotenv import load_dotenv

from tools.dubbing_srt import dubbing_srt

# 加载 .env 文件
load_dotenv()

translated_filename = './translated.srt'
translated_mp3 = './translated.mp3'
asyncio.run(dubbing_srt(translated_filename, translated_mp3))
