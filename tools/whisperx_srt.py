import datetime

import torch
import whisperx


def format_time(seconds):
    return str(datetime.timedelta(seconds=seconds)).replace(".", ",")[:11]


def convert_audio_to_srt(audio_file, srt_file):
    print(f"提取字幕进行中...")
    language = 'en'
    # 1. 转录
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisperx.load_model("base.en", device, compute_type='float32')

    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, language=language)

    # 2. 对齐
    model_a, metadata = whisperx.load_align_model(language_code=language, device=device)
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

    print(f"提取字幕完成，生成如下字幕文件: {srt_file}")
