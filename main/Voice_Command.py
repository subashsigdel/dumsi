import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import serial

# Initialize audio player
pygame.mixer.init()

# Setup serial connection (uncomment if using Arduino)
arduino = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)

# List of predefined commands
commands = [
    "turn head left",
    "turn head right",
    "open your mouth",
    "close your mouth",
    "look right",
    "look left",
    "on",
    "off"
]

# Text-to-speech and play using pygame
def speak(text, filename="tts.mp3"):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    os.remove(filename)

# Fuzzy match the command
def match_command(command):
    best_match = process.extractOne(command, commands, scorer=fuzz.partial_ratio)
    return best_match

# Main listening and processing loop
def listen_and_respond():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Press [Enter] to start listening. Press Ctrl+C to quit.")

    while True:
        input()  # Wait for Enter key
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...")
            audio = recognizer.listen(source)
            print("Captured audio of length:", len(audio.frame_data), "bytes")

        try:
            command = recognizer.recognize_google(audio).lower()
            print("You said:", command)

            # Get the closest match
            best_match, score = match_command(command)
            print(f"Best match: {best_match} with score {score}")

            if score >= 80:  # Set a threshold for good match
                if best_match == "turn left":
                    arduino.write(b'headleft\n')
                    speak("Turning My head left")
                elif best_match == "turn right":
                    arduino.write(b'headright\n')
                    speak("Turning my head right")
                elif best_match == "open your mouth":
                    arduino.write(b'openmouth\n')
                    speak("Opening my mouth. HAHAHa")
                elif best_match == "close your mouth":
                    arduino.write(b'closemouth\n')
                    speak("Closing my mouth")
                elif best_match == "look right":
                    arduino.write(b'lookright\n')
                    speak("Seeing right")
                elif best_match == "look left":
                    arduino.write(b'lookleft\n')
                    speak("Seeing left")
                elif best_match == "on":
                    # arduino.write(b'on\n')
                    speak("Powering on")
                elif best_match == "off":
                    # arduino.write(b'off\n')
                    speak("Powering off")
            else:
                speak("Sorry, I didn't understand")

        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError:
            print("Speech recognition service unavailable.")
            speak("Service unavailable")

if __name__ == "__main__":
    listen_and_respond()
