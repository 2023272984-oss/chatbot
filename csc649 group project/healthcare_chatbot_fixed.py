import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu, ttk
import google.generativeai as genai
import threading
import json
import os
from datetime import datetime
import time

# ===================== CONFIGURATION =====================
GEMINI_API_KEY = "AIzaSyDKtbo_JfHjfnzYYV2LFxavnwQEx26mQDM"
MODEL_NAME = "gemini-pro"
DOMAIN = "Healthcare"

# ===================== SETUP GEMINI API =====================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# ===================== HEALTHCARE SYSTEM PROMPT =====================
HEALTHCARE_SYSTEM_PROMPT = """You are MediAssist, a healthcare information assistant.

YOUR ROLE:
- Provide general health information and wellness tips
- Explain common medical terms and conditions
- Suggest healthy lifestyle practices
- Offer basic first aid guidance
- Share nutritional information

CRITICAL RULES:
1. YOU ARE NOT A DOCTOR OR MEDICAL PROFESSIONAL
2. NEVER provide medical diagnoses
3. ALWAYS recommend consulting healthcare professionals for medical concerns
4. Focus on prevention and general wellness
5. Keep responses clear, accurate, and under 3-4 sentences
6. Use simple language understandable by non-medical users
7. When discussing symptoms, emphasize seeing a doctor
8. Never recommend specific medications or dosages

DISCLAIMER TO INCLUDE IN EVERY RESPONSE:
"I am an AI assistant providing general health information. I am not a medical professional. Always consult a doctor for medical advice."

EXAMPLE RESPONSES:
User: "I have a headache"
Assistant: "Headaches can have various causes like tension, dehydration, or lack of sleep. Try drinking water, resting in a dark room, or applying a cool compress. If headaches persist or are severe, please consult a doctor. I am an AI assistant providing general health information. I am not a medical professional. Always consult a doctor for medical advice."

User: "How to prevent flu?"
Assistant: "To prevent flu: get annual flu vaccine, wash hands frequently, avoid close contact with sick people, and maintain a healthy lifestyle with good nutrition and sleep. I am an AI assistant providing general health information. I am not a medical professional. Always consult a doctor for medical advice."

Now begin assisting as MediAssist:"""

# ===================== HEALTHCARE KNOWLEDGE BASE =====================
HEALTH_TOPICS = {
    "First Aid": [
        "Burns treatment",
        "CPR basics",
        "Choking emergency",
        "Cuts and wounds",
        "Sprains and strains"
    ],
    "Nutrition": [
        "Balanced diet",
        "Vitamins and minerals",
        "Hydration importance",
        "Healthy eating tips",
        "Food allergies"
    ],
    "Exercise": [
        "Daily activity recommendations",
        "Strength training",
        "Cardiovascular exercise",
        "Stretching benefits",
        "Exercise safety"
    ],
    "Mental Health": [
        "Stress management",
        "Sleep hygiene",
        "Mindfulness techniques",
        "Anxiety coping",
        "Depression awareness"
    ],
    "Prevention": [
        "Vaccination information",
        "Health screenings",
        "Hygiene practices",
        "Disease prevention",
        "Regular checkups"
    ]
}

# ===================== MAIN HEALTHCARE CHATBOT =====================
class HealthcareChatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("🏥 MediAssist - Healthcare Information Assistant")
        self.root.geometry("900x750")
        self.root.configure(bg="#e8f4f8")
        
        # Conversation history
        self.conversation = []
        self.conversation_history = [{"role": "system", "content": HEALTHCARE_SYSTEM_PROMPT}]
        
        # Statistics
        self.query_count = 0
        self.start_time = datetime.now()
        
        # Create GUI
        self.setup_gui()
        self.create_menu()
        self.setup_sidebar()
        
        # Initial greeting
        self.display_welcome_message()
        
    def setup_gui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg="#0077b6", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title and logo
        title_frame = tk.Frame(header_frame, bg="#0077b6")
        title_frame.pack(pady=15)
        
        self.logo_label = tk.Label(
            title_frame,
            text="🏥",
            font=("Arial", 24),
            bg="#0077b6",
            fg="white"
        )
        self.logo_label.pack(side=tk.LEFT, padx=(20, 10))
        
        title_text = tk.Label(
            title_frame,
            text="MediAssist - Healthcare Information Assistant",
            font=("Arial", 20, "bold"),
            bg="#0077b6",
            fg="white"
        )
        title_text.pack(side=tk.LEFT)
        
        # Disclaimer label
        disclaimer = tk.Label(
            header_frame,
            text="⚠️ For informational purposes only. Not a substitute for professional medical advice.",
            font=("Arial", 9, "italic"),
            bg="#ffcc00",
            fg="#333333",
            wraplength=600
        )
        disclaimer.pack(pady=(0, 5))
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg="#ffffff")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Chat display area with border
        chat_frame = tk.LabelFrame(main_frame, text="  Health Consultation  ", 
                                 font=("Arial", 12, "bold"),
                                 bg="#ffffff", fg="#0077b6", bd=2, relief="groove")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#ffffff",
            fg="#333333",
            state="normal",
            height=20,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags for styling
        self.configure_tags()
        
        # Input area
        input_frame = tk.Frame(main_frame, bg="#ffffff")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.user_input = tk.Entry(
            input_frame,
            font=("Arial", 12),
            width=70,
            bg="#f8f9fa",
            fg="#333333",
            insertbackground="#0077b6",
            relief="solid",
            bd=1
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)
        self.user_input.bind("<KeyRelease>", self.on_key_release)
        
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            font=("Arial", 11, "bold"),
            bg="#0077b6",
            fg="white",
            activebackground="#005a8c",
            command=self.send_message,
            width=12,
            height=2,
            state="normal"
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Quick buttons frame
        quick_frame = tk.Frame(main_frame, bg="#ffffff")
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(quick_frame, text="Quick Topics:", font=("Arial", 10, "bold"), 
                bg="#ffffff", fg="#555555").pack(side=tk.LEFT, padx=(0, 10))
        
        quick_topics = ["Headache relief", "Healthy diet", "Exercise tips", "Stress management", "First aid basics"]
        for topic in quick_topics:
            btn = tk.Button(
                quick_frame,
                text=topic,
                font=("Arial", 9),
                bg="#e3f2fd",
                fg="#0077b6",
                command=lambda t=topic: self.use_quick_topic(t),
                relief="flat",
                padx=10,
                pady=4
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_bar = tk.Frame(self.root, bg="#333333", height=30)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_bar,
            text=f"Ready • Queries: 0 • Session: {self.start_time.strftime('%H:%M')}",
            bg="#333333",
            fg="#ffffff",
            font=("Arial", 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.api_status = tk.Label(
            self.status_bar,
            text="API: Connected ✓",
            bg="#333333",
            fg="#4CAF50",
            font=("Arial", 9)
        )
        self.api_status.pack(side=tk.RIGHT, padx=10)
        
    def setup_sidebar(self):
        # Create sidebar for health topics
        sidebar = tk.Frame(self.root, bg="#f0f8ff", width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0), pady=10)
        sidebar.pack_propagate(False)
        
        # Sidebar header
        sidebar_header = tk.Label(
            sidebar,
            text="📚 Health Topics",
            font=("Arial", 14, "bold"),
            bg="#0077b6",
            fg="white",
            pady=10
        )
        sidebar_header.pack(fill=tk.X)
        
        # Health categories
        for category, topics in HEALTH_TOPICS.items():
            category_frame = tk.LabelFrame(sidebar, text=category, font=("Arial", 11, "bold"),
                                         bg="#f0f8ff", fg="#0077b6")
            category_frame.pack(fill=tk.X, padx=10, pady=5)
            
            for topic in topics:
                topic_btn = tk.Button(
                    category_frame,
                    text=f"• {topic}",
                    font=("Arial", 9),
                    bg="white",
                    fg="#333333",
                    anchor="w",
                    command=lambda t=topic: self.use_health_topic(t),
                    relief="flat",
                    width=25
                )
                topic_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # Emergency info
        emergency_frame = tk.Frame(sidebar, bg="#fff3cd", relief="solid", bd=1)
        emergency_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(emergency_frame, text="🆘 Emergency", font=("Arial", 11, "bold"),
                bg="#fff3cd", fg="#856404").pack(pady=5)
        tk.Label(emergency_frame, text="For emergencies:", font=("Arial", 9),
                bg="#fff3cd", fg="#856404").pack()
        tk.Label(emergency_frame, text="Call 911 or visit ER", font=("Arial", 10, "bold"),
                bg="#fff3cd", fg="#dc3545").pack(pady=5)
        
    def configure_tags(self):
        """Configure text tags for chat display"""
        # User messages
        self.chat_display.tag_config("user", 
                                   foreground="#1a73e8",
                                   font=("Arial", 11, "bold"))
        
        # Bot messages
        self.chat_display.tag_config("bot", 
                                   foreground="#0d652d",
                                   font=("Arial", 11))
        
        # Disclaimer in bot messages
        self.chat_display.tag_config("disclaimer",
                                   foreground="#e65100",
                                   font=("Arial", 9, "italic"))
        
        # Timestamps
        self.chat_display.tag_config("timestamp",
                                   foreground="#666666",
                                   font=("Arial", 8))
        
        # System messages
        self.chat_display.tag_config("system",
                                   foreground="#7b1fa2",
                                   font=("Arial", 10, "italic"))
        
        # Error messages
        self.chat_display.tag_config("error",
                                   foreground="#d32f2f",
                                   font=("Arial", 10, "bold"))
        
    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Conversation", command=self.save_conversation)
        file_menu.add_command(label="Export as PDF", command=self.export_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Clear Chat", command=self.clear_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools Menu
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Test API Connection", command=self.test_api_connection)
        tools_menu.add_command(label="Health Assessment", command=self.health_assessment)
        tools_menu.add_command(label="BMI Calculator", command=self.bmi_calculator)
        tools_menu.add_separator()
        tools_menu.add_command(label="View Statistics", command=self.show_statistics)
        
        # Resources Menu
        resources_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Resources", menu=resources_menu)
        resources_menu.add_command(label="First Aid Guide", command=self.show_first_aid)
        resources_menu.add_command(label="Nutrition Tips", command=self.show_nutrition)
        resources_menu.add_command(label="Exercise Guide", command=self.show_exercise)
        resources_menu.add_command(label="Mental Wellness", command=self.show_mental_health)
        
        # Help Menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About MediAssist", command=self.show_about)
        help_menu.add_command(label="How to Use", command=self.show_instructions)
        help_menu.add_command(label="Disclaimer", command=self.show_disclaimer)
        help_menu.add_separator()
        help_menu.add_command(label="Report Issue", command=self.report_issue)
        
    def display_welcome_message(self):
        """Display welcome message with health tips"""
        welcome_msg = """🏥 Welcome to MediAssist!

I'm your healthcare information assistant. I can help with:
• General health information and wellness tips
• Basic first aid guidance
• Nutrition and exercise advice
• Mental health support
• Disease prevention information

⚠️ IMPORTANT: I am NOT a doctor. For medical emergencies, call 911.
For specific medical advice, always consult a healthcare professional.

What health topic can I help you with today?"""
        
        self.add_message("system", welcome_msg)
        
    def add_message(self, sender, message):
        """Add a message to the chat display"""
        timestamp = datetime.now().strftime("%H:%M")
        
        # Insert timestamp
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Insert message
        if sender == "user":
            self.chat_display.insert(tk.END, f"You: {message}\n\n", "user")
            self.conversation.append({"time": timestamp, "sender": "user", "message": message})
        elif sender == "bot":
            # Split message to highlight disclaimer
            lines = message.split('\n')
            for i, line in enumerate(lines):
                if "I am an AI assistant" in line or "consult a doctor" in line.lower():
                    self.chat_display.insert(tk.END, f"Assistant: {line}\n", "disclaimer")
                else:
                    self.chat_display.insert(tk.END, f"Assistant: {line}\n", "bot")
            self.chat_display.insert(tk.END, "\n", "bot")
            self.conversation.append({"time": timestamp, "sender": "bot", "message": message})
        elif sender == "system":
            self.chat_display.insert(tk.END, f"System: {message}\n\n", "system")
            self.conversation.append({"time": timestamp, "sender": "system", "message": message})
        elif sender == "error":
            self.chat_display.insert(tk.END, f"Error: {message}\n\n", "error")
            self.conversation.append({"time": timestamp, "sender": "error", "message": message})
        
        # Auto-scroll
        self.chat_display.see(tk.END)
        
        # Update statistics
        if sender == "user":
            self.query_count += 1
            self.update_status()
    
    def update_status(self):
        """Update status bar information"""
        duration = datetime.now() - self.start_time
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        self.status_label.config(
            text=f"Ready • Queries: {self.query_count} • Duration: {hours}h {minutes}m"
        )
    
    def send_message(self, event=None):
        """Send user message to Gemini API"""
        user_message = self.user_input.get().strip()
        
        if not user_message:
            return
        
        # Clear input
        self.user_input.delete(0, tk.END)
        self.send_button.config(state="disabled")
        
        # Add user message
        self.add_message("user", user_message)
        
        # Show typing indicator
        self.show_typing_indicator(True)
        
        # Process in background thread
        thread = threading.Thread(target=self.process_message, args=(user_message,))
        thread.daemon = True
        thread.start()
    
    def process_message(self, user_message):
        """Process message with Gemini API"""
        try:
            # Add disclaimer context
            prompt = f"{HEALTHCARE_SYSTEM_PROMPT}\n\nUser question: {user_message}"
            
            # Call Gemini API
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 300,
                }
            )
            
            bot_response = response.text.strip()
            
            # Ensure disclaimer is included
            if "I am an AI assistant" not in bot_response:
                bot_response += "\n\nI am an AI assistant providing general health information. I am not a medical professional. Always consult a doctor for medical advice."
            
            # Update GUI
            self.root.after(0, self.display_response, bot_response)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.display_response, error_msg)
    
    def display_response(self, response):
        """Display the bot's response"""
        self.show_typing_indicator(False)
        
        if response.startswith("Error:"):
            self.add_message("error", response)
        else:
            self.add_message("bot", response)
        
        self.send_button.config(state="normal")
    
    def show_typing_indicator(self, show=True):
        """Show/hide typing indicator"""
        if show:
            self.api_status.config(text="API: Processing... ⏳", fg="#ff9800")
        else:
            self.api_status.config(text="API: Connected ✓", fg="#4CAF50")
        self.root.update()
    
    def use_quick_topic(self, topic):
        """Use quick topic button"""
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, topic)
        self.send_message()
    
    def use_health_topic(self, topic):
        """Use health topic from sidebar"""
        self.add_message("user", f"Tell me about {topic}")
        self.show_typing_indicator(True)
        
        thread = threading.Thread(target=self.process_message, args=(f"Explain {topic} in simple terms",))
        thread.daemon = True
        thread.start()
    
    def test_api_connection(self):
        """Test Gemini API connection"""
        self.show_typing_indicator(True)
        
        def test():
            try:
                response = model.generate_content("Say 'MediAssist is working!'")
                if "MediAssist" in response.text:
                    messagebox.showinfo("API Test", "✅ Connection Successful!\n\nGemini API is working correctly.")
                else:
                    messagebox.showwarning("API Test", f"⚠️ Response: {response.text}")
            except Exception as e:
                messagebox.showerror("API Test Failed", f"❌ Connection Failed:\n\n{str(e)}")
            
            self.root.after(0, lambda: self.show_typing_indicator(False))
        
        thread = threading.Thread(target=test)
        thread.daemon = True
        thread.start()
    
    def health_assessment(self):
        """Simple health assessment tool"""
        assessment_window = tk.Toplevel(self.root)
        assessment_window.title("Health Assessment")
        assessment_window.geometry("500x400")
        assessment_window.configure(bg="#ffffff")
        
        questions = [
            "How many hours do you sleep per night?",
            "Do you exercise regularly? (Yes/No)",
            "How many glasses of water do you drink daily?",
            "Do you smoke? (Yes/No)",
            "Rate your stress level (1-10):"
        ]
        
        answers = []
        
        tk.Label(assessment_window, text="Health Assessment", 
                font=("Arial", 16, "bold"), bg="#ffffff", fg="#0077b6").pack(pady=10)
        
        for i, question in enumerate(questions):
            frame = tk.Frame(assessment_window, bg="#ffffff")
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            tk.Label(frame, text=f"{i+1}. {question}", 
                    font=("Arial", 11), bg="#ffffff", anchor="w").pack(fill=tk.X)
            
            entry = tk.Entry(frame, font=("Arial", 11), width=40)
            entry.pack(pady=2)
            answers.append(entry)
        
        def submit_assessment():
            responses = [entry.get().strip() for entry in answers]
            analysis = "Based on your responses:\n\n"
            
            # Simple analysis
            if len(responses[0]) > 0:
                sleep = int(responses[0]) if responses[0].isdigit() else 0
                if sleep < 7:
                    analysis += "• Consider aiming for 7-9 hours of sleep\n"
                else:
                    analysis += "• Good sleep duration\n"
            
            if responses[1].lower() == "yes":
                analysis += "• Great that you exercise regularly\n"
            else:
                analysis += "• Try to incorporate regular exercise\n"
            
            if len(responses[2]) > 0:
                water = int(responses[2]) if responses[2].isdigit() else 0
                if water < 8:
                    analysis += "• Increase water intake to 8+ glasses daily\n"
                else:
                    analysis += "• Good hydration habits\n"
            
            analysis += "\n⚠️ Remember: This is general advice. Consult a doctor for personalized assessment."
            
            self.add_message("bot", analysis)
            assessment_window.destroy()
        
        tk.Button(assessment_window, text="Submit Assessment", 
                 command=submit_assessment, bg="#0077b6", fg="white",
                 font=("Arial", 11, "bold")).pack(pady=20)
    
    def bmi_calculator(self):
        """BMI Calculator tool"""
        bmi_window = tk.Toplevel(self.root)
        bmi_window.title("BMI Calculator")
        bmi_window.geometry("400x350")
        bmi_window.configure(bg="#ffffff")
        
        tk.Label(bmi_window, text="BMI Calculator", 
                font=("Arial", 16, "bold"), bg="#ffffff", fg="#0077b6").pack(pady=10)
        
        # Weight input
        weight_frame = tk.Frame(bmi_window, bg="#ffffff")
        weight_frame.pack(pady=10)
        tk.Label(weight_frame, text="Weight (kg):", font=("Arial", 11), bg="#ffffff").pack(side=tk.LEFT)
        weight_entry = tk.Entry(weight_frame, font=("Arial", 11), width=10)
        weight_entry.pack(side=tk.LEFT, padx=10)
        
        # Height input
        height_frame = tk.Frame(bmi_window, bg="#ffffff")
        height_frame.pack(pady=10)
        tk.Label(height_frame, text="Height (cm):", font=("Arial", 11), bg="#ffffff").pack(side=tk.LEFT)
        height_entry = tk.Entry(height_frame, font=("Arial", 11), width=10)
        height_entry.pack(side=tk.LEFT, padx=10)
        
        result_label = tk.Label(bmi_window, text="", font=("Arial", 12), bg="#ffffff")
        result_label.pack(pady=20)
        
        def calculate_bmi():
            try:
                weight = float(weight_entry.get())
                height = float(height_entry.get()) / 100  # Convert cm to meters
                
                bmi = weight / (height ** 2)
                
                if bmi < 18.5:
                    category = "Underweight"
                    color = "#ff9800"
                elif bmi < 25:
                    category = "Normal weight"
                    color = "#4CAF50"
                elif bmi < 30:
                    category = "Overweight"
                    color = "#ff9800"
                else:
                    category = "Obese"
                    color = "#f44336"
                
                result_label.config(
                    text=f"BMI: {bmi:.1f}\nCategory: {category}",
                    fg=color,
                    font=("Arial", 12, "bold")
                )
                
                advice = f"Your BMI is {bmi:.1f} ({category}). "
                if category == "Normal weight":
                    advice += "Maintain your healthy lifestyle!"
                else:
                    advice += "Consider consulting a nutritionist or doctor for personalized advice."
                
                self.add_message("bot", advice)
                
            except:
                result_label.config(text="Please enter valid numbers", fg="#f44336")
        
        tk.Button(bmi_window, text="Calculate BMI", command=calculate_bmi,
                 bg="#0077b6", fg="white", font=("Arial", 11, "bold")).pack(pady=10)
    
    def show_statistics(self):
        """Show usage statistics"""
        duration = datetime.now() - self.start_time
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        stats = f"""
📊 Session Statistics:
────────────────────────
• Queries Processed: {self.query_count}
• Session Duration: {hours}h {minutes}m {seconds}s
• Start Time: {self.start_time.strftime('%H:%M:%S')}
• API Status: Connected
• Domain: Healthcare

💡 Tips:
• Save conversation for reference
• Use quick topics for common questions
• Always verify with professionals
"""
        
        messagebox.showinfo("Statistics", stats)
    
    def save_conversation(self):
        """Save conversation to JSON file"""
        try:
            filename = f"health_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            data = {
                "title": "MediAssist Conversation",
                "timestamp": datetime.now().isoformat(),
                "domain": "Healthcare",
                "query_count": self.query_count,
                "duration": str(datetime.now() - self.start_time),
                "conversation": self.conversation
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Saved", f"✅ Conversation saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save: {str(e)}")
    
    def export_pdf(self):
        """Export conversation as PDF (placeholder)"""
        messagebox.showinfo("Export PDF", "PDF export feature would be implemented with ReportLab library.")
        # In production, use: from reportlab.lib.pagesizes import letter
        # from reportlab.pdfgen import canvas
    
    def clear_chat(self):
        """Clear the chat history"""
        if messagebox.askyesno("Clear Chat", "Clear all conversation history?"):
            self.chat_display.delete(1.0, tk.END)
            self.conversation.clear()
            self.query_count = 0
            self.start_time = datetime.now()
            self.update_status()
            self.display_welcome_message()
    
    def show_about(self):
        """Show about information"""
        about_text = """
🏥 MediAssist - Healthcare Chatbot
────────────────────────────────
Version: 1.0 | Domain: Healthcare

📋 Project: CSC649 Group Project
🎯 Objective: Domain-specific chatbot using LLM API

👥 Team Roles:
• Project Coordinator: Overall management
• Frontend Developer: GUI design
• Backend Developer: API integration
• Domain Specialist: Healthcare content

🔧 Technology Stack:
• Python 3.10+
• Google Gemini API
• Tkinter GUI
• JSON for data storage

⚠️ DISCLAIMER:
This chatbot provides general health information only.
It is NOT a substitute for professional medical advice.
Always consult healthcare professionals for medical concerns.
"""
        messagebox.showinfo("About MediAssist", about_text)
    
    def show_disclaimer(self):
        """Show detailed disclaimer"""
        disclaimer = """
⚠️ IMPORTANT MEDICAL DISCLAIMER

MediAssist is an AI-powered healthcare information assistant designed to provide general health information and wellness guidance.

CRITICAL LIMITATIONS:
─────────────────────
1. NOT A MEDICAL PROFESSIONAL: I am an AI assistant, not a doctor, nurse, or licensed healthcare provider.

2. NO DIAGNOSIS: I cannot and will not provide medical diagnoses, treatment plans, or prescriptions.

3. EMERGENCY SITUATIONS: In case of medical emergencies, call 911 or your local emergency number immediately.

4. PROFESSIONAL ADVICE: Always consult qualified healthcare professionals for personal medical advice.

5. INFORMATION ACCURACY: While I strive for accuracy, medical information changes rapidly. Verify with current sources.

INTENDED USE:
─────────────
• General wellness information
• Basic first aid guidance
• Health education
• Preventive care suggestions

MISUSE WARNING:
───────────────
Do not use this chatbot for:
• Self-diagnosis
• Treatment decisions
• Emergency guidance
• Medication advice

By using MediAssist, you acknowledge these limitations and agree to seek professional medical care when needed.
"""
        messagebox.showwarning("Medical Disclaimer", disclaimer)
    
    def report_issue(self):
        """Report an issue placeholder"""
        messagebox.showinfo("Report Issue", 
            "To report an issue:\n\n"
            "1. Take a screenshot of the error\n"
            "2. Note the steps to reproduce\n"
            "3. Contact the development team\n\n"
            "This feature will be implemented in future versions.")
    
    def show_exercise(self):
        """Show exercise information"""
        exercise_info = """
🏃 EXERCISE GUIDELINES

RECOMMENDATIONS:
• Adults: 150 minutes of moderate aerobic activity or 75 minutes of vigorous activity per week
• Strength training: 2+ days per week (work all major muscle groups)
• Children (6-17): 60+ minutes of physical activity daily

BENEFITS:
• Reduces risk of chronic diseases
• Improves mental health and mood
• Helps with weight management
• Strengthens bones and muscles

TIPS:
• Start slowly and gradually increase intensity
• Find activities you enjoy
• Stay consistent
• Warm up and cool down properly
• Stay hydrated during exercise

⚠️ Consult a doctor before starting a new exercise program, especially if you have health concerns.
"""
        self.add_message("bot", exercise_info)
    
    def show_mental_health(self):
        """Show mental health information"""
        mental_health_info = """
🧠 MENTAL WELLNESS TIPS

SELF-CARE:
• Get enough sleep (7-9 hours for adults)
• Eat a balanced diet
• Exercise regularly
• Practice relaxation techniques (deep breathing, meditation)

STRESS MANAGEMENT:
• Identify stress triggers
• Take regular breaks
• Maintain a work-life balance
• Connect with friends and family

WHEN TO SEEK HELP:
• Persistent sadness or anxiety
• Difficulty functioning in daily life
• Changes in sleep or appetite
• Thoughts of self-harm

RESOURCES:
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741
• Seek professional help from a therapist or counselor

Remember: Mental health is just as important as physical health.
"""
        self.add_message("bot", mental_health_info)
    
    def on_key_release(self, event):
        """Enable/disable send button based on input"""
        if self.user_input.get().strip():
            self.send_button.config(state="normal", bg="#0077b6")
        else:
            self.send_button.config(state="disabled", bg="#cccccc")
    
    def show_first_aid(self):
        """Show first aid information"""
        first_aid = """
🆘 BASIC FIRST AID GUIDE

BURNS:
• Cool with running water for 20 minutes
• Cover with sterile dressing
• Don't apply ice, butter, or ointments
• Seek medical help for severe burns

CUTS & WOUNDS:
• Apply direct pressure to stop bleeding
• Clean with clean water
• Apply antibiotic ointment
• Cover with sterile bandage
• Watch for infection signs

CHOKING (Adult):
• Encourage coughing
• Perform abdominal thrusts (Heimlich maneuver)
• Call 911 if person becomes unconscious

CPR BASICS:
1. Check responsiveness
2. Call 911
3. Start chest compressions (100-120/min)
4. Use AED if available

⚠️ Always get proper first aid training from certified organizations like Red Cross.
"""
        self.add_message("bot", first_aid)
    
    def show_nutrition(self):
        """Show nutrition information"""
        nutrition = """
🥦 NUTRITION GUIDELINES

BALANCED DIET:
• Fruits & Vegetables: 5+ servings daily
• Whole Grains: Brown rice, whole wheat bread
• Protein: Lean meats, fish, beans, nuts
• Dairy: Low-fat milk, yogurt, cheese
• Healthy Fats: Olive oil, avocado, nuts

HYDRATION:
• Drink 8+ glasses of water daily
• Limit sugary drinks
• Watch for dehydration signs

HEALTHY EATING TIPS:
• Eat regular meals
• Portion control
• Read food labels
• Cook at home more often
• Limit processed foods

VITAMINS:
• Vitamin C: Citrus fruits, peppers
• Vitamin D: Sunlight, fatty fish
• Calcium: Dairy, leafy greens
• Iron: Red meat, spinach

Consult a nutritionist for personalized advice.
"""
        self.add_message("bot", nutrition)
    
    def show_instructions(self):
        """Show usage instructions"""
        instructions = """
📖 HOW TO USE MEDIASSIST

BASIC USAGE:
────────────
1. Type your health question in the input box
2. Press Enter or click Send
3. Receive AI-generated health information
4. Use quick buttons for common topics

FEATURES:
─────────
• Sidebar Topics: Click any health topic for instant information
• Quick Buttons: Common questions at bottom
• Tools Menu: Health assessment, BMI calculator
• Resources: First aid, nutrition, exercise guides

IMPORTANT NOTES:
───────────────
• Always verify information with professionals
• Use for general information only
• Don't rely on for emergencies
• Save conversations for reference

For best results, ask specific questions and provide context when needed.
"""
        messagebox.showinfo("Instructions", instructions)

# ===================== START APPLICATION =====================
def main():
    # Check and install dependencies
    try:
        import google.generativeai
    except ImportError:
        print("Installing required packages...")
        os.system("pip install google-generativeai")
        import google.generativeai
    
    # Create main window
    root = tk.Tk()
    app = HealthcareChatbot(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start application
    root.mainloop()

if __name__ == "__main__":
    main()
