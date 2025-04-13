"""
Language processor module for Dumsi
"""

import logging
import re
import random


class LanguageProcessor:
    """Processes natural language commands and converts them to robot actions"""

    def __init__(self, config):
        """Initialize the language processor with the given configuration"""
        self.logger = logging.getLogger("dumsi.processor")
        self.config = config

        # Basic responses for chitchat
        self.greetings = [
            "Hello there!",
            "Hi, how can I help you?",
            "Hello, I'm Dumsi. Nice to meet you!"
        ]
        self.farewells = [
            "Goodbye!",
            "See you later!",
            "Bye for now!"
        ]
        self.acknowledgments = [
            "I understood that.",
            "Got it.",
            "I'll handle that for you.",
            "Processing your request."
        ]
        self.confusion = [
            "I'm not sure I understood that.",
            "Could you please repeat?",
            "I didn't catch that. Can you say it differently?"
        ]

    def process(self, text):
        """Process the input text and return appropriate responses or actions"""
        text = text.lower().strip()
        self.logger.debug(f"Processing text: {text}")

        # Prepare response structure
        response = {"speech": None, "action": None}

        # Check for greeting patterns
        if self._is_greeting(text):
            response["speech"] = random.choice(self.greetings)
            response["action"] = {"type": "animate", "movement": "greet"}
            return response

        # Check for farewell patterns
        if self._is_farewell(text):
            response["speech"] = random.choice(self.farewells)
            return response

        # Check for movement commands
        movement_action = self._check_movement_commands(text)
        if movement_action:
            response["action"] = movement_action
            response["speech"] = random.choice(self.acknowledgments)
            return response

        # Check for simple queries
        query_response = self._handle_queries(text)
        if query_response:
            response["speech"] = query_response
            return response

        # Default response for unrecognized input
        response["speech"] = random.choice(self.confusion)
        return response

    def _is_greeting(self, text):
        """Check if the text contains a greeting"""
        greeting_patterns = ["hello", "hi", "hey", "greetings", "good morning",
                            "good afternoon", "good evening", "howdy"]
        return any(pattern in text for pattern in greeting_patterns)

    def _is_farewell(self, text):
        """Check if the text contains a farewell"""
        farewell_patterns = ["bye", "goodbye", "see you", "farewell", "good night",
                            "later", "have a good day"]
        return any(pattern in text for pattern in farewell_patterns)

    def _check_movement_commands(self, text):
        """Check for robot movement commands in the text"""
        # Check for eye movement commands
        if re.search(r"look (up|down|left|right|forward|ahead|straight)", text):
            if "up" in text:
                return {"type": "eye_vertical", "value": 50}  # Look up
            elif "down" in text:
                return {"type": "eye_vertical", "value": 90}  # Look down
            elif "left" in text:
                return {"type": "eye_horizontal", "value": 0}  # Look left
            elif "right" in text:
                return {"type": "eye_horizontal", "value": 180}  # Look right
            else:  # forward, ahead, straight
                return {"type": "reset_eyes", "value": None}  # Reset eye position

        # Check for neck movement commands
        if re.search(r"turn (left|right|center|middle|ahead|straight)", text):
            if "left" in text:
                return {"type": "neck", "value": 45}  # Turn neck left
            elif "right" in text:
                return {"type": "neck", "value": 135}  # Turn neck right
            else:  # center, middle, ahead, straight
                return {"type": "neck", "value": 90}  # Center neck

        # Check for jaw movement
        if re.search(r"(open|close) (your |the )?mouth", text):
            if "open" in text:
                return {"type": "jaw", "value": 160}  # Open jaw
            else:  # close
                return {"type": "jaw", "value": 90}  # Close jaw

        # Check for talk animation
        if re.search(r"(start|stop|begin|end) (talking|speaking)", text):
            if "start" in text or "begin" in text:
                return {"type": "talk", "value": 1}  # Start talking animation
            else:  # stop, end
                return {"type": "talk", "value": 0}  # Stop talking animation

        return None

    def _handle_queries(self, text):
        """Handle simple queries"""
        if "what is your name" in text or "who are you" in text:
            return "I'm Dumsi, your robot assistant. How can I help you today?"

        if "what can you do" in text or "help" in text:
            return "I can listen to your commands, talk to you, and move my head and eyes. Try saying 'look left' or 'turn right'."

        if "how are you" in text:
            return "I'm functioning properly, thank you for asking!"

        return None