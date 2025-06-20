
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import wikipedia

class ActionWikipediaFallback(Action):

    def name(self) -> Text:
        return "action_wikipedia_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_message = tracker.latest_message.get('text')

        try:
            # Search Wikipedia and get a summary (first 2 sentences)
            summary = wikipedia.summary(user_message, sentences=2)
            dispatcher.utter_message(text=summary)
        except wikipedia.DisambiguationError as e:
            # If multiple topics found, pick the first option
            option = e.options[0]
            try:
                summary = wikipedia.summary(option, sentences=2)
                dispatcher.utter_message(text=summary)
            except Exception:
                dispatcher.utter_message(text="माफ गर्नुहोस्, त्यो विषयमा मैले जानकारी पाइनँ।")
        except Exception:
            dispatcher.utter_message(text="माफ गर्नुहोस्, त्यो विषयमा मैले जानकारी पाइनँ।")

        return []

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import datetime
import json
import random

class ActionTellTime(Action):
    def name(self):
        return "action_tell_time"
    def run(self, dispatcher, tracker, domain):
        current_time = datetime.datetime.now().strftime("%H:%M")
        responses = [
            f"हम्म, अहिले {current_time} बज्यो।",
            f"लौ न, {current_time} भयो हजुर।",
            f"अहिले त {current_time} हो, के गर्ने सोच?"
        ]
        dispatcher.utter_message(text=random.choice(responses))
        return []

class ActionSing(Action):
    def name(self):
        return "action_sing"
    def run(self, dispatcher, tracker, domain):
        with open("data/songs.json", "r", encoding="utf-8") as f:
            songs = json.load(f)
        song = random.choice(songs)
        responses = [
            f"लौ न, यो गीत गाउँछु: {song['title']}!\n{song['lyrics']}",
            f"हजुर, यो सुन: {song['title']}!\n{song['lyrics']}",
            f"हम्म, लौ यो गीत त: {song['title']}!\n{song['lyrics']}"
        ]
        dispatcher.utter_message(text=random.choice(responses))
        return []

