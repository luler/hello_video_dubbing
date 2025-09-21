# 基础镜像
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

# 设置工作目录
WORKDIR /app

# 复制当前目录中的文件到工作目录中
COPY . .

# 安装 git 以确保可以从 git 仓库拉取依赖
RUN apt-get update && apt-get install -y git ffmpeg && rm -rf /var/lib/apt/lists/* && cp fonts/* /usr/share/fonts/truetype && fc-cache -fv

# 安装依赖
RUN pip install -r requirements.txt

# 加载模型
RUN python -c 'import torch; import whisperx; device = "cuda" if torch.cuda.is_available() else "cpu"; whisperx.load_model("base.en", device, compute_type="float32"); whisperx.load_align_model(language_code="en", device=device);'

# 暴露端口
EXPOSE 7860

# 设置启动命令
CMD ["python","-u", "gradio_app.py"]