"""
Natural language processing module for Dumsi
"""

import logging
import re
import spacy
from collections import defaultdict
import sys

import logging
import threading
import os
import subprocess
import speech_recognition as sr
import pyttsx3
from google.cloud import texttospeech
import numpy as np
import json


import os
import pygame

def play_funny_sound():
    """Play the funny sound file if speech is not recognized"""
    funny_audio_path = os.path.expanduser('~/Downloads/funny.mp3')

    if os.path.exists(funny_audio_path):
        # Initialize pygame mixer
        pygame.mixer.init()

        # Load and play the sound
        pygame.mixer.music.load(funny_audio_path)
        pygame.mixer.music.play()

        # Wait until the sound finishes playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    else:
        print(f"Funny sound file not found at {funny_audio_path}")

class LanguageProcessor:
    """Processes natural language input and determines appropriate responses"""

    def __init__(self, config):
        """Initialize the language processor with the given configuration"""
        self.logger = logging.getLogger("dumsi.processor")
        self.config = config

        # Load spaCy model
        try:
            self.nlp = spacy.load(config.get("spacy_model", "en_core_web_sm"))
            self.logger.info("Loaded spaCy model successfully")
        except OSError:
            self.logger.warning("spaCy model not found. Downloading...")
            import subprocess
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        # Define command patterns
        self.command_patterns = {
            "greeting": [r"hello", r"hi", r"hey", r"greetings"],
            "farewell": [r"goodbye", r"bye", r"see you", r"later"],
            "move": [r"move", r"go", r"walk", r"run"],
            "stop": [r"stop", r"halt", r"freeze", r"don't move"],
            "info": [r"what", r"who", r"where", r"when", r"how", r"tell me"],
        }

        # Compile patterns
        self.compiled_patterns = {}
        for intent, patterns in self.command_patterns.items():
            self.compiled_patterns[intent] = [
                re.compile(r"\b" + pattern + r"\b", re.IGNORECASE)
                for pattern in patterns
            ]

    def process(self, text):
        """
        Process the input text and return a response dictionary

        Returns:
            dict: {
                "intent": detected intent,
                "action": action to perform (if any),
                "speech": text to speak in response
            }
        """
        if not text:
            return {"speech": "I didn't hear anything"}

        # Process with spaCy
        doc = self.nlp(text)

        # Determine intent based on patterns
        intent_scores = defaultdict(int)
        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    intent_scores[intent] += 1

        # Get the highest scoring intent
        if intent_scores:
            primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
        else:
            primary_intent = "unknown"

        # Generate response based on intent
        response = self._generate_response(primary_intent, doc, text)

        self.logger.info(f"Intent: {primary_intent}, Response: {response}")
        return response

    def _generate_response(self, intent, doc, original_text):
        """Generate a response based on the detected intent"""
        response = {
            "intent": intent,
            "action": None,
            "speech": None
        }

        if intent == "greeting":
            response["speech"] = "Hello! I am Dumsi, how can I help you today?"

        elif intent == "farewell":
            response["speech"] = "Goodbye! Have a nice day."

        elif intent == "move":
            # Extract direction if present
            direction = "forward"  # default
            for token in doc:
                if token.text.lower() in ["forward", "backward", "left", "right"]:
                    direction = token.text.lower()
                    break

            response["action"] = f"move_{direction}"
            response["speech"] = f"Moving {direction}"

        elif intent == "stop":
            response["action"] = "stop"
            response["speech"] = "Stopping now"

        elif intent == "info":
            # This would be expanded to handle different info requests
            response["speech"] = "I'm Dumsi, a voice-controlled robot. You can ask me to move in different directions or tell me to stop."

        else:
            play_funny_sound()

        return response