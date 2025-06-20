import speech_recognition as sr
import asyncio
from edge_tts import Communicate
import sounddevice as sd
import soundfile as sf
import os

AUDIO_FILE = "speech_output.wav"

# Get voice input using Google Speech Recognition
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:

        text = r.recognize_google(audio, language="en")

        text = recognizer.recognize_google(audio, language="ne-NP")

        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Google STT error: {e}")
        return None

# Async function to handle TTS generation and playback
async def _speak_async(text):
    communicate = Communicate(text, voice="ne-NP-SagarNeural")
    await communicate.save(AUDIO_FILE)

    # Play the saved audio
    data, samplerate = sf.read(AUDIO_FILE)
    sd.play(data, samplerate)
    sd.wait()

    # Clean up
    os.remove(AUDIO_FILE)

# Wrapper to run async speak from sync code
def speak_response(text):
    asyncio.run(_speak_async(text))
