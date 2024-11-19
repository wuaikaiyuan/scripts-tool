import os
from groq import Groq

parent_path = os.path.dirname("I:/人生七年/")

# 使用GROQ API进行语音识别
client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)
filename = os.path.join(parent_path, "1.1964.wav")
print(filename)

with open(filename, "rb") as file:
    transcription = client.audio.transcriptions.create(
      file=(filename, file.read()),
      model="distil-whisper-large-v3-en",
      prompt="Translate into Chinese",
      response_format="json",
    )
    print(transcription.text)