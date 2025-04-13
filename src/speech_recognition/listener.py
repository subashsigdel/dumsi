"""
Speech recognition listener module for Dumsi
"""

import os
import logging
import threading
import queue
import json
import numpy as np
import speech_recognition as sr

# Import models based on availability
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from vosk import Model, KaldiRecognizer
    import pyaudio
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False


class SpeechListener:
    """Listens for speech using either Whisper or VOSK models"""

    def __init__(self, config, language_processor, speaker=None):
        """Initialize the speech listener with the given configuration"""
        self.logger = logging.getLogger("dumsi.listener")
        self.config = config
        self.language_processor = language_processor
        self.speaker = speaker
        self.listening = False
        self.audio_queue = queue.Queue()

        # Set speech recognition model
        self.model_type = config.get("speech_model", "whisper")
        if self.model_type not in ["whisper", "vosk"]:
            self.logger.warning(f"Unknown model type: {self.model_type}. Defaulting to whisper.")
            self.model_type = "whisper"

        # Initialize the selected model
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the selected speech recognition model"""
        if self.model_type == "whisper":
            if not WHISPER_AVAILABLE:
                self.logger.error("Whisper is not available. Install with 'pip install openai-whisper'")
                raise ImportError("Whisper is required but not installed")

            model_size = self.config.get("whisper_model_size", "base")
            self.logger.info(f"Loading Whisper model: {model_size}")
            self.model = whisper.load_model(model_size)
            self.recognizer = sr.Recognizer()

        elif self.model_type == "vosk":
            if not VOSK_AVAILABLE:
                self.logger.error("VOSK is not available. Install with 'pip install vosk'")
                raise ImportError("VOSK is required but not installed")

            model_path = self.config.get("vosk_model_path", "models/vosk-model-small-en-us-0.15")
            if not os.path.exists(model_path):
                self.logger.error(f"VOSK model not found at {model_path}")
                raise FileNotFoundError(f"VOSK model not found at {model_path}")

            self.logger.info(f"Loading VOSK model from: {model_path}")
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.audio = pyaudio.PyAudio()

    def start_listening(self):
        """Start listening for speech in a separate thread"""
        if self.listening:
            return

        self.listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.logger.info("Started speech listener")

        # Announce that the system is ready to listen
        if self.speaker:
            self.speaker.speak("I am ready. Here is my listener.")

    def stop_listening(self):
        """Stop the speech listener"""
        self.listening = False
        if hasattr(self, 'listen_thread') and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        self.logger.info("Stopped speech listener")

    def _listen_loop(self):
        """Main listening loop that runs in a separate thread"""
        if self.model_type == "whisper":
            self._listen_with_whisper()
        else:  # VOSK
            self._listen_with_vosk()

    def _listen_with_whisper(self):
        """Listen for speech using Whisper model and sr"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            self.logger.info("Whisper listener is ready")

            while self.listening:
                try:
                    self.logger.debug("Listening for audio...")
                    audio = self.recognizer.listen(source, timeout=5.0, phrase_time_limit=10.0)

                    # Convert audio data to numpy array for Whisper
                    audio_data = np.frombuffer(audio.get_raw_data(), np.int16).astype(np.float32) / 32768.0

                    # Process with Whisper
                    result = self.model.transcribe(audio_data)
                    text = result["text"].strip()

                    if text:
                        self.logger.info(f"Recognized: {text}")
                        self._process_text(text)
                    else:
                        self.logger.debug("No speech detected")

                except sr.WaitTimeoutError:
                    self.logger.debug("Listening timeout, continuing...")
                except Exception as e:
                    self.logger.error(f"Error in Whisper listening: {e}")

    def _listen_with_vosk(self):
        """Listen for speech using VOSK model"""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000
        )

        self.logger.info("VOSK listener is ready")
        stream.start_stream()

        try:
            while self.listening:
                data = stream.read(4000, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()

                    if text:
                        self.logger.info(f"Recognized: {text}")
                        self._process_text(text)
        except Exception as e:
            self.logger.error(f"Error in VOSK listening: {e}")
        finally:
            stream.stop_stream()
            stream.close()

    def _process_text(self, text):
        """Process recognized text with the language processor"""
        if not text:
            return

        response = self.language_processor.process(text)

        # Handle the response according to your application's needs
        if response.get("speech") and self.speaker:
            self.logger.info(f"Response: {response['speech']}")
            self.speaker.speak(response['speech'])

        if response.get("action"):
            self.logger.info(f"Action: {response['action']}")
            # Here you would trigger the action in your robot controller