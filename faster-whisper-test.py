import torch
from faster_whisper import WhisperModel
import os
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_file_path(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")
    if not os.path.isfile(path):
        raise ValueError(f"Path is not a file: {path}")

def validate_dir_path(path):
    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Path parent dir does not exist: {path}")
    if not os.path.isdir(dir_path):
        raise ValueError(f"Path is not a dir: {path}")

def validate_model_params(model_size, device, compute_type):
    valid_sizes = ['base', 'base.en', 'distil-medium.en', 'distil-large-v2']
    valid_devices = ['cpu', 'cuda']
    valid_compute_types = ['float16', 'int8', 'int8_float16', 'int16']

    if model_size not in valid_sizes:
        raise ValueError(f"Invalid model size: {model_size}. Valid sizes: {valid_sizes}")
    if device not in valid_devices:
        raise ValueError(f"Invalid device: {device}. Valid devices: {valid_devices}")
    if compute_type not in valid_compute_types:
        raise ValueError(f"Invalid compute type: {compute_type}. Valid compute types: {valid_compute_types}")

def transcribe_audio_to_srt(audio_path, output_srt_path, model_size='base.en', device='cpu', compute_type='int8'):
    try:
        # 验证路径
        validate_file_path(audio_path)
        validate_dir_path(output_srt_path)

        # 验证模型参数
        validate_model_params(model_size, device, compute_type)

        # 加载预训练模型
        model = WhisperModel(model_size, device=device, compute_type=compute_type)

        # 进行语音转文本
        segments, _ = model.transcribe(audio_path)
        logging.info("Transcription completed.")

        # 创建SRT文件内容
        # 方式一：
        srt_content = []
        for i, segment in enumerate(segments):
            # start_time = format_timestamp(segment.start)
            # end_time = format_timestamp(segment.end)
            # text = segment.text.strip()
            # line = f"{i + 1}\n{start_time} --> {end_time}\n{text}\n"

            line = f"{i + 1}\n{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}\n{segment.text.strip()}\n"

            srt_content.append(line)
            logging.info(line)

        # 方式二：
        # srt_content = []
        # srt_content = [
        #     f"{i + 1}\n{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}\n{segment.text.strip()}\n"
        #     for i, segment in enumerate(segments)
        # ]

        logging.info("SRT content generation completed.")
        # 将SRT内容写入文件
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))
        logging.info(f"SRT文件已生成: {output_srt_path}")

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
    except ValueError as e:
        logging.error(f"Value error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

if __name__ == "__main__":  
    # model_size = "distil-large-v2"
    model_size = "distil-medium.en"

    # define our torch configuration
    device = "cuda" if torch.cuda.is_available() else "cpu"

    compute_type = "int8" if torch.cuda.is_available() else "float32"
    # 8-bit integers (INT8)
    # 16-bit integers (INT16)
    # 16-bit floating points (FP16)
    # 16-bit brain floating points (BF16)
    # 4-bit AWQ Quantization

    audio_path = "I:/人生七年/1.1964.wav"
    output_srt_path = "I:/人生七年/output1111.srt"

    transcribe_audio_to_srt(audio_path, output_srt_path, model_size, device, compute_type)
