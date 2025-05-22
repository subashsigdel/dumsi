import gradio as gr
import requests
import json
from datetime import datetime
from SST import get_voice_input, speak_response  # Voice functions

LOG_FILE = "feedback_log.jsonl"
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

def talk_to_bot(user_input):
    res = requests.post(RASA_URL, json={"sender": "user", "message": user_input})
    bot_response = res.json()[0]["text"] if res.json() else "मलाई थाहा भएन।"
    speak_response(bot_response)  # Speak bot's response
    return bot_response

def save_feedback(user_input, bot_response, correct, manual_response=""):
    entry = {
        "timestamp": str(datetime.now()),
        "user_query": user_input,
        "bot_response": bot_response,
        "correct": correct,
        "manual_response": manual_response
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return "फीडब्याक सुरक्षित भयो।"

with gr.Blocks() as demo:
    with gr.Row():
        user_input = gr.Textbox(label="📝 प्रश्न लेख्नुहोस्", lines=1)
        mic_button = gr.Button("🎤 भ्वाइसबाट सोध्नुहोस्")

    bot_output = gr.Textbox(label="🤖 पाण्डा भन्छ", interactive=False)
    feedback_text = gr.Textbox(label="✏️ यदि गलत हो भने यहाँ सहि उत्तर लेख्नुहोस्", visible=False)
    status = gr.Textbox(label="📌 स्थिति", interactive=False)

    correct_btn = gr.Button("✅ सही हो")
    wrong_btn = gr.Button("❌ गलत छ")
    submit_btn = gr.Button("📤 अपडेट गर्नुहोस्", visible=False)

    def handle_text_input(user_msg):
        response = talk_to_bot(user_msg)
        return response, gr.update(visible=True), gr.update(visible=True)

    def handle_voice_input():
        voice_input = get_voice_input()
        if voice_input:
            response = talk_to_bot(voice_input)
            return voice_input, response, gr.update(visible=True), gr.update(visible=True)
        else:
            return "", "भ्वाइस बुझ्न सकिएन।", gr.update(visible=False), gr.update(visible=False)

    def mark_correct(user_msg, bot_msg):
        return save_feedback(user_msg, bot_msg, True, "")

    def mark_wrong(user_msg, bot_msg, corrected_text):
        return save_feedback(user_msg, bot_msg, False, corrected_text)

    # Event bindings
    user_input.submit(handle_text_input, inputs=user_input, outputs=[bot_output, feedback_text, submit_btn])
    mic_button.click(handle_voice_input, inputs=[], outputs=[user_input, bot_output, feedback_text, submit_btn])
    correct_btn.click(mark_correct, inputs=[user_input, bot_output], outputs=status)
    submit_btn.click(mark_wrong, inputs=[user_input, bot_output, feedback_text], outputs=status)
