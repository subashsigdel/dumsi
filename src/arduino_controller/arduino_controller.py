"""
Arduino controller module for Dumsi robot
Handles communication with Arduino for servo control
"""

import serial
import time
import logging
import threading
import queue

class ArduinoController:
    """Controls the Arduino-based servos for the robot's face and neck movements"""

    def __init__(self, config):
        """
        Initialize the Arduino controller

        Args:
            config (dict): Configuration dictionary containing Arduino settings
        """
        self.logger = logging.getLogger("dumsi.arduino_controller")

        # Get configuration
        arduino_config = config.get("arduino", {})
        self.port = arduino_config.get("port", "/dev/ttyACM0")
        self.baud_rate = arduino_config.get("baud_rate", 9600)

        self.serial = None
        self.connected = False

        # For talking animation
        self.is_talking = False
        self.command_queue = queue.Queue()

        # Try to connect to Arduino
        self._connect()

        # Start command processing thread
        self.running = True
        self.process_thread = threading.Thread(target=self._process_commands)
        self.process_thread.daemon = True
        self.process_thread.start()

    def _connect(self):
        """Establish connection with the Arduino"""
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=1)
            # Wait for Arduino to reset after connection
            time.sleep(2)
            self.connected = True
            self.logger.info(f"Connected to Arduino on {self.port}")
        except Exception as e:
            self.connected = False
            self.logger.error(f"Failed to connect to Arduino: {e}")

    def _process_commands(self):
        """Process commands from the queue and send to Arduino"""
        while self.running:
            try:
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    self._send_command(command)
                    self.command_queue.task_done()
                else:
                    time.sleep(0.01)  # Sleep to prevent CPU hogging
            except Exception as e:
                self.logger.error(f"Error processing commands: {e}")

    def _send_command(self, command):
        """Send a command to the Arduino"""
        if not self.connected:
            self.logger.warning("Cannot send command - not connected to Arduino")
            return False

        try:
            # Add newline to command
            command_bytes = (command + '\n').encode('utf-8')
            self.serial.write(command_bytes)

            # Read response (optional)
            response = self.serial.readline().decode('utf-8').strip()
            if response:
                self.logger.debug(f"Arduino response: {response}")

            return True
        except Exception as e:
            self.logger.error(f"Error sending command to Arduino: {e}")
            self.connected = False
            return False

    def queue_command(self, command):
        """Add a command to the queue"""
        self.command_queue.put(command)

    def move_eye_vertical(self, angle):
        """
        Move the eye vertically

        Args:
            angle (int): Angle between 50-90 degrees
        """
        self.queue_command(f"EYE_V {angle}")

    def move_eye_horizontal(self, angle):
        """
        Move the eye horizontally

        Args:
            angle (int): Angle between 0-180 degrees
        """
        self.queue_command(f"EYE_H {angle}")

    def move_jaw(self, angle):
        """
        Move the jaw

        Args:
            angle (int): Angle between 90-160 degrees
        """
        self.queue_command(f"JAW {angle}")

    def move_neck(self, angle):
        """
        Move the neck

        Args:
            angle (int): Angle between 0-180 degrees
        """
        self.queue_command(f"NECK {angle}")

    def start_talking(self):
        """Start the talking animation"""
        if not self.is_talking:
            self.is_talking = True
            self.queue_command("TALK 1")

    def stop_talking(self):
        """Stop the talking animation"""
        if self.is_talking:
            self.is_talking = False
            self.queue_command("TALK 0")

    def reset_position(self):
        """Reset all servos to default positions"""
        self.move_eye_vertical(90)  # Center
        self.move_eye_horizontal(90)  # Center
        self.move_jaw(90)  # Closed
        self.move_neck(90)  # Center
        self.logger.info("Reset robot to default position")

    def close(self):
        """Clean up resources"""
        self.running = False
        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join(timeout=1.0)

        if self.connected and self.serial:
            self.serial.close()
            self.logger.info("Disconnected from Arduino")