"""
Language processor module for Dumsi
Integrates with Arduino controller for robot control
"""

import logging
import time
import threading
from src.arduino_controller.arduino_controller import ArduinoController


class LanguageProcessor:
    """Processes speech and controls robot actions"""

    def __init__(self, config):
        """Initialize the language processor with the given configuration"""
        self.logger = logging.getLogger("dumsi.processor")
        self.config = config

        # Initialize Arduino controller
        try:
            self.arduino = ArduinoController(config)
            self.logger.info("Initialized Arduino controller")

            # Reset to default position
            self.arduino.reset_position()
        except Exception as e:
            self.logger.error(f"Failed to initialize Arduino controller: {e}")
            self.arduino = None

    def process(self, text):
        """
        Process recognized text and determine appropriate response

        Args:
            text (str): The recognized speech text

        Returns:
            dict: Response containing speech and action
        """
        text = text.lower()
        self.logger.info(f"Processing text: {text}")

        response = {
            "speech": None,
            "action": None
        }

        # Check for robot control commands
        if self.arduino:
            if "look up" in text:
                self.arduino.move_eye_vertical(50)  # Look up
                response["speech"] = "Looking up"
                response["action"] = "look_up"
            elif "look down" in text:
                self.arduino.move_eye_vertical(90)  # Look down/center
                response["speech"] = "Looking down"
                response["action"] = "look_down"
            elif "look left" in text:
                self.arduino.move_eye_horizontal(0)  # Look left
                response["speech"] = "Looking to the left"
                response["action"] = "look_left"
            elif "look right" in text:
                self.arduino.move_eye_horizontal(180)  # Look right
                response["speech"] = "Looking to the right"
                response["action"] = "look_right"
            elif "look center" in text or "look straight" in text:
                self.arduino.move_eye_horizontal(90)  # Look center
                response["speech"] = "Looking straight ahead"
                response["action"] = "look_center"
            elif "turn head left" in text:
                self.arduino.move_neck(0)  # Turn head left
                response["speech"] = "Turning my head to the left"
                response["action"] = "turn_head_left"
            elif "turn head right" in text:
                self.arduino.move_neck(180)  # Turn head right
                response["speech"] = "Turning my head to the right"
                response["action"] = "turn_head_right"
            elif "center head" in text:
                self.arduino.move_neck(90)  # Center head
                response["speech"] = "Centering my head"
                response["action"] = "center_head"
            elif "open mouth" in text:
                self.arduino.move_jaw(160)  # Open mouth
                response["speech"] = "Opening my mouth"
                response["action"] = "open_mouth"
            elif "close mouth" in text:
                self.arduino.move_jaw(90)  # Close mouth
                response["speech"] = "Closing my mouth"
                response["action"] = "close_mouth"
            elif "reset position" in text:
                self.arduino.reset_position()
                response["speech"] = "Resetting to default position"
                response["action"] = "reset"

        # Process other types of queries here
        # ...

        # If no specific command was recognized, provide a default response
        if not response["speech"]:
            response["speech"] = "I heard you, but I'm not sure what to do"

        return response

    def speak(self, text):
        """
        Handle text-to-speech with mouth animation

        Args:
            text (str): The text to speak

        Returns:
            bool: Success status
        """
        if not text:
            return False

        self.logger.info(f"Speaking: {text}")

        # Start mouth animation if Arduino is connected
        if self.arduino:
            self.arduino.start_talking()

        # Here you would call your text-to-speech system
        # For example:
        # self.tts.speak(text)

        # For demonstration, we'll just wait based on text length
        time.sleep(len(text) * 0.08)  # Rough approximation

        # Stop mouth animation
        if self.arduino:
            self.arduino.stop_talking()

        return True

    def close(self):
        """Clean up resources"""
        if hasattr(self, 'arduino') and self.arduino:
            self.arduino.close()
            self.logger.info("Closed Arduino controller")