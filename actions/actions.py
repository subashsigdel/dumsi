
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from dotenv import load_dotenv
import requests
import json
import os
from rasa_sdk.events import SlotSet
import datetime

import random
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
                        "content": (
        f"you are not a chatbot You are a Nepali person who lives in Nepal and knows the country and its culture very well "
        f"Your answers should feel natural, easy to understand, and respectful — just like how an educated Nepali would talk to another person in a real conversation "
        f"Speak only in Nepali script (do not use Hindi). "
        f"Do not use slang, but make sure your tone feels real and human — not robotic or overly formal."
        f"Question: {user_input}"
    )
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

