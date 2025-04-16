import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import random
import serial



# Initialize audio player
pygame.mixer.init()

# #Setup serial connection
# arduino = serial.Serial('/dev/ttyACM0', 9600)
# time.sleep(2)

# Match threshold for fuzzy matching
MATCH_THRESHOLD = 50

# Wake words
wake_words = ["hey robot", "hello buddy"]

# List of predefined commands
commands = [
    "turn head left",
    "turn head right",
    "open your mouth",
    "close your mouth",
    "look right",
    "look left",
    "look up",
    "look down",
    "off",
    "repeat that",
    "can you sing"
]
wake_responses = [
    "Yes, I am listening...",
    "Hello, I'm here!",
    "Hey, you called?",
    "Ready for your command!",
    "Yes buddy?",
    "At your service!",
    "What's up?"
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
    return process.extractOne(command, commands, scorer=fuzz.partial_ratio)

# Match wake word
def match_wake_word(text):
    match, score = process.extractOne(text, wake_words, scorer=fuzz.token_set_ratio)
    return score >= 80  # Adjust threshold for wake word as needed

# Main loop
def listen_and_respond():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    last_command = ""

    print("Press [Enter] and say the wake word to activate me. Press Ctrl+C to exit.")

    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening for wake word...")
            audio = recognizer.listen(source)

        try:
            trigger_text = recognizer.recognize_google(audio).lower()
            print("Wake input:", trigger_text)

            if not match_wake_word(trigger_text):
                print("Wake word not detected.")
                speak("Say 'Hey Robot' to wake me up.")
                continue

            print("Wake word detected!")

            # Now listen for actual command
            speak(random.choice(wake_responses))
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                print("Listening for command...")
                audio = recognizer.listen(source)

            command = recognizer.recognize_google(audio).lower()
            print("You said:", command)

            best_match, score = match_command(command)
            print(f"Best match: {best_match} with score {score}")

            if score >= MATCH_THRESHOLD:
                if best_match == "repeat that" and last_command:
                    speak(f"Repeating: {last_command}")
                    best_match = last_command  # Re-trigger
                else:
                    last_command = best_match

                # Handle command actions
                if best_match == "turn head left":
                    # arduino.write(b'headleft\n')
                    speak("Turning my head left")
                elif best_match == "turn head right":
                    # arduino.write(b'headright\n')
                    speak("Turning my head right")
                elif best_match == "open your mouth":
                    # arduino.write(b'openmouth\n')
                    speak("Opening my mouth. HAHAHa")
                elif best_match == "close your mouth":
                    # arduino.write(b'closemouth\n')
                    speak("Closing my mouth")
                elif best_match == "look right":
                    # arduino.write(b'lookright\n')
                    speak("Seeing right")
                elif best_match == "look left":
                    # arduino.write(b'lookleft\n')
                    speak("Seeing left")
                elif best_match == "look up":
                    # arduino.write(b'lookup\n')
                    speak("Looking up")
                elif best_match == "look down":
                    # arduino.write(b'lookdown\n')
                    speak("Looking down")
                elif best_match == "on":
                    speak("Powering on")
                elif best_match == "off":
                    speak("Powering off")

                elif "can you sing" in command:
                    speak("No, I can't sing, but I can say a poetry for you.")

                    poems = [
                    [
                    "Roses are red, violets are blue,",
                    "I'm a robot, and I'm here with you.",
                    "No tunes I can carry, no melodies to hum,",
                    "But my words can dance, like a poetic drum."
                    ],
                    [
                    "Beep beep boop, the circuits hum,",
                    "I speak in code, not just for fun.",
                    "But listen close, and you might see,",
                    "Even robots write poetry."
                    ]
                    ]

                    poetry_lines = random.choice(poems)
                    for line in poetry_lines:
                        speak(line)
                elif "Introduce yoursel" or "Tell me about you" or "who are you" in command:
                    speak("Hello! I am your intelligent assistant robot, proudly developed at High Tech Pioneer, a hub of innovation and technology in Nepal. Ive been built by passionate engineers and researchers pioneering the future of robotics and artificial intelligence. My purpose is to assist you with everyday tasks, understand your voice commands, and interact with the physical world using advanced sensors and precision motors. I'm constantly learning and evolving to become smarter and more helpful each day. Just let me know what you need—and Ill be at your service.")
            else:
                speak("I am sorry, can you repeat your command once again.")

        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError:
            print("Speech recognition service unavailable.")
            speak("Service unavailable.")

if __name__ == "__main__":
    try:
        listen_and_respond()
    except KeyboardInterrupt:
        print("\nExiting...")
