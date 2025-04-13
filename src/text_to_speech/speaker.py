"""
Speaker module for Dumsi
"""

import logging
import threading
import os
import subprocess
import pyttsx3

try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False


class Speaker:
    """Handles text-to-speech functionality"""

    def __init__(self, config):
        """Initialize the speaker with the given configuration"""
        self.logger = logging.getLogger("dumsi.speaker")
        self.config = config
        self.engine_type = config.get("tts_engine", "pyttsx3")

        if self.engine_type == "google_tts":
            if not GOOGLE_TTS_AVAILABLE:
                self.logger.warning("Google TTS not available, falling back to pyttsx3")
                self._init_pyttsx3()
            else:
                try:
                    self._init_google_tts()
                except Exception as e:
                    self.logger.error(f"Error initializing Google TTS: {e}")
                    self._init_pyttsx3()
        else:
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
        self.engine_type = "pyttsx3"
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

    def play_sound(self, sound_file):
        """Play a sound file"""
        if os.path.exists(sound_file):
            subprocess.run(["mpg123", sound_file])
        else:
            self.logger.warning(f"Sound file not found at {sound_file}")