import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import time
import threading
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import serial

# Initialize audio player
pygame.mixer.init()

# Setup serial connection for Arduino
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600)
    time.sleep(2)
    arduino_connected = True
    print("Arduino connected successfully")
except:
    arduino_connected = False
    print("Arduino connection failed - continuing in simulation mode")

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

# Dictionary mapping commands to Arduino messages
arduino_commands = {
    "turn head left": b'headleft\n',
    "turn head right": b'headright\n',
    "open your mouth": b'openmouth\n',
    "close your mouth": b'closemouth\n',
    "look right": b'lookright\n',
    "look left": b'lookleft\n',
    "on": b'on\n',
    "off": b'off\n'
}

# Response phrases for each command
responses = {
    "turn head left": "Turning my head left",
    "turn head right": "Turning my head right",
    "open your mouth": "Opening my mouth. HAHAHa",
    "close your mouth": "Closing my mouth",
    "look right": "Looking right",
    "look left": "Looking left",
    "on": "Powering on",
    "off": "Powering off"
}


# Pre-generate speech files to eliminate delay
def pregenerate_speech():
    speech_files = {}
    for command, response in responses.items():
        filename = f"speech_{command.replace(' ', '_')}.mp3"
        tts = gTTS(text=response, lang='en')
        tts.save(filename)
        speech_files[command] = filename

    # Also pre-generate error messages
    tts = gTTS(text="Sorry, I didn't understand that command", lang='en')
    tts.save("speech_error.mp3")
    speech_files["error"] = "speech_error.mp3"

    return speech_files


# Function to play pre-generated speech
def play_speech(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()


# Send command to Arduino if connected
def send_to_arduino(command_key):
    if arduino_connected:
        arduino.write(arduino_commands[command_key])
        print(f"Sent to Arduino: {arduino_commands[command_key]}")
    else:
        print(f"Would send to Arduino: {arduino_commands[command_key]}")


# Fuzzy match the command
def match_command(command):
    best_match = process.extractOne(command, commands, scorer=fuzz.partial_ratio)
    return best_match


# Main listening and processing loop
def listen_and_respond(speech_files):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Robot Voice Control System Ready")
    print("Press [Enter] to start listening. Press Ctrl+C to quit.")

    try:
        while True:
            input()  # Wait for Enter key
            print("Listening...")

            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    print("Audio captured!")
                except sr.WaitTimeoutError:
                    print("No speech detected in timeout period")
                    continue

            try:
                command = recognizer.recognize_google(audio).lower()
                print("You said:", command)

                # Get the closest match
                best_match, score = match_command(command)
                print(f"Best match: {best_match} with score {score}")

                if score >= 70:
                    # Start playing speech immediately while sending command
                    threading.Thread(target=play_speech,
                                     args=(speech_files[best_match],)).start()

                    # Send command to Arduino simultaneously
                    send_to_arduino(best_match)
                else:
                    play_speech(speech_files["error"])

            except sr.UnknownValueError:
                print("Could not understand audio.")
                play_speech(speech_files["error"])
            except sr.RequestError as e:
                print(f"Speech recognition service error: {e}")
                play_speech(speech_files["error"])

    except KeyboardInterrupt:
        print("Exiting program...")
        if arduino_connected:
            arduino.close()
        # Clean up speech files
        for filename in speech_files.values():
            if os.path.exists(filename):
                os.remove(filename)
        print("Program terminated")


if __name__ == "__main__":
    print("Preparing speech files...")
    speech_files = pregenerate_speech()
    print("Ready!")
    listen_and_respond(speech_files)