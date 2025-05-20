import asyncio
from edge_tts import Communicate
import sounddevice as sd
import soundfile as sf

# Function to speak the text using edge-tts
async def speak_text(text):
    communicate = Communicate(text=text, voice="ne-NP-SagarNeural")  # Nepali voice
    await communicate.save("output.wav")
    data, samplerate = sf.read("output.wav")
    sd.play(data, samplerate)
    sd.wait()

# Direct text-to-speech
if __name__ == "__main__":
    asyncio.run(speak_text(""))  # Replace with any Nepali or English text
