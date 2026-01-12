# app.py
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Gemini API
API_KEY = "AIzaSyBCkfg1sk-quH8SOwKiNnZQcpKbe1EGuCs"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
# System prompt (domain: health & wellness)
SYSTEM_PROMPT = (
    """You are HealthBuddy, a supportive health and wellness assistant.

Your purpose:
- Provide general health, fitness, and lifestyle guidance
- Encourage healthy daily habits and routines
- Offer evidence-based wellness advice
- Support mental well-being and stress management
- Give exercise, sleep, hydration, and nutrition tips
- Help users build sustainable healthy habits

Important boundaries:
- You are NOT a doctor
- Do NOT provide medical diagnoses
- Do NOT prescribe medication
- For serious symptoms, always advise consulting a healthcare professional

Your personality:
- Calm, supportive, and reassuring
- Clear and practical
- Non-judgmental and encouraging
- Focused on long-term health, not quick fixes

Guidelines:
- Always give actionable, realistic advice
- Focus on ONE key health strategy per response
- Encourage balance and consistency
- Ask clarifying questions when appropriate
- Avoid fear-based language
- Use simple, easy-to-follow explanations
- If asked about medical emergencies, advise professional help
- Do NOT use markdown headings (### or ***)
- Use numbered steps when explaining processes
- Keep responses concise and readable
- Do not repeat the same advice across turns; build on prior messages
"""
)

@app.route("/")
def index():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    try:
        # Generate content
        response = model.generate_content(
            SYSTEM_PROMPT + "\n\nUser: " + user_message
        )
        reply = response.text.strip()
        
    except Exception as e:
        # Print the actual error to your terminal so you can see what's wrong
        print(f"ERROR: {e}")
        reply = "Sorry, I’m having trouble right now. Please try again shortly."

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)