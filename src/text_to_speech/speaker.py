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
    """Provides voice output using TTS (Text-to-Speech)"""

    def __init__(self, config):
        """Set up the speaker with the provided configuration"""
        self.logger = logging.getLogger("dumsi.speaker")
        self.config = config
        self.engine_type = config.get("tts_engine", "pyttsx3")

        if self.engine_type == "google_tts":
            if not GOOGLE_TTS_AVAILABLE:
                self.logger.warning("Google TTS not found — switching to pyttsx3.")
                self._init_pyttsx3()
            else:
                try:
                    self._init_google_tts()
                except Exception as e:
                    self.logger.error(f"Couldn't initialize Google TTS: {e}. Falling back to pyttsx3.")
                    self._init_pyttsx3()
        else:
            self._init_pyttsx3()

        self.logger.info(f"Speaker is ready using the '{self.engine_type}' engine.")

    def _init_google_tts(self):
        """Set up Google Cloud Text-to-Speech"""
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
        """Set up pyttsx3 as the speech engine"""
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
        """Speak the given text using the configured engine"""
        if not text:
            return

        self.logger.debug(f"Speaking: '{text}'")

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
        """Generate speech using Google Cloud TTS"""
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=self.voice,
            audio_config=self.audio_config,
        )
        file_path = "output.mp3"
        with open(file_path, "wb") as out:
            out.write(response.audio_content)
        self.logger.info("Google TTS audio saved to 'output.mp3'.")

        # Play the audio
        os.system(f"mpg123 {file_path}")

        # Clean up
        os.remove(file_path)

    def _speak_threaded(self, text):
        """Helper for speaking text asynchronously using pyttsx3"""
        self.engine.say(text)
        self.engine.runAndWait()

    def play_sound(self, sound_file):
        """Play a pre-recorded sound file"""
        if os.path.exists(sound_file):
            subprocess.run(["mpg123", sound_file])
        else:
            self.logger.warning(f"Couldn't find the sound file at: {sound_file}")
