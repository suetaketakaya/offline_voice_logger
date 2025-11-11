import soundcard as sc
import numpy as np
import tempfile
import wave
from faster_whisper import WhisperModel
import torch
import os

SAMPLE_RATE = 16000
CHANNELS = 2
DURATION = 10  # 秒

def record_system_audio(duration=DURATION):
    default_speaker = sc.default_speaker()
    mic = sc.get_microphone(id=str(default_speaker.name), include_loopback=True)

    print(f"🎧 録音開始: {mic.name}")
    data = mic.record(samplerate=SAMPLE_RATE, numframes=int(duration * SAMPLE_RATE))
    print("✅ 録音終了")
    return data

def save_wav(path, data, samplerate=SAMPLE_RATE):
    data = (data * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(data.shape[1])
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(data.tobytes())

def transcribe_audio(path):
    
    base_dir = r"C:\Users\suetake\OFFLINEVOICELOGGER\models\models--Systran--faster-whisper-medium"
    snapshot_dirs = [d for d in os.listdir(os.path.join(base_dir, "snapshots"))]
    model_dir = os.path.join(base_dir, "snapshots", snapshot_dirs[0])
    print("model_dir : ", model_dir)
    print("モデルパス:", model_dir)


    # ✅ ローカルモデルを使うため local_files_only=True を指定
    model = WhisperModel(
        model_dir,
        device="cuda" if torch.cuda.is_available() else "cpu",
        compute_type="float16",
        local_files_only=True
    )

    print("🗣️ 音声認識中...")
    segments, info = model.transcribe(path, beam_size=5)
    print(f"Detected language: {info.language}")
    for seg in segments:
        print(f"[{seg.start:.2f}s → {seg.end:.2f}s] {seg.text}")

if __name__ == "__main__":
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio = record_system_audio()
        save_wav(tmp.name, audio)
        transcribe_audio(tmp.name)
