import speech_recognition as sr
import requests
import asyncio
from edge_tts import Communicate
import sounddevice as sd
import soundfile as sf

RASA_ENDPOINT = "http://localhost:5005/webhooks/rest/webhook"
AUDIO_FILE = "user_input.wav"

# Function to get voice input from the user
def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="en")
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Google STT error: {e}")
        return None

# Function to send user input to the Rasa bot and get a response
def send_to_rasa(message):
    response = requests.post(RASA_ENDPOINT, json={"sender": "user", "message": message})
    if response.status_code == 200:
        responses = response.json()
        if responses:
            bot_reply = responses[0].get("text", "")
            print(f"Rasa says: {bot_reply}")
            return bot_reply
    print("No response from Rasa")
    return "मलाई केही थाहा भएन।"

# Function to convert the text response to speech and play it
async def speak_response(text):
    # Initialize the TTS communication with Microsoft Edge TTS
    communicate = Communicate(text, voice="ne-NP-SagarNeural")
    
    # Save the speech to a file (e.g., speech_output.wav)
    await communicate.save("speech_output.wav")
    
    # Read the saved file and play the audio using sounddevice
    data, samplerate = sf.read("speech_output.wav")
    sd.play(data, samplerate)
    sd.wait()  # Wait until the audio is finished playing

# Main conversation loop
if __name__ == "__main__":
    while True:
        # Get voice input from the user
        user_input = get_voice_input()
        
        if user_input:
            # Send the input to Rasa and get the bot's reply
            bot_reply = send_to_rasa(user_input)
            
            # Convert the bot's reply to speech and play it
            asyncio.run(speak_response(bot_reply))