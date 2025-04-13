import tkinter as tk
from gtts import gTTS
import pygame
import os
import serial
import time
import speech_recognition as sr
import threading

# Initialize Pygame for audio
pygame.mixer.init()

# Setup Serial (update port if needed)
# arduino = serial.Serial('/dev/ttyACM0', 9600)
# time.sleep(2)

recognizer = sr.Recognizer()

# Text-to-speech function
def speak(text, filename="voice.mp3"):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    os.remove(filename)

# Listen, recognize, send to Arduino, speak
def listen_and_process():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        update_label("🎤 Listening...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        update_label(f"You said: {command}")

        if "left" in command:
            # arduino.write(b'left\n')
            speak("Turning left")
        elif "right" in command:
            # arduino.write(b'right\n')
            speak("Turning right")
        elif "on" in command:
            # arduino.write(b'on\n')
            speak("Powering on")
        elif "off" in command:
            # arduino.write(b'off\n')
            speak("Powering off")
        else:
            speak("Sorry, I didn't understand")
    except sr.UnknownValueError:
        update_label("Could not understand audio.")
        # speak("Sorry, I couldn't understand.")
    except sr.RequestError:
        update_label("Speech recognition service is unavailable.")
        speak("Service unavailable.")

# Update GUI label text
def update_label(text):
    label_var.set(text)

# Handle keypress (space to start listening)
def on_keypress(event):
    if event.keysym == 'space':
        threading.Thread(target=listen_and_process, daemon=True).start()

# GUI Setup
root = tk.Tk()
root.title("Voice Controlled Robot")
root.geometry("400x200")
root.configure(bg="#222")

label_var = tk.StringVar()
label_var.set("Press SPACE to speak...")

label = tk.Label(root, textvariable=label_var, font=("Arial", 16), fg="#0f0", bg="#222")
label.pack(pady=60)

root.bind('<KeyPress>', on_keypress)
root.mainloop()
