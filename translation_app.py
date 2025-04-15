import sys
import traceback
import logging
import os
import customtkinter as ctk
import sounddevice as sd
import numpy as np
import wave
import tempfile
import whisper
from openai import OpenAI
from dotenv import load_dotenv

# .env 読み込み
load_dotenv()

# ログ設定
logging.basicConfig(level=logging.DEBUG)

# 例外処理
def custom_excepthook(exctype, value, tb):
    logging.error("An error occurred:")
    traceback.print_exception(exctype, value, tb)
    update_text_output(f"❌ エラー発生: {str(value)}\n")

sys.excepthook = custom_excepthook

# ChatGPT互換API設定
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    logging.error("APIキーが設定されていません。")
else:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

# Whisperモデルの読み込み
model = whisper.load_model("base")

# アプリウィンドウ
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.title("音声翻訳アプリ")
app.geometry("600x550")

# テキスト出力エリア
text_output = ctk.CTkTextbox(app, height=150, wrap="word")
text_output.pack(pady=10, padx=20, fill="both", expand=True)

# 翻訳出力エリア
translation_output = ctk.CTkTextbox(app, height=100, wrap="word")
translation_output.pack(pady=10, padx=20, fill="both", expand=True)

# 翻訳言語選択
language_var = ctk.StringVar(value="ja")

language_frame = ctk.CTkFrame(app)
language_frame.pack(pady=10)

ctk.CTkLabel(language_frame, text="翻訳先:").pack(side="left", padx=10)

lang_options = {
    "日本語": "ja",
    "英語": "en",
    "ドイツ語": "de"
}

for label, value in lang_options.items():
    ctk.CTkRadioButton(
        language_frame,
        text=label,
        variable=language_var,
        value=value
    ).pack(side="left", padx=5)

# 状態管理
is_recording = False
audio_path = None

def update_text_output(text):
    app.after(0, lambda: text_output.insert("end", text))

def update_translation_output(text):
    app.after(0, lambda: translation_output.insert("end", text))

def record_audio(duration=5):
    global is_recording, audio_path
    logging.info("Recording audio...")
    update_text_output("🎙️ 録音中...\n")
    audio = []

    def callback(indata, frames, time, status):
        audio.append(indata.copy())

    try:
        with sd.InputStream(callback=callback, channels=1, samplerate=16000, dtype='int16'):
            sd.sleep(duration * 1000)
    except Exception as e:
        logging.error(f"録音エラー: {e}")
        update_text_output(f"❌ 録音エラー: {str(e)}\n")
        return None

    audio_np = np.concatenate(audio, axis=0)
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with wave.open(temp_wav.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_np.tobytes())

    update_text_output("✅ 録音完了\n")
    audio_path = temp_wav.name
    return temp_wav.name

def transcribe_audio(file_path):
    logging.info(f"Transcribing audio from {file_path}...")
    update_text_output("🔍 音声認識中...\n")
    try:
        result = model.transcribe(file_path)
        transcription = result['text']
        update_text_output(f"📝 認識結果: {transcription}\n")
        return transcription
    except Exception as e:
        logging.error(f"音声認識エラー: {e}")
        update_text_output(f"❌ 音声認識エラー: {str(e)}\n")
        return None

def translate_text(text, target_lang):
    logging.info(f"Translating to {target_lang}: {text}")
    update_text_output("🌐 翻訳中...\n")

    if target_lang == "ja":
        prompt = "以下の文章を日本語に翻訳してください。"
    elif target_lang == "en":
        prompt = "Please translate the following text into English."
    elif target_lang == "de":
        prompt = "Bitte übersetze den folgenden Text ins Deutsche."
    else:
        prompt = "Please translate the following text."

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
        )
        translated = completion.choices[0].message.content
        update_translation_output(f"📘 翻訳結果: {translated}\n")
        return translated
    except Exception as e:
        logging.error(f"翻訳エラー: {e}")
        update_translation_output(f"❌ 翻訳エラー: {str(e)}\n")
        return None

def run_pipeline():
    try:
        logging.info("Running pipeline...")
        update_text_output("処理中...\n")
        text_output.delete("1.0", "end")
        translation_output.delete("1.0", "end")

        if not is_recording:
            return

        audio_path = record_audio(duration=5)
        if audio_path is None:
            return

        transcription = transcribe_audio(audio_path)
        if transcription is None:
            return

        target_lang = language_var.get()
        translate_text(transcription, target_lang)

    except Exception as e:
        logging.error(f"エラー: {e}")
        update_text_output(f"❌ エラー発生: {str(e)}\n")

def toggle_recording():
    global is_recording
    is_recording = not is_recording
    if is_recording:
        record_btn.configure(text="停止")
        run_pipeline()
    else:
        record_btn.configure(text="🎤 録音開始")
        update_text_output("録音停止しました。\n")

# 録音ボタン
record_btn = ctk.CTkButton(app, text="🎤 録音開始", command=toggle_recording)
record_btn.pack(pady=20)

# メインループ
try:
    app.mainloop()
except Exception as e:
    logging.error(f"メインループ中のエラー: {str(e)}")
