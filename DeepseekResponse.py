import requests
import json
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

def Response(question):
    prompt = (
        f"Kripaya, yo prasna ko uttar 1-2 sentence ma, sajilo ra samjhana milne, "
        f"tatha sambidhanik Romanized Nepali ma dinu hos. "
        f"Shishtachar ra sambodhan ko khyal garnuhos, slang ya colloquial shabda prayoog nagarnuhos. "
        f"Question: {question}"
    )

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
                    "role": "system",
                    "content": (
        f"you are not a chatbot You are a Nepali person who lives in Nepal and knows the country and its culture very well "
        f"Your answers should feel natural, easy to understand, and respectful — just like how an educated Nepali would talk to another person in a real conversation "
        f"Speak only in Romanized Nepali (do not use Devanagari or Hindi). "
        f"Do not use slang, but make sure your tone feels real and human — not robotic or overly formal."
        f"Question: {question}"
    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        })
    )

    if response.status_code == 200:
        result = response.json()
        message = result['choices'][0]['message']['content'].strip()
        print(message)
        return message
    else:
        print("Error:", response.status_code, response.text)
        return response.status_code, response.text

# Example usage
Response("tmi dance garna sakxau?")
