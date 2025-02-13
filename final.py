import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import time
import google.generativeai as genai
from transformers import pipeline
import pyttsx3

# Configure Google Generative AI
genai.configure(api_key="AIzaSyCRbnEmx-3tgblNCzwFc5EE5CiQ_IBipYk")
model = genai.GenerativeModel("gemini-1.5-flash")

# Load Emotion Detection Model
emotion_model = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions")

# Initialize text-to-speech engine
engine = pyttsx3.init()

def set_voice(persona):
    voices = engine.getProperty('voices')
    if persona == "Shah Rukh Khan":
        engine.setProperty('voice', voices[0].id)  # Male voice
    else:
        engine.setProperty('voice', voices[1].id)  # Female voice

def speak_text(text, persona):
    set_voice(persona)
    engine.say(text)
    engine.runAndWait()

# Function to generate bot response
def bot_response(user_input, emotions, chatbot_persona):
    prompt = f"The user is feeling {emotions}. Respond as {chatbot_persona} in a short and empathetic manner: {user_input}"
    response = model.generate_content(prompt)
    return response.text.strip() if response and response.text else "I'm not sure how to respond."

# Function to detect emotions
def detect_emotions(text):
    emotion_scores = emotion_model(text, top_k=3)
    top_emotions = [(e["label"], e["score"]) for e in emotion_scores]
    emotions = ', '.join([e[0] for e in top_emotions])
    return emotions, top_emotions

def show_reasoning(emotion_details):
    reason_window = ctk.CTkToplevel(app)
    reason_window.title("Emotion Analysis")
    reason_window.geometry("300x200")
    reason_label = ctk.CTkLabel(reason_window, text=f"Top Emotions:\n{emotion_details}", font=("Arial", 12))
    reason_label.pack(padx=10, pady=10)

def display_bot_response(text, persona):
    response_frame = ctk.CTkFrame(conversation_frame, fg_color="#44475a")
    response_frame.pack(fill="x", padx=10, pady=5)
    response_label = ctk.CTkLabel(response_frame, text=text, text_color="white", justify="left")
    response_label.pack(side="left", padx=5, pady=5)
    speak_button = ctk.CTkButton(response_frame, text="🔊 Speak", width=50, command=lambda: speak_text(text, persona), fg_color="#50fa7b")
    speak_button.pack(side="right", padx=5, pady=5)

def start_chat(persona):
    chatbot_persona.set(persona)
    selection_frame.pack_forget()
    chat_frame.pack(fill="both", expand=True)

def go_back():
    chat_frame.pack_forget()
    selection_frame.pack(fill="both", expand=True)

def send_message(event=None):
    user_input = user_entry.get().strip()
    if user_input:
        emotions, top_emotions = detect_emotions(user_input)
        response = bot_response(user_input, emotions, chatbot_persona.get())
        
        display_bot_response(f"You: {user_input}", chatbot_persona.get())
        display_bot_response(f"{chatbot_persona.get()}: {response}", chatbot_persona.get())

        user_entry.delete(0, ctk.END)
        emotion_details = "\n".join([f"- {label}: {score * 100:.2f}%" for label, score in top_emotions])
        reasoning_button.configure(command=lambda: show_reasoning(emotion_details))

# Main window
app = ctk.CTk()
app.title("Chatbot UI")
app.geometry("500x600")
app.configure(fg_color=("#1e1e2e", "#1e1e2e"))

# Selection Frame
selection_frame = ctk.CTkFrame(app, fg_color=("#282a36", "#282a36"))
selection_frame.pack(fill="both", expand=True)

ctk.CTkLabel(selection_frame, text="Who do you want to talk with?", font=("Arial", 18), text_color="white").pack(pady=20)
chatbot_persona = tk.StringVar()

# Load icons
personas = ["Shah Rukh Khan", "Sydney Sweeney"]
icons = ["srk.jpg", "sydney.jpg"]
for i, persona in enumerate(personas):
    img = Image.open(icons[i]).resize((80, 80))
    img = ImageTk.PhotoImage(img)
    btn = ctk.CTkButton(selection_frame, text=persona, image=img, compound="left", command=lambda p=persona: start_chat(p), fg_color="#6272a4")
    btn.image = img
    btn.pack(pady=10, padx=10, ipadx=10, ipady=5)

# Chat Frame
chat_frame = ctk.CTkFrame(app, fg_color=("#282a36", "#282a36"))

header_frame = ctk.CTkFrame(chat_frame, fg_color=("#44475a", "#44475a"))
header_frame.pack(fill="x", pady=5)
back_button = ctk.CTkButton(header_frame, text="← Back", command=go_back, fg_color="#ff5555")
back_button.pack(side="left", padx=5)
header = ctk.CTkLabel(header_frame, textvariable=chatbot_persona, font=("Arial", 18, "bold"), text_color="white")
header.pack(side="left", padx=10)
reasoning_button = ctk.CTkButton(header_frame, text="Reasoning", fg_color="#ffb86c")
reasoning_button.pack(side="right", padx=5)

conversation_frame = ctk.CTkFrame(chat_frame, fg_color="#282a36")
conversation_frame.pack(padx=10, pady=10, fill="both", expand=True)

input_frame = ctk.CTkFrame(chat_frame, fg_color=("#282a36", "#282a36"))
input_frame.pack(fill="x", pady=5)
user_entry = ctk.CTkEntry(input_frame, width=350, fg_color="#44475a", text_color="white")
user_entry.pack(side="left", padx=5, expand=True)
user_entry.bind("<Return>", send_message)
send_button = ctk.CTkButton(input_frame, text="Send", command=send_message, fg_color="#50fa7b")
send_button.pack(side="right", padx=5)

app.mainloop()
