"""
Main module for Dumsi
"""

import argparse
import json
import logging
import os
import time

from src.nlp.processor import LanguageProcessor
from src.speech_recognition.listener import SpeechListener
from src.text_to_speech.speaker import Speaker


def setup_logging():
    """Configure logging for the application"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("dumsi.log")
        ]
    )
    return logging.getLogger("dumsi.main")


def load_config(config_path):
    """Load configuration from JSON file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        return json.load(f)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Dumsi - Voice-controlled robot")
    parser.add_argument("--config", default="config/config.json", help="Path to configuration file")
    parser.add_argument("--model", choices=["whisper", "vosk"], default=None,
                        help="Speech recognition model to use (overrides config)")
    parser.add_argument("--tts", choices=["pyttsx3", "google_tts"], default=None,
                        help="Text-to-speech engine to use (overrides config)")
    args = parser.parse_args()

    # Set up logging
    logger = setup_logging()
    logger.info("Starting Dumsi")

    # Load configuration
    try:
        config = load_config(args.config)
        logger.info(f"Loaded configuration from {args.config}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return 1

    # Override model selection if specified in command line
    if args.model:
        config["speech_model"] = args.model
        logger.info(f"Using speech model from command line: {args.model}")

    # Override TTS engine if specified in command line
    if args.tts:
        config["tts_engine"] = args.tts
        logger.info(f"Using TTS engine from command line: {args.tts}")

    # Initialize language processor
    try:
        language_processor = LanguageProcessor(config)
        logger.info("Initialized language processor")
    except Exception as e:
        logger.error(f"Failed to initialize language processor: {e}")
        return 1

    # Initialize speaker
    try:
        speaker = Speaker(config)
        logger.info("Initialized speaker")
    except Exception as e:
        logger.error(f"Failed to initialize speaker: {e}")
        return 1

    # Initialize speech listener
    try:
        speech_listener = SpeechListener(config, language_processor, speaker)
        logger.info("Initialized speech listener")
    except Exception as e:
        logger.error(f"Failed to initialize speech listener: {e}")
        return 1

    # Start listening
    try:
        speech_listener.start_listening()
        logger.info("Dumsi is now listening for commands")

        # Keep the main thread running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down")
    finally:
        # Clean up
        speech_listener.stop_listening()
        logger.info("Dumsi has been shut down")

    return 0


if __name__ == "__main__":
    exit(main())