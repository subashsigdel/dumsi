"""
Robot Controller module for Dumsi
"""

import logging
import serial
import time
import threading


class RobotController:
    """Controls the physical robot movements via Arduino"""

    def __init__(self, config):
        """Initialize the robot controller with the given configuration"""
        self.logger = logging.getLogger("dumsi.controller")
        self.config = config
        self.port = config.get("arduino_port", "/dev/ttyACM0")  # Default for Linux
        self.baud_rate = config.get("arduino_baud_rate", 9600)
        self.serial = None
        self.connected = False
        self.lock = threading.Lock()
        self.keep_alive = True

        # Connect to the Arduino
        self._connect()

        # Start keep-alive thread
        self.keep_alive_thread = threading.Thread(target=self._keep_alive_loop)
        self.keep_alive_thread.daemon = True
        self.keep_alive_thread.start()

    def _connect(self):
        """Establish a connection to the Arduino"""
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=1)
            # Give the Arduino time to reset after connection
            time.sleep(2)
            self.connected = True
            self.logger.info(f"Connected to Arduino on {self.port}")

            # Read initial message from Arduino
            response = self._read_response()
            if response and "initialized" in response.lower():
                self.logger.info("Arduino initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to connect to Arduino: {e}")
            self.connected = False

    def _read_response(self, timeout=1.0):
        """Read a response from the Arduino"""
        if not self.connected or not self.serial:
            return None

        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if self.serial.in_waiting > 0:
                try:
                    response = self.serial.readline().decode('utf-8').strip()
                    self.logger.debug(f"Arduino response: {response}")
                    return response
                except Exception as e:
                    self.logger.error(f"Error reading from Arduino: {e}")
                    return None
            time.sleep(0.1)
        return None

    def _keep_alive_loop(self):
        """Send periodic commands to keep the connection alive"""
        while self.keep_alive:
            if self.connected:
                try:
                    # Send a simple command to keep the connection active
                    # Using a non-intrusive command that won't affect robot behavior
                    with self.lock:
                        # Just read responses without sending commands
                        while self.serial.in_waiting > 0:
                            self._read_response(timeout=0.1)
                except Exception as e:
                    self.logger.error(f"Keep-alive error: {e}")
                    self.connected = False
                    self._connect()  # Try to reconnect

            # Sleep for a bit before next keep-alive
            time.sleep(5)

    def send_command(self, command):
        """Send a command to the Arduino"""
        if not self.connected or not self.serial:
            self.logger.error("Cannot send command: Not connected to Arduino")
            return False

        try:
            with self.lock:
                self.logger.debug(f"Sending command to Arduino: {command}")
                self.serial.write(f"{command}\n".encode('utf-8'))
                response = self._read_response()
                return response
        except Exception as e:
            self.logger.error(f"Error sending command to Arduino: {e}")
            self.connected = False
            self._connect()  # Try to reconnect
            return False

    def move_eye_vertical(self, angle):
        """Move the vertical eye servo to the specified angle"""
        return self.send_command(f"EYE_V {angle}")

    def move_eye_horizontal(self, angle):
        """Move the horizontal eye servo to the specified angle"""
        return self.send_command(f"EYE_H {angle}")

    def move_jaw(self, angle):
        """Move the jaw servo to the specified angle"""
        return self.send_command(f"JAW {angle}")

    def move_neck(self, angle):
        """Move the neck servo to the specified angle"""
        return self.send_command(f"NECK {angle}")

    def start_talking(self):
        """Start the talking animation"""
        return self.send_command("TALK 1")

    def stop_talking(self):
        """Stop the talking animation"""
        return self.send_command("TALK 0")

    def set_autonomous_mode(self, enabled):
        """Enable or disable autonomous mode"""
        value = 1 if enabled else 0
        return self.send_command(f"AUTO {value}")

    def close(self):
        """Close the connection to the Arduino"""
        self.keep_alive = False
        if hasattr(self, 'keep_alive_thread') and self.keep_alive_thread.is_alive():
            self.keep_alive_thread.join(timeout=1.0)

        if self.serial:
            self.serial.close()
            self.connected = False
            self.logger.info("Disconnected from Arduino")