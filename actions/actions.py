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
