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