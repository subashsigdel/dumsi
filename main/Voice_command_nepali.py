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

# Setup serial connection (uncomment if using Arduino)
# arduino = serial.Serial('/dev/ttyACM0', 9600)
# time.sleep(2)

# Match threshold for fuzzy matching
MATCH_THRESHOLD = 50

# Nepali wake words
wake_words = ["हे रोबोट", "नमस्कार साथी", "कान्छा"]

# Predefined Nepali commands
commands = [
    "बायाँ फर्क",         # turn left
    "दायाँ फर्क",         # turn right
    "मुख खोल",           # open your mouth
    "मुख बन्द गर",        # close your mouth
    "दायाँ हेर",         # look right
    "बायाँ हेर",         # look left
    "माथि हेर",          # look up
    "तल हेर",            # look down
    "अन",                # on
    "अफ",                # off
    "फेरी भन"            # repeat that
]

# Nepali wake responses
wake_responses = [
    "हजुर, म सुन्दैछु...",
    "नमस्कार, म यहाँ छु!",
    "के भन्यौ मलाई?",
    "म तयार छु!",
    "के काम छ साथी?",
    "सेवामा उपस्थित छु!",
    "के गर्नु पर्‍यो?"
]

# Nepali Text-to-Speech
def speak(text, filename="tts.mp3"):
    tts = gTTS(text=text, lang='ne')
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
    print(f"Wake word match: {match} (Score: {score})")
    return score >= 80

# Main loop
def listen_and_respond():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    last_command = ""

    print("प्रेस गर्नुहोस् [Enter] र 'हे रोबोट', 'नमस्कार साथी' वा 'कान्छा' भन्नुहोस्। Ctrl+C थिचेर बाहिर जानुहोस्।")

    while True:
        input()
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Wake word सुन्दैछु...")
            audio = recognizer.listen(source)

        try:
            trigger_text = recognizer.recognize_google(audio, language='ne-NP').lower()
            print("Wake input:", trigger_text)

            if not match_wake_word(trigger_text):
                print("Wake word भेटिएन।")
                speak("मलाई बोलाउन 'हे रोबोट', 'नमस्कार साथी' वा 'कान्छा' भन्नुहोस्।")
                continue

            print("Wake word भेटियो!")
            speak(random.choice(wake_responses))

            # Now listen for actual command
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                print("आदेश सुन्दैछु...")
                audio = recognizer.listen(source)

            command = recognizer.recognize_google(audio, language='ne-NP').lower()
            print("तपाईंले भन्नुभयो:", command)

            best_match, score = match_command(command)
            print(f"सबैभन्दा मिल्दो: {best_match} with score {score}")

            if score >= MATCH_THRESHOLD:
                if best_match == "फेरी भन" and last_command:
                    speak(f"फेरि भन्दैछु: {last_command}")
                    best_match = last_command
                else:
                    last_command = best_match

                # Command actions
                if best_match == "बायाँ फर्क":
                    # arduino.write(b'headleft\n')
                    speak("टाउको बायाँ फर्काउँदैछु।")
                elif best_match == "दायाँ फर्क":
                    # arduino.write(b'headright\n')
                    speak("टाउको दायाँ फर्काउँदैछु।")
                elif best_match == "मुख खोल":
                    # arduino.write(b'openmouth\n')
                    speak("मुख खोल्दैछु। हाहाहा")
                elif best_match == "मुख बन्द गर":
                    # arduino.write(b'closemouth\n')
                    speak("मुख बन्द गर्दैछु।")
                elif best_match == "दायाँ हेर":
                    # arduino.write(b'lookright\n')
                    speak("दायाँ हेरिरहेको छु।")
                elif best_match == "बायाँ हेर":
                    # arduino.write(b'lookleft\n')
                    speak("बायाँ हेरिरहेको छु।")
                elif best_match == "माथि हेर":
                    # arduino.write(b'lookup\n')
                    speak("माथि हेर्दैछु।")
                elif best_match == "तल हेर":
                    # arduino.write(b'lookdown\n')
                    speak("तल हेर्दैछु।")
                elif best_match == "अन":
                    speak("पावर अन गर्दैछु।")
                elif best_match == "अफ":
                    speak("पावर अफ गर्दैछु।")
            else:
                speak("माफ गर्नुहोस्, मैले बुझिन।")

        except sr.UnknownValueError:
            print("ध्वनि बुझ्न सकिएन।")
        except sr.RequestError:
            print("Speech recognition सेवा उपलब्ध छैन।")
            speak("सेवा उपलब्ध छैन।")

if __name__ == "__main__":
    try:
        listen_and_respond()
    except KeyboardInterrupt:
        print("\nबाहिरिंदै...")
