import os
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from groq import Groq
import speech_recognition as sr

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversation_history = [
    {
        "role": "system", 
        "content": "You are a helpful AI voice assistant. Keep answers short, natural, and conversational."
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listen', methods=['POST'])
def listen_and_process():
    global conversation_history
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1

    user_text = ""
    error_message = ""

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        user_text = recognizer.recognize_google(audio)
    except sr.WaitTimeoutError:
        error_message = "Didn't hear anything. Try again."
    except sr.UnknownValueError:
        error_message = "Couldn't understand the audio."
    except Exception as e:
        error_message = f"Microphone error: {str(e)}"

    if error_message:
        return jsonify({"error": error_message})

    exit_words = ["exit", "quit", "stop", "bye", "goodbye"]
    is_exit = any(word in user_text.lower() for word in exit_words)

    if is_exit:
        ai_response = "Goodbye! 👋"
        conversation_history.append({"role": "user", "content": user_text})
        conversation_history.append({"role": "assistant", "content": ai_response})
        return jsonify({"user": user_text, "ai": ai_response, "stop_loop": True})

    conversation_history.append({"role": "user", "content": user_text})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation_history
        )
        ai_response = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": ai_response})
    except Exception as e:
        ai_response = f"AI Error: {str(e)}"

    return jsonify({"user": user_text, "ai": ai_response})

@app.route('/clear', methods=['POST'])
def clear_chat():
    global conversation_history
    conversation_history = [
        {
            "role": "system", 
            "content": "You are a helpful AI voice assistant. Keep answers short, natural, and conversational."
        }
    ]
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    app.run(debug=True)