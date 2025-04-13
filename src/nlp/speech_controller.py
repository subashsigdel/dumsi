"""
Module for handling speech and jaw synchronization
"""

import threading
import time
import logging


class SpeechController:
    """Controls speech and coordinates jaw movements with speech"""

    def __init__(self, speaker, robot_controller):
        """Initialize with speaker and robot controller instances"""
        self.logger = logging.getLogger("dumsi.speech")
        self.speaker = speaker
        self.robot = robot_controller
        self.is_speaking = False
        self.speech_lock = threading.Lock()

    def speak(self, text):
        """Speak the given text and coordinate jaw movements"""
        if not text:
            return False

        with self.speech_lock:
            # Prevent overlapping speech
            if self.is_speaking:
                self.logger.warning("Already speaking, cannot start new speech")
                return False

            try:
                self.is_speaking = True

                # Start jaw movement before speaking
                if self.robot and self.robot.connected:
                    self.robot.start_talking()
                    # Small delay to ensure jaw starts moving
                    time.sleep(0.1)

                # Speak the text
                if self.speaker:
                    self.speaker.speak(text)

                # Small delay after speech before stopping jaw
                time.sleep(0.3)

                # Stop jaw movement
                if self.robot and self.robot.connected:
                    self.robot.stop_talking()

                return True

            except Exception as e:
                self.logger.error(f"Error during speech: {e}")
                return False

            finally:
                self.is_speaking = False

    def speak_async(self, text):
        """Speak in a separate thread to avoid blocking"""
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()
        return thread