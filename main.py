#!/usr/bin/env python3
"""
Dumsi - A voice-controlled robot that listens, processes language, and speaks
"""

import os
import sys
import yaml
import logging
from src.speech_recognition.listener import AudioListener
from src.nlp.processor import LanguageProcessor
from src.text_to_speech.speaker import Speaker
from src.robot_control.controller import RobotController
from src.utils.logger import setup_logger


def load_config(config_path="config/settings.yaml"):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def main():
    # Setup logging
    setup_logger()
    logger = logging.getLogger("dumsi")
    logger.info("Starting Dumsi - Voice-controlled Robot")

    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")

        # Initialize components
        listener = AudioListener(config["speech_recognition"])
        processor = LanguageProcessor(config["nlp"])
        speaker = Speaker(config["text_to_speech"])
        controller = RobotController(config["robot_control"])

        logger.info("All components initialized successfully")

        # Main interaction loop
        print("Dumsi is ready! Say something...")
        while True:
            # Listen for audio input
            audio_input = listener.listen()
            if audio_input:
                # Convert speech to text
                text = listener.recognize(audio_input)
                logger.info(f"Recognized: {text}")

                if text:
                    # Process the text
                    response = processor.process(text)

                    # Control robot if necessary
                    if response.get("action"):
                        controller.execute_action(response["action"])

                    # Speak the response
                    if response.get("speech"):
                        speaker.speak(response["speech"])

    except KeyboardInterrupt:
        logger.info("Shutting down Dumsi...")
        print("\nGoodbye!")
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()