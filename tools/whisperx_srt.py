import datetime

import torch
import whisperx

device = "cuda" if torch.cuda.is_available() else "cpu"
language = 'en'
model = whisperx.load_model("base.en", device, compute_type='float32')
model_a, metadata = whisperx.load_align_model(language_code=language, device=device)


def format_time(seconds):
    return str(datetime.timedelta(seconds=seconds)).replace(".", ",")[:11]


def convert_audio_to_srt(audio_file, srt_file):
    print(f"提取字幕进行中...")
    # 加载音频文件
    audio = whisperx.load_audio(audio_file)
    # 1. 转录
    result = model.transcribe(audio, language=language)
    # 2. 对齐
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    # 3. 生成 SRT 文件
    with open(srt_file, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result["segments"], start=1):
            start_time = format_time(segment["start"])
            end_time = format_time(segment["end"])
            text = segment["text"].strip()

            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")

    print(f"提取字幕成功，生成如下字幕文件: {srt_file}")
