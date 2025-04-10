import logging
import threading
import os
import subprocess
import speech_recognition as sr
import pyttsx3
from google.cloud import texttospeech
import numpy as np
import json

class AudioListener:
    """Handles audio input and speech recognition"""

    def __init__(self, config):
        """Initialize the audio listener with the given configuration"""
        self.logger = logging.getLogger("dumsi.listener")
        self.config = config
        self.engine = config.get("engine", "speechrecognition")
        self.microphone_index = config.get("microphone_index", None)

        # Initialize default recognizer
        self.recognizer = sr.Recognizer()

        # Adjust for ambient noise level
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = config.get("energy_threshold", 300)

        self.logger.info(f"Initialized AudioListener with {self.engine} engine")

    def listen(self, timeout=None, phrase_time_limit=None):
        """Listen for audio input and return the audio data"""
        timeout = timeout or self.config.get("timeout", 5)
        phrase_time_limit = phrase_time_limit or self.config.get("phrase_time_limit", 5)

        self.logger.debug("Listening for audio input...")

        try:
            with sr.Microphone(device_index=self.microphone_index) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                audio = self.recognizer.listen(source, timeout=timeout,
                                               phrase_time_limit=phrase_time_limit)
                return audio
        except sr.WaitTimeoutError:
            self.logger.debug("Listen timeout - no speech detected")
            return None
        except Exception as e:
            self.logger.error(f"Error while listening: {str(e)}")
            return None

    def recognize(self, audio):
        """Convert audio to text using the selected engine"""
        if audio is None:
            return ""

        try:
            if self.engine == "speechrecognition":
                return self.recognizer.recognize_google(audio)

            elif self.engine == "vosk":
                # Convert audio to format Vosk can use
                audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)

                if self.vosk_recognizer.AcceptWaveform(audio_data):
                    result = json.loads(self.vosk_recognizer.Result())
                    return result.get("text", "")
                else:
                    result = json.loads(self.vosk_recognizer.PartialResult())
                    return result.get("partial", "")

            else:
                self.logger.error(f"Unknown speech recognition engine: {self.engine}")
                return ""

        except sr.UnknownValueError:
            self.logger.debug("Could not understand audio, playing funny.mp3")
            self.play_funny_sound()
            return ""
        except sr.RequestError as e:
            self.logger.error(f"Error with speech recognition service: {str(e)}")
            return ""
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {str(e)}")
            return ""

    def play_funny_sound(self):
        """Play the funny sound file if speech is not recognized"""
        funny_audio_path = os.path.expanduser('~/Downloads/funny.mp3')
        if os.path.exists(funny_audio_path):
            subprocess.run(["mpg123", funny_audio_path])
        else:
            self.logger.warning(f"Funny sound file not found at {funny_audio_path}")


class Speaker:
    """Handles text-to-speech functionality"""

    def __init__(self, config):
        """Initialize the speaker with the given configuration"""
        self.logger = logging.getLogger("dumsi.speaker")
        self.config = config
        self.engine_type = config.get("engine", "pyttsx3")

        if self.engine_type == "google_tts":
            try:
                self._init_google_tts()
            except Exception as e:
                self.logger.error(f"Error initializing Google TTS: {e}")
                self._init_pyttsx3()
        else:
            self.logger.warning(f"Unknown TTS engine: {self.engine_type}, falling back to pyttsx3")
            self._init_pyttsx3()

        self.logger.info(f"Initialized Speaker with {self.engine_type} engine")

    def _init_google_tts(self):
        """Initialize Google Text-to-Speech API client"""
        self.client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(
            language_code=self.config.get("language_code", "en-US"),
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=self.config.get("rate", 1.0),
            pitch=self.config.get("pitch", 0.0),
        )

    def _init_pyttsx3(self):
        """Initialize the pyttsx3 engine"""
        self.engine = pyttsx3.init()
        rate = self.config.get("rate", 150)
        self.engine.setProperty("rate", rate)
        volume = self.config.get("volume", 1.0)
        self.engine.setProperty("volume", volume)
        voice_id = self.config.get("voice_id")
        if voice_id:
            voices = self.engine.getProperty("voices")
            for voice in voices:
                if voice.id == voice_id:
                    self.engine.setProperty("voice", voice.id)
                    break

    def speak(self, text, block=False):
        """Convert text to speech"""
        if not text:
            return

        self.logger.debug(f"Speaking: {text}")

        if self.engine_type == "google_tts":
            if block:
                self._speak_google_tts(text)
            else:
                threading.Thread(
                    target=self._speak_google_tts,
                    args=(text,),
                    daemon=True
                ).start()
        else:
            if block:
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                threading.Thread(
                    target=self._speak_threaded,
                    args=(text,),
                    daemon=True
                ).start()

    def _speak_google_tts(self, text):
        """Use Google Text-to-Speech API to synthesize speech"""
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=self.voice,
            audio_config=self.audio_config,
        )
        file_path = "output.mp3"
        with open(file_path, "wb") as out:
            out.write(response.audio_content)
        self.logger.info("Audio content written to file 'output.mp3'")

        # Play the audio
        os.system(f"mpg123 {file_path}")

        # Clean up the file
        os.remove(file_path)

    def _speak_threaded(self, text):
        """Speak text in a separate thread (pyttsx3)"""
        self.engine.say(text)
        self.engine.runAndWait()
