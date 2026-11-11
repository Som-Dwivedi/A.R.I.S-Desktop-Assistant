import datetime
import json
import os
import customtkinter as ctk
import webbrowser
import subprocess
import requests
from music import play_music

# ==================== YOUR EXACT BACKEND LOGIC ====================
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

user_data = load_memory()

# Flag for multi-step 'naam()' command sequence
waiting_for_name_input = False

def greet():
    name = user_data.get("name", "")
    if name:
        return f"Hello {name}! How are you?"
    else:
        return "Hello! How are you?"

def ask():
    return "Awesome! How can I help?"

def who():
    return "I am ARIS, your personal AI assistant."

def naam():
    global waiting_for_name_input
    waiting_for_name_input = True
    return "My name is ARIS.\nWhat is your name?"

def ainame():
    name = user_data.get("name", "")
    if name:
        return f"Your name is {name}."
    else:
        return "I don't know your name yet. Tell me 'my name is [your name]'."

def telltime():
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    return f"Current time is {current_time}"

def telldate():
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    return f"Today's date is {current_date}"

def tellday():
    current_day = datetime.datetime.now().strftime("%A")
    return f"Today is {current_day}."

def open_app(command):
    command = command.lower()

    if "youtube" in command:
        webbrowser.open("https://www.youtube.com/")
        return "Opening YouTube..."

    elif "google" in command:
        webbrowser.open("https://google.com")
        return "Opening Google..."

    elif "chatgpt" in command:
        webbrowser.open("https://chat.openai.com")
        return "Opening ChatGPT..."

    elif "calculator" in command:
        subprocess.Popen("calc")
        return "Opening Calculator..."

    elif "notepad" in command:
        subprocess.Popen("notepad")
        return "Opening Notepad..."

    elif "paint" in command:
        subprocess.Popen("mspaint")
        return "Opening Paint..."

    elif "vscode" in command:
        os.system("code")
        return "Opening VS Code..."
    else:
        return "I don't know that application."

def remember_fact(command):
    # Command: "remember that my birthday is on 12 december"
    fact = command.replace("remember that", "").strip()
    
    # Key ke aage se "my " hata do agar ho toh
    if fact.startswith("my "):
        fact = fact[3:].strip()
        
    if " is " in fact:
        key, value = fact.split(" is ", 1)
        user_data[key.strip()] = value.strip()
        save_memory(user_data)
        return f"Got it! Saved your {key.strip()} as '{value.strip()}'."
    else:
        return "Please specify in format: 'remember that [item] is [value]'."

def recall_fact(command):
    command = command.lower().strip()

    if command.startswith("what is my "):
        item = command.replace("what is my ", "").strip()

        if item in user_data:
            return f"Your {item} is {user_data[item]}."
        else:
            return f"I don't know your {item} yet."

    return "I don't have that information."
def thank():
    name = user_data.get("name", "")
    return f"Happy to help you {name}!!" if name else "Happy to help you!!"

def bye():
    return "Goodbye! Have a great day."

conversation_history = []

def get_relevant_memory(prompt):
    if not user_data:
        return ""

    prompt_words = set(prompt.lower().split())
    relevant = []

    for key, value in user_data.items():
        key_words = set(str(key).lower().split())
        value_words = set(str(value).lower().split())

        # Directly relevant memory
        if prompt_words & (key_words | value_words):
            relevant.append(f"{key}: {value}")

    # Always keep the user's name available
    if "name" in user_data and not any(
        item.startswith("name:") for item in relevant
    ):
        relevant.insert(0, f"name: {user_data['name']}")

    # Limit memory sent to the model
    relevant = relevant[:8]

    if not relevant:
        return ""

    return "\n".join(relevant)

def ask_ai(prompt):
    global conversation_history

    system_prompt = """
You are A.R.I.S. — Advanced Robotic Intelligence System,
a personal AI assistant and close digital companion for the user.

PERSONALITY:
- Talk naturally and casually, like a smart friend who happens to be an AI.
- Be warm, relaxed, and human-like in conversation.
- You can use casual words like "bro", "bhai", "yeah", "nah", "yep", "got it" when they fit naturally.
- Do NOT force slang into every response.
- Do not sound like a corporate customer-support agent.
- Do not sound overly formal, robotic, or textbook-like.
- Don't constantly say things like "Certainly", "Absolutely", "I understand", or "As an AI".
- If the user is joking, joke back naturally.
- If the user is frustrated, respond like a friend who is actually trying to help.
- If the user asks for advice, give your honest opinion instead of automatically agreeing.
- If the user's idea is weak or has a problem, tell them directly and explain why.

INTELLIGENCE:
- Think before answering.
- Don't blindly agree with the user.
- Challenge weak assumptions when necessary.
- Give practical advice instead of generic motivational statements.
- Never make up information.
- If you don't know something, say so.

LANGUAGE:
- Understand Hindi, English, and Hinglish naturally.
- The user may switch between Hindi and English in the same sentence.
- If the user speaks in Hinglish, reply in natural Hinglish.
- If the user speaks mostly Hindi, reply mostly Hindi.
- If the user speaks English, reply in English.
- Understand casual texting such as "bhai", "kr", "bta", "ni", "mtlb", etc.

CONVERSATION STYLE:
- Talk like an intelligent buddy, not a formal assistant.
- Keep simple conversations short and natural.
- Don't repeat the user's question unnecessarily.
- Don't introduce yourself unless relevant.
"""

    # Add the new user message
    conversation_history.append({
        "role": "user",
        "content": prompt
    })

    # Keep only the latest 15 messages
    conversation_history = conversation_history[-15:]
    memory_context = get_relevant_memory(prompt)
    # Build the conversation for Ollama
    conversation_text = ""

    for message in conversation_history:
        if message["role"] == "user":
            conversation_text += f"USER: {message['content']}\n"
        else:
            conversation_text += f"A.R.I.S.: {message['content']}\n"

    full_prompt = f"""
{system_prompt}

RELEVANT LONG-TERM MEMORY:
{memory_context if memory_context else "No relevant memory available."}

RECENT CONVERSATION:
{conversation_text}

Respond naturally to the user's latest message.
"""


    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:latest",
                "prompt": full_prompt,
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            ai_response = response.json()["response"].strip()

            # Save A.R.I.S.'s response to conversation history
            conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })

            return ai_response

        return "I couldn't connect to my AI core."

    except requests.exceptions.ConnectionError:
        return "Ollama is not running. Please start the Ollama service."

    except requests.exceptions.Timeout:
        return "The AI core took too long to respond."

    except Exception as e:
        return f"AI Error: {str(e)}"
# Exact Routing logic mapping your original while loop conditions
def handle_command(command_raw):
    global waiting_for_name_input
    command = command_raw.strip().lower()

    # Handling second step of naam()
    if waiting_for_name_input:
        waiting_for_name_input = False
        user_name = command_raw.strip().title()
        user_data["name"] = user_name
        save_memory(user_data)
        return f"Nice to meet you, {user_name}! Saved your name in memory."

    if command in ["hello", "hey", "hi"]:
        return greet()
    elif command.startswith("what is my "):
        return recall_fact(command)
    elif command in ["fine", "good", "i am fine", "great"]:
        return ask()
    elif "who are you" in command:
        return who()
    elif "your name" in command:
        return naam()
    elif "my name" in command:
        return ainame()      
    elif "remember that" in command:
        return remember_fact(command_raw)
    elif "time" in command:
        return telltime()      
    elif "date" in command:
        return telldate()        
    elif command in ["day", "what day is it", "today's day"]:
        return tellday()       
    elif command in ["thankyou", "thanks", "thank you"]:
        return thank()
    elif command.startswith("open "):
        return open_app(command)   
    elif command == "bye":
        return bye()
    elif command.startswith("play "):
        song = command_raw[5:].strip()
        return play_music(song)
    else:
        return ask_ai(command_raw)


# ==================== HOLOGRAPHIC GUI INTERFACE ====================
ctk.set_appearance_mode("Dark")

class ARISHolographicHUD(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("A.R.I.S. // ADVANCED RESEARCH AND INTEGRATION SYSTEM")
        self.geometry("1280x720")
        self.configure(fg_color="#050811")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_center_panel()
        self._build_right_panel()

    def _build_left_panel(self):
        left_frame = ctk.CTkFrame(self, fg_color="#0A111E", corner_radius=15, border_width=1, border_color="#00F0FF")
        left_frame.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

        lbl_title = ctk.CTkLabel(left_frame, text="SYSTEM & MEMORY DATA", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00F0FF")
        lbl_title.pack(anchor="w", padx=15, pady=(15, 5))

        status_box = ctk.CTkFrame(left_frame, fg_color="#082032", corner_radius=10, border_width=1, border_color="#38BDF8")
        status_box.pack(fill="x", padx=12, pady=8)
        
        st_txt = (
            "• MEMORY FILE: ACTIVE\n"
            "• DATABASE: JSON INTEGRATED\n"
            "• ENCRYPTION: LOCAL SECURE"
        )
        ctk.CTkLabel(status_box, text=st_txt, font=ctk.CTkFont(size=11), text_color="#38BDF8", justify="left").pack(anchor="w", padx=10, pady=8)

        env_frame = ctk.CTkFrame(left_frame, fg_color="#0F172A", corner_radius=10, border_width=1, border_color="#1E293B")
        env_frame.pack(fill="x", padx=12, pady=10)
        
        ctk.CTkLabel(env_frame, text="SYSTEM TELEMETRY", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=10, pady=(8, 4))
        
        self._add_metric_bar(env_frame, "CORE LOAD", "28%", 0.28, "#00F0FF")
        self._add_metric_bar(env_frame, "MEMORY STORAGE", "45%", 0.45, "#A855F7")

    def _add_metric_bar(self, parent, label, val_text, progress, color):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(fill="x", padx=10, pady=5)
        
        lbl = ctk.CTkLabel(box, text=f"{label}: {val_text}", font=ctk.CTkFont(size=10), text_color="#CBD5E1")
        lbl.pack(anchor="w")
        
        pbar = ctk.CTkProgressBar(box, height=6, progress_color=color, fg_color="#1E293B")
        pbar.set(progress)
        pbar.pack(fill="x", pady=(2, 6))

    def _build_center_panel(self):
        center_frame = ctk.CTkFrame(self, fg_color="#060D19", corner_radius=15, border_width=1, border_color="#00F0FF")
        center_frame.grid(row=0, column=1, padx=6, pady=12, sticky="nsew")
        center_frame.grid_rowconfigure(2, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)

        header_box = ctk.CTkFrame(center_frame, fg_color="transparent")
        header_box.grid(row=0, column=0, pady=(15, 5))

        title = ctk.CTkLabel(header_box, text="A. R. I. S.", font=ctk.CTkFont(size=36, weight="bold"), text_color="#00F0FF")
        title.pack()
        subtitle = ctk.CTkLabel(header_box, text="ADVANCED RESEARCH AND INTEGRATION SYSTEM", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B")
        subtitle.pack()

        core_hud = ctk.CTkFrame(center_frame, fg_color="#0A1628", corner_radius=100, border_width=2, border_color="#00F0FF", width=120, height=120)
        core_hud.grid(row=1, column=0, pady=10)
        core_hud.grid_propagate(False)

        core_inner = ctk.CTkLabel(core_hud, text="⚙\nCORE", font=ctk.CTkFont(size=16, weight="bold"), text_color="#38BDF8")
        core_inner.place(relx=0.5, rely=0.5, anchor="center")

        self.chat_frame = ctk.CTkScrollableFrame(center_frame, fg_color="#091322", corner_radius=12, border_width=1, border_color="#1E293B")
        self.chat_frame.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")

        self._add_message("A.R.I.S.", "ARIS v0.5 with Memory is online...", is_user=False)

        input_container = ctk.CTkFrame(center_frame, fg_color="transparent")
        input_container.grid(row=3, column=0, padx=15, pady=15, sticky="ew")

        self.entry = ctk.CTkEntry(
            input_container, 
            placeholder_text="Enter command...", 
            height=45, 
            corner_radius=22,
            fg_color="#0F172A",
            border_color="#00F0FF",
            text_color="#F8FAFC",
            font=ctk.CTkFont(size=13)
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send_command())

        btn = ctk.CTkButton(
            input_container, 
            text="EXECUTE", 
            width=100, 
            height=45, 
            corner_radius=22,
            fg_color="#00F0FF",
            text_color="#050811",
            hover_color="#00B8D4",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.send_command
        )
        btn.pack(side="right")

    def _build_right_panel(self):
        right_frame = ctk.CTkFrame(self, fg_color="#0A111E", corner_radius=15, border_width=1, border_color="#00F0FF")
        right_frame.grid(row=0, column=2, padx=12, pady=12, sticky="nsew")

        lbl_title = ctk.CTkLabel(right_frame, text="MODULE STATUS", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00F0FF")
        lbl_title.pack(anchor="w", padx=15, pady=(15, 5))

        wave_box = ctk.CTkFrame(right_frame, fg_color="#0F172A", corner_radius=10, border_width=1, border_color="#1E293B")
        wave_box.pack(fill="x", padx=12, pady=15)

        ctk.CTkLabel(wave_box, text="NEURAL FEEDBACK", font=ctk.CTkFont(size=10, weight="bold"), text_color="#00F0FF").pack(anchor="w", padx=10, pady=(8, 4))
        self.wave_label = ctk.CTkLabel(wave_box, text=" ▂▃▅▆▇█▇▆▅▃▂ ", font=ctk.CTkFont(size=18), text_color="#38BDF8")
        self.wave_label.pack(pady=10)

        task_box = ctk.CTkFrame(right_frame, fg_color="#0F172A", corner_radius=10)
        task_box.pack(fill="both", expand=True, padx=12, pady=(0, 15))

        ctk.CTkLabel(task_box, text="ACTIVE CAPABILITIES", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=10, pady=(8, 4))
        
        tasks = ["[✓] Memory Protocol", "[✓] Holographic HUD Architecture"]
        for t in tasks:
            ctk.CTkLabel(task_box, text=t, font=ctk.CTkFont(size=11), text_color="#CBD5E1").pack(anchor="w", padx=10, pady=4)

    def _add_message(self, sender, text, is_user=False):
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        msg_box = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_box.pack(fill="x", pady=6, padx=5)

        bg_col = "#1E293B" if is_user else "#0B192C"
        border_col = "#38BDF8" if is_user else "#00F0FF"
        text_col = "#F8FAFC" if is_user else "#00F0FF"
        align = "e" if is_user else "w"

        bubble = ctk.CTkFrame(msg_box, fg_color=bg_col, corner_radius=10, border_width=1, border_color=border_col)
        bubble.pack(anchor=align)

        header = ctk.CTkLabel(bubble, text=f"{sender} [{timestamp}]", font=ctk.CTkFont(size=9, weight="bold"), text_color="#64748B")
        header.pack(anchor="w", padx=10, pady=(4, 1))

        content = ctk.CTkLabel(bubble, text=text, font=ctk.CTkFont(size=12), text_color=text_col, wraplength=420, justify="left")
        content.pack(anchor="w", padx=10, pady=(0, 6))

    def send_command(self):
        cmd = self.entry.get().strip()
        if not cmd:
            return

        self._add_message("You", cmd, is_user=True)
        self.entry.delete(0, "end")

        # Calls exact backend router
        response = handle_command(cmd)

        self.after(200, lambda: self._add_message("ARIS", response, is_user=False))

if __name__ == "__main__":
    app = ARISHolographicHUD()
    app.mainloop()