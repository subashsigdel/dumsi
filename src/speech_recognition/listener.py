import json
import logging
import os

import numpy as np
import speech_recognition as sr
from vosk import Model, KaldiRecognizer


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

        # Initialize the selected recognition engine
        if self.engine == "vosk":
            self._init_vosk()
        elif self.engine == "whisper":
            self.logger.warning("Whisper engine is not fully implemented.")
        else:
            self.logger.warning(f"Unknown engine: {self.engine}, falling back to speechrecognition.")

        self.logger.info(f"Initialized AudioListener with {self.engine} engine")

    def _init_vosk(self):
        """Initialize Vosk model for offline recognition"""
        model_path = self.config.get("vosk_model_path", "models/vosk")
        if not os.path.exists(model_path):
            error_message = f"Vosk model not found at {model_path}. Please download a model."
            self.logger.error(error_message)
            raise FileNotFoundError(error_message)

        self.vosk_model = Model(model_path)
        self.vosk_recognizer = KaldiRecognizer(self.vosk_model, 16000)

    def listen(self, timeout=None, phrase_time_limit=None):
        """Listen for audio input and return the audio data"""
        timeout = timeout or self.config.get("timeout", 5)
        phrase_time_limit = phrase_time_limit or self.config.get("phrase_time_limit", 5)

        self.logger.debug("Listening for audio input...")

        try:
            with sr.Microphone(device_index=self.microphone_index) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
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

            elif self.engine == "whisper":
                # Placeholder for Whisper engine, needs implementation
                self.logger.warning("Whisper engine not implemented yet")
                return ""

            else:
                self.logger.error(f"Unknown speech recognition engine: {self.engine}")
                return ""

        except sr.UnknownValueError:
            self.logger.debug("Could not understand audio")
            return ""
        except sr.RequestError as e:
            self.logger.error(f"Error with speech recognition service: {str(e)}")
            return ""
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {str(e)}")
            return ""
