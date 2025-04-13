"""
Robot integration module for Dumsi
Connects the language processor, Arduino controller, and robot movement
"""

import logging
import threading
import time
from .arduino_controller import ArduinoController


class RobotIntegration:
    """Integrates Arduino control with language processing and speech"""

    def __init__(self, config):
        """
        Initialize the robot integration

        Args:
            config (dict): Configuration for the robot
        """
        self.logger = logging.getLogger("dumsi.robot_integration")
        self.config = config

        # Extract Arduino config
        arduino_config = config.get("arduino", {})
        self.port = arduino_config.get("port", "/dev/ttyACM0")
        self.baud_rate = arduino_config.get("baud_rate", 9600)

        # Initialize Arduino controller
        try:
            self.arduino = ArduinoController(
                port=self.port,
                baud_rate=self.baud_rate
            )
            self.logger.info("Initialized Arduino controller")
        except Exception as e:
            self.logger.error(f"Failed to initialize Arduino controller: {e}")
            self.arduino = None

        # Initialize to default positions
        self.reset_position()

    def reset_position(self):
        """Reset all servos to default positions"""
        if self.arduino:
            self.arduino.move_eye_vertical(90)  # Center
            self.arduino.move_eye_horizontal(90)  # Center
            self.arduino.move_jaw(90)  # Closed
            self.arduino.move_neck(90)  # Center
            self.logger.info("Reset robot to default position")

    def handle_speech_start(self):
        """Called when the robot starts speaking"""
        if self.arduino:
            self.arduino.start_talking()

    def handle_speech_end(self):
        """Called when the robot stops speaking"""
        if self.arduino:
            self.arduino.stop_talking()

    def handle_command(self, command, params=None):
        """
        Handle a command from the language processor

        Args:
            command (str): The command to execute
            params (dict): Optional parameters for the command
        """
        if not self.arduino:
            self.logger.warning("Cannot execute command - Arduino not initialized")
            return

        self.logger.info(f"Handling command: {command} with params: {params}")

        if command == "look_up":
            self.arduino.move_eye_vertical(50)  # Look up
        elif command == "look_down":
            self.arduino.move_eye_vertical(90)  # Look down/center
        elif command == "look_left":
            self.arduino.move_eye_horizontal(0)  # Look left
        elif command == "look_right":
            self.arduino.move_eye_horizontal(180)  # Look right
        elif command == "look_center":
            self.arduino.move_eye_horizontal(90)  # Look center
        elif command == "turn_head_left":
            self.arduino.move_neck(0)  # Turn head left
        elif command == "turn_head_right":
            self.arduino.move_neck(180)  # Turn head right
        elif command == "center_head":
            self.arduino.move_neck(90)  # Center head
        elif command == "open_mouth":
            self.arduino.move_jaw(160)  # Open mouth
        elif command == "close_mouth":
            self.arduino.move_jaw(90)  # Close mouth
        elif command == "reset":
            self.reset_position()
        else:
            self.logger.warning(f"Unknown command: {command}")

    def close(self):
        """Clean up resources"""
        if self.arduino:
            self.reset_position()
            time.sleep(0.5)  # Give time for the reset to complete
            self.arduino.close()
            self.logger.info("Closed Arduino controller")