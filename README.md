# 视频音频自动翻译与配音工具

一个基于AI的视频自动翻译和配音工具，支持将外语视频自动转换为中文配音版本，同时生成中文字幕。

## 功能特性

- 🎯 **自动语音识别**：使用WhisperX将视频音频转换为字幕
- 🌐 **智能翻译**：支持多语言(目前仅支持英文，可扩展)自动翻译成中文
- 🎤 **AI配音**：使用edge-tts生成自然流畅的中文语音
- 📝 **字幕生成**：自动生成SRT/ASS格式字幕文件
- 🎬 **视频合成**：自动替换原视频音频并添加字幕
- 🖥️ **Web界面**：提供Gradio图形界面，操作简单便捷
- 🐳 **Docker支持**：支持容器化部署

## 处理模式

1. **生成中文配音视频**：速度一般，生成带中文配音的视频
2. **仅提取中文字幕**：速度较快，仅生成翻译后的字幕文件
3. **生成中文配音视频+中文字幕**：速度最慢，同时生成配音和嵌入字幕

## 安装

### 本地安装

```bash
# 克隆项目
git clone https://github.com/yourusername/hello_video_dubbing.git
cd hello_video_dubbing

# 安装依赖
pip install -r requirements.txt

# 启动
python gradio_app.py
```

### Docker部署

```bash
# 构建镜像
docker build -t video-dubbing .

# 使用docker-compose运行
docker-compose up -d
```

## 配置

1. 复制环境变量配置文件：

```bash
cp .env.example .env
```

2. 编辑`.env`文件，配置相关参数：

```bash
# 并发处理限制
CONCURRENCY_LIMIT=3

#大语言模型翻译配置
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-xx

# 其他配置项...
```

## 使用方法

### 方式一：命令行模式

编辑`app.py`，修改视频路径：

```python
# 输入视频路径
input_video = 'test.mp4'
```

运行程序：

```bash
python app.py
```

### 方式二：Web界面模式（推荐）

启动Gradio界面：

```bash
python gradio_app.py
```

访问 `http://localhost:7860` 使用Web界面操作

## 项目结构

```
hello_video_dubbing/
├── tools/                  # 核心功能模块
│   ├── video_to_mp3.py    # 视频音频提取
│   ├── whisperx_srt.py    # 语音识别转字幕
│   ├── translate_srt.py   # 字幕翻译
│   ├── dubbing_srt.py     # 字幕配音生成
│   ├── replace_audio.py   # 音频替换
│   ├── add_srt.py        # 字幕嵌入
│   └── helpers.py         # 辅助函数
├── result/                # 处理结果输出目录
├── fonts/                 # 字幕字体文件
├── app.py                # 命令行主程序
├── gradio_app.py         # Web界面程序
├── requirements.txt      # Python依赖
├── Dockerfile           # Docker镜像配置
└── docker-compose.yml   # Docker Compose配置
```

## 工作流程

1. **音频提取**：从视频中提取音频流
2. **语音识别**：使用WhisperX识别音频内容生成原始字幕
3. **字幕翻译**：将原始字幕翻译成中文
4. **语音合成**：根据翻译后的字幕生成中文配音
5. **音频替换**：将原视频音频替换为中文配音
6. **字幕嵌入**：将中文字幕嵌入视频（可选）

## 依赖要求

- Python 3.11+
- FFmpeg
- CUDA（可选，用于GPU加速）

## 注意事项

- 首次运行时会自动下载WhisperX模型，需要良好的网络连接
- 处理大型视频文件时需要足够的磁盘空间
- GPU加速可显著提升处理速度
- 生成的视频和字幕文件保存在`result/`目录下

## 贡献

欢迎提交Issue和Pull Request！