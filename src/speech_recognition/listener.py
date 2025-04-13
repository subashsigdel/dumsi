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
import time

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

    def __init__(self, config, language_processor, speaker=None, controller=None):
        """Initialize the speech listener with the given configuration"""
        self.logger = logging.getLogger("dumsi.listener")
        self.config = config
        self.language_processor = language_processor
        self.speaker = speaker
        self.controller = controller
        self.listening = False
        self.audio_queue = queue.Queue()
        self.last_recognition_time = 0
        self.idle_timeout = config.get("idle_timeout", 60)  # seconds of inactivity before idle behaviors
        self.idle_thread = None
        self.is_idle = False

        # Set speech recognition model
        self.model_type = config.get("speech_model", "whisper")
        if self.model_type not in ["whisper", "vosk"]:
            self.logger.warning(f"Unknown model type: {self.model_type}. Defaulting to whisper.")
            self.model_type = "whisper"

        # Recognition settings
        self.energy_threshold = config.get("energy_threshold", 300)
        self.pause_threshold = config.get("pause_threshold", 0.8)
        self.dynamic_energy_threshold = config.get("dynamic_energy_threshold", True)

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

            # Configure recognizer settings
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.pause_threshold = self.pause_threshold
            self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold

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

        # Start idle behavior monitoring
        self.idle_thread = threading.Thread(target=self._idle_monitor)
        self.idle_thread.daemon = True
        self.idle_thread.start()

        self.logger.info("Started speech listener")

        # Announce that the system is ready to listen
        if self.speaker:
            self.speaker.speak("I am ready. Here is my listener.")

    def stop_listening(self):
        """Stop the speech listener"""
        self.listening = False
        if hasattr(self, 'listen_thread') and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)

        if hasattr(self, 'idle_thread') and self.idle_thread.is_alive():
            self.idle_thread.join(timeout=1.0)

        self.logger.info("Stopped speech listener")

    def _idle_monitor(self):
        """Monitor for idle state and trigger random movements"""
        while self.listening:
            time_since_last_recognition = time.time() - self.last_recognition_time

            if time_since_last_recognition > self.idle_timeout and not self.is_idle:
                self.is_idle = True
                self.logger.info("Entering idle state")
                self._start_idle_behaviors()

            elif time_since_last_recognition <= self.idle_timeout and self.is_idle:
                self.is_idle = False
                self.logger.info("Exiting idle state")
                self._stop_idle_behaviors()

            time.sleep(5)  # Check every 5 seconds

    def _start_idle_behaviors(self):
        """Start random idle behaviors"""
        if not self.controller:
            return

        # Perform a random idle movement
        self._perform_random_idle_movement()

    def _stop_idle_behaviors(self):
        """Stop idle behaviors"""
        if not self.controller:
            return

        # Reset to default position
        self.controller.move_eye_vertical(70)
        self.controller.move_eye_horizontal(90)
        self.controller.move_neck(90)
        self.controller.stop_talking()

    def _perform_random_idle_movement(self):
        """Perform a random idle movement"""
        if not self.controller or not self.is_idle:
            return

        # Select a random movement
        movements = [
            lambda: self.controller.move_eye_horizontal(np.random.randint(30, 150)),
            lambda: self.controller.move_eye_vertical(np.random.randint(60, 90)),
            lambda: self.controller.move_neck(np.random.randint(45, 135)),
            lambda: self.controller.move_jaw(np.random.randint(90, 120)),
        ]

        # Execute the random movement
        movement = np.random.choice(movements)
        movement()

        # Schedule the next movement if still idle
        if self.is_idle and self.listening:
            delay = np.random.randint(3, 10)  # Random delay between 3-10 seconds
            threading.Timer(delay, self._perform_random_idle_movement).start()

    def _listen_loop(self):
        """Main listening loop that runs in a separate thread"""
        if self.model_type == "whisper":
            self._listen_with_whisper()
        else:  # VOSK
            self._listen_with_vosk()

    def _listen_with_whisper(self):
        """Listen for speech using Whisper model and sr"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            self.logger.info("Whisper listener is ready")
            self.last_recognition_time = time.time()  # Initialize the last recognition time

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
                        self.last_recognition_time = time.time()
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
        self.last_recognition_time = time.time()  # Initialize the last recognition time

        try:
            while self.listening:
                data = stream.read(4000, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()

                    if text:
                        self.last_recognition_time = time.time()
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

        # If there's a robot controller and the response includes an action
        if self.controller and response.get("action"):
            action = response["action"]
            action_type = action.get("type")

            # Start jaw animation for speaking
            if self.speaker and response.get("speech"):
                self.controller.start_talking()

            # Handle different action types
            if action_type == "eye_vertical":
                self.controller.move_eye_vertical(action["value"])
            elif action_type == "eye_horizontal":
                self.controller.move_eye_horizontal(action["value"])
            elif action_type == "jaw":
                self.controller.move_jaw(action["value"])
            elif action_type == "neck":
                self.controller.move_neck(action["value"])
            elif action_type == "talk":
                if action["value"] == 1:
                    self.controller.start_talking()
                else:
                    self.controller.stop_talking()
            elif action_type == "reset_eyes":
                self.controller.move_eye_vertical(70)
                self.controller.move_eye_horizontal(90)
            elif action_type == "animate" and action.get("movement") == "greet":
                # Greet animation sequence
                self.controller.move_neck(45)  # Look left
                time.sleep(0.5)
                self.controller.move_neck(135)  # Look right
                time.sleep(0.5)
                self.controller.move_neck(90)  # Center

        # Handle speech response
        if self.speaker and response.get("speech"):
            self.speaker.speak(response["speech"])

            # Stop jaw animation after speaking
            if self.controller:
                time.sleep(0.5)  # Give a brief pause
                self.controller.stop_talking()