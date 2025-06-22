
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

class ActionDeepSeekFallback(Action):

    def name(self) -> Text:
        return "action_deepseek_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_input = tracker.latest_message.get('text')

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": "deepseek/deepseek-chat-v3-0324:free",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"give answer in one or two sentences in Romanized English of nepali: {user_input}?"
                        }
                    ],
                })
            )

            if response.status_code == 200:
                message = response.json()['choices'][0]['message']['content']
                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text="Sorry, I couldn't understand and fetch an answer.")

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {str(e)}")

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

