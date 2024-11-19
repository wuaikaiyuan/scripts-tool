import sys
import time
import os
import subprocess
from datetime import timedelta
from faster_whisper import WhisperModel

model_size = "distil-large-v2"

# 获取文件夹中的所有视频文件
def get_video_files(folder_path):
    video_files = []
    for file in os.listdir(folder_path):
        if file.endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.mpeg', '.mpg', '.m4v')):
            print(file)
            video_files.append(file)
    return video_files

# 将视频文件转换为音频文件
def video_to_audio(video_file):
# if video_file.endswith(".mp4"):
    #     audio_file = video_file.replace(".mp4", ".wav")
    #     # 使用ffmpeg将视频文件转换为音频文件
    #     command = f"ffmpeg -i {video_file} -ar 16000 -acodec pcm_s16le -map a -vn {audio_file}"
    #     os.system(command)
    # elif video_file.endswith(".avi"):
    #     audio_file = video_file.replace(".avi", ".mp3")
    #     command = f"ffmpeg -i {video_file} -ar 16000 -acodec libmp3lame -ab 128k -map a -f mp3 -vn {audio_file}"
    #     os.system(command)
    # elif video_file.endswith(".mkv"):
    #     audio_file = video_file.replace(".mkv", ".wav")
    #     command = f"ffmpeg -i {video_file} -ar 16000 -q:a 0 -map a -f wav -ab 128k -vn {audio_file}"
    #     os.system(command)
    # elif video_file.endswith(".mpeg"):
    #     audio_file = video_file.replace(".mpeg", ".mp3")
    #     command = f"ffmpeg -i {video_file} -f mp3 -ab 192k -vn {audio_file}"
    #     os.system(command)
    # ---------------------------------------------------------------------
    
    if video_file.endswith(".mp4"):
        audio_file = video_file.replace(".mp4", ".wav")
        command = ["ffmpeg", "-i", video_file, "-ar", "16000", "-acodec", "pcm_s16le", "-ac", "1", "-map", "a", "-ab", "128k", "-vn", "-f", "wav", "-y", audio_file]
    elif video_file.endswith(".avi"):
        audio_file = video_file.replace(".avi", ".wav")
        # command = ["ffmpeg", "-i", video_file, "-ar", "16000", "-acodec", "libmp3lame", "-map", "a", "-ab", "128k", "-vn", "-f", "mp3", "-y", audio_file]
        command = ["ffmpeg", "-i", video_file, "-ar", "16000", "-acodec", "pcm_s16le", "-ac", "1", "-map", "a", "-ab", "128k", "-vn", "-f", "wav", "-y", audio_file]
    elif video_file.endswith(".mkv"):
        audio_file = video_file.replace(".mkv", ".wav")
        # Adjust the audio bitrate to compress the output WAV file
        command = ["ffmpeg", "-i", video_file, "-ar", "16000", "-acodec", "pcm_s16le", "-ac", "1", "-map", "a", "-ab", "128k", "-vn", "-f", "wav", "-y", audio_file]
    else:
        audio_file = video_file.replace(".mpeg", ".mp3")
        command = ["ffmpeg", "-i", video_file, "-ar", "16000", "-acodec", "libmp3lame", "-ac", "1", "-map", "a", "-ab", "128k", "-vn", "-f", "mp3", "-y", audio_file]

    print(f"1.1 视频转音频: {video_file} -> {audio_file} ####开始")
    print(f"1.1 命令: {' '.join(command)}")
    start_time = time.time()
    # 使用subprocess.Popen来执行命令并捕获实时输出
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in process.stdout:
        print(line, end="")
    time_use = time.time() - start_time
    print(f"1.2 视频转音频: {video_file} -> {audio_file} ####结束, 耗时: {time_use:.2f} 秒")

    if audio_file.endswith(".mp3"):
        print(f"2.1 mp3转wav: {audio_file} -> {wav_file} ####开始")
        wav_file = audio_file.replace(".mp3", ".wav")
        convert_command = ["ffmpeg", "-i", audio_file, "-ar", "16000", "-acodec", "pcm_f32le", "-vn", "-f", "wav", "-y", wav_file]
        print(f"1.1 命令: {' '.join(convert_command)}")
        start_time = time.time()
        process = subprocess.run(convert_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            print(line, end="")
        time_use = time.time() - start_time
        print(f"2.2 mp3转wav: {audio_file} -> {wav_file} ####结束, 耗时: {time_use:.2f} 秒")
        audio_file = wav_file

    return audio_file

# 语音识别文字
def transcribe_audio(audio_file, language = "en"):
    """ 使用faster_whisper进行语音识别 """
    print(f"3.1 音频识别: {audio_file}  ###开始")
    start_time = time.time()
    model = WhisperModel(model_size, device="cuda", compute_type="int8", local_files_only=False)
    segments, info = model.transcribe(audio_file, beam_size=5, condition_on_previous_text=False, language=language)
    # for segment in segments:
    #     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    time_use = time.time() - start_time
    print(f"3.2 音频识别: {audio_file}  ###结束, 耗时: {time_use:.2f} 秒")

    output_srt_path = audio_file.replace(".wav", ".srt")

    # Generate SRT file from the transcription segments
    # 创建SRT文件内容
    srt_content = []
    for i, segment in enumerate(segments):
        start_time = format_timestamp(segment.start)
        end_time = format_timestamp(segment.end)
        text = segment.text.strip()
        line = f"{i + 1}\n{start_time} --> {end_time}\n{text}\n"
        print(line)
        srt_content.append(line)
    print(f"SRT 字幕内容: {srt_content}")
    # 将SRT内容写入文件
    with open(output_srt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_content))
    print(f"SRT file created: {output_srt_path}")

    return output_srt_path


def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

def main(folder_path):
    # 获取当前目录下的所有视频文件
    files = get_video_files(folder_path)
    # 遍历所有文件，将视频文件转换为音频文件
    for file in files:
        print(f"[{file}] 处理中 ...... ")
        try:
            audio_file = video_to_audio(file)
            print(f"[视频]提取[音频]成功：{file} -> {audio_file}")
            srt_file = transcribe_audio(audio_file, "en")
            print(f"[音频]提取[字幕]成功：{audio_file} -> {srt_file}")
        except Exception as e:
            print(f"{file} 视频提取字幕失败: {str(e)}")

if __name__ == "__main__":
    
    # if len(sys.argv) > 1:
    #     folder_path = sys.argv[1]
    # else:
    #     folder_path = os.getcwd()
    # print(f"当前处理文件夹路径: {folder_path}")
    # os.chdir(folder_path)

    # start_total_time = time.time()
    # main(folder_path)
    # total_time_used = time.time() - start_total_time
    # print(f"Total processing time: {total_time_used:.2f} seconds")

    # srt_file = transcribe_audio("I:/人生七年/1.1964.wav", "en")
    video_to_audio("I://人生七年//1.1964.avi");

