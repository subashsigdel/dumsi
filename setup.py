#!/usr/bin/env python3
"""
Dumsi - A voice-controlled robot with Nepali language support
"""

import os
import sys
import yaml
import logging
import time
import argparse
from src.speech_recognition.listener import AudioListener
from src.nlp.processor import LanguageProcessor
from src.nlp.nepali_processor import NepaliProcessor  # New Nepali processor
from src.text_to_speech.speaker import Speaker
from src.robot_control.controller import RobotController
from src.utils.logger import setup_logger
from pygame import mixer


def load_config(config_path="config/settings.yaml"):
    """Load configuration from YAML file"""
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def play_sound(sound_file):
    """Play a sound effect"""
    if os.path.exists(sound_file):
        mixer.init()
        mixer.music.load(sound_file)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.1)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Dumsi - Voice-controlled robot")
    parser.add_argument('--config', default="config/settings.yaml",
                        help="Path to configuration file")
    parser.add_argument('--lang', default=None,
                        help="Language to use (en or ne)")
    args = parser.parse_args()

    # Setup logging
    setup_logger()
    logger = logging.getLogger("dumsi")
    logger.info("Starting Dumsi - Voice-controlled Robot")

    try:
        # Load configuration
        config = load_config(args.config)
        logger.info("Configuration loaded successfully")

        # Determine language
        language = args.lang or config.get("language", "en")

        # Play startup sound if available
        if "theme" in config and "sound_effects" in config["theme"]:
            startup_sound = config["theme"]["sound_effects"].get("startup")
            if startup_sound:
                play_sound(startup_sound)

        # Initialize components
        listener = AudioListener(config["speech_recognition"])

        # Choose appropriate language processor
        if language == "ne":
            processor = NepaliProcessor(config["nlp"])
            logger.info("Using Nepali language processor")
        else:
            processor = LanguageProcessor(config["nlp"])
            logger.info("Using English language processor")

        speaker = Speaker(config["text_to_speech"])
        controller = RobotController(config["robot_control"])

        logger.info("All components initialized successfully")

        # Greet the user in the appropriate language
        if language == "ne":
            speaker.speak("नमस्ते! म दुम्सी हुँ। म तपाईंलाई कसरी मद्दत गर्न सक्छु?", block=True)
            print("दुम्सी तयार छ! केही भन्नुहोस्...")
        else:
            speaker.speak("Hello! I am Dumsi. How can I help you?", block=True)
            print("Dumsi is ready! Say something...")

        # Main interaction loop
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

        # Play shutdown sound if available
        if "theme" in config and "sound_effects" in config["theme"]:
            shutdown_sound = config["theme"]["sound_effects"].get("shutdown")
            if shutdown_sound:
                play_sound(shutdown_sound)

        if language == "ne":
            print("\nनमस्कार!")
        else:
            print("\nGoodbye!")
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()