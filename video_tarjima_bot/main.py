import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip, AudioFileClip
import openai
import uuid
import subprocess
from gtts import gTTS

# === CONFIGURATION ===
BOT_TOKEN = '8037671172:AAEcGHmMYn-C6ihjQu1BH7uYl9E6P6T7EM8'
openai.api_key = 'YOUR_OPENAI_API_KEY'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === FUNCTIONS ===
def download_youtube_video(url):
    video_id = str(uuid.uuid4())
    output_path = f"videos/{video_id}.mp4"
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

def extract_audio(video_path):
    audio_path = video_path.replace('.mp4', '.mp3')
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    return audio_path

def transcribe_audio_whisper(audio_path):
    with open(audio_path, 'rb') as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript['text']

def translate_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a translator from English to Uzbek."},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']

def text_to_speech_uzbek(text, output_path):
    tts = gTTS(text=text, lang='uz')
    tts.save(output_path)

def merge_audio_video(original_video, new_audio, output_video):
    subprocess.call([
        'ffmpeg',
        '-i', original_video,
        '-i', new_audio,
        '-c:v', 'copy',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        output_video,
        '-y'
    ])

# === HANDLERS ===
@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer("Salom! YouTube videosini yuboring, men sizga o'zbek tilida tarjima qilingan versiyasini qaytaraman.")

@dp.message()
async def handle_video_link(message: Message):
    if not message.text.startswith("http"):
        await message.reply("Iltimos, YouTube havolasini yuboring!")
        return

    await message.reply("Video yuklanmoqda va tarjima qilinmoqda, biroz kuting...")

    video_path = download_youtube_video(message.text)
    audio_path = extract_audio(video_path)
    transcript = transcribe_audio_whisper(audio_path)
    uzbek_translation = translate_text(transcript)

    tts_path = video_path.replace('.mp4', '_uzbek.mp3')
    output_final_video = video_path.replace('.mp4', '_uzbek.mp4')

    text_to_speech_uzbek(uzbek_translation, tts_path)
    merge_audio_video(video_path, tts_path, output_final_video)

    await message.reply_video(types.FSInputFile(output_final_video), caption="Tarjima qilingan video")

# === START ===
if __name__ == '__main__':
    os.makedirs("videos", exist_ok=True)
    asyncio.run(dp.start_polling(bot))
