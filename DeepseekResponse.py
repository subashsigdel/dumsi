import requests
import json
from dotenv import load_dotenv
import os

###############load API key#############
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
####################done#################

def Response(question):
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
          f"content": 'give answer in one or two sentences in Romanized English of nepali'f"{question}?"
        }
      ],
      
    })
  )

  # Print response
  if response.status_code == 200:
      result = response.json()
      message = result['choices'][0]['message']['content']
      print(message)
      return message
  else:
      return response.status_code, response.text
