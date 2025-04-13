import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import os

# Step 1: Record audio
def record_audio(filename="audio.wav", duration=5, fs=44100):
    print("🎙️ Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, recording)
    print(f"✅ Audio saved to {filename}")

# Step 2: Transcribe using Whisper
def transcribe_audio(filename="audio.wav"):
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found!")
        return
    
    print("🧠 Loading Whisper tiny model...")
    model = whisper.load_model("tiny")

    print("🔍 Transcribing...")
    result = model.transcribe(filename)
    
    print("\n📝 Transcription:")
    print(result["text"])

# Run the whole thing
if __name__ == "__main__":
    record_audio()
    transcribe_audio()
