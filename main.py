
# main.py

import os
import logging
import gradio as gr
from dotenv import load_dotenv
from crewai import Agent
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Set OpenAI API Key (optional if using .env)
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Logging
logging.basicConfig(level=logging.INFO)

# LLM Setup
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# Interview Agent
interview_agent = Agent(
    role="Conversational Interviewer",
    goal="Conduct realistic interviews and give STAR feedback",
    backstory="A seasoned HR and technical interviewer with experience in multiple industries.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# State
dialogue_history = []
settings = {}

# Define Custom Theme
custom_theme = gr.themes.Base(
    primary_hue="blue",
    secondary_hue="gray"
)

# App UI
with gr.Blocks(theme=custom_theme) as app:
    gr.Markdown("# 🎯 Ace-Bot 💼 – Smart Interview Companion")

    with gr.Column():
        role = gr.Textbox(label="Job Role", placeholder="e.g., UI Developer")
        level = gr.Dropdown(["Intern", "Entry", "Mid", "Senior"], label="Experience Level")
        itype = gr.Dropdown(["HR", "Technical", "Behavioral"], label="Interview Type")
        start_btn = gr.Button("Start Interview")

    chatbot = gr.Chatbot(label="Interview Chat")

    with gr.Row():
        user_input = gr.Textbox(label="Your Answer", placeholder="Type your answer here", interactive=False)
        send_btn = gr.Button("Enter", interactive=False)

    # Start Interview Logic
    def start_interview(job_role, exp_level, interview_type):
        settings.update({"role": job_role, "level": exp_level, "type": interview_type})
        greeting = (
            f"👋 Hi, I’m your interview partner. Let’s start your {interview_type} interview "
            f"for a {exp_level} {job_role}.

First, could you please introduce yourself?"
        )
        dialogue_history.clear()
        dialogue_history.append(("Ace-Bot", greeting))
        return dialogue_history, gr.update(interactive=True), gr.update(interactive=True)

    # Continue Interview Logic
    def continue_conversation(message):
        try:
            user_msg = message.strip()
            if not user_msg:
                return dialogue_history

            dialogue_history.append(("You", user_msg))

            prompt = (
                f"You are interviewing a {settings.get('level', 'Entry')} {settings.get('role', 'Candidate')} "
                f"in a {settings.get('type', 'HR')} interview.
"
                f"Here is the last user response: '{user_msg}'.
"
                "Continue the interview by giving STAR feedback, and then ask the next relevant question."
            )

            response = llm.predict(prompt)
            dialogue_history.append(("Ace-Bot", response))

            return dialogue_history
        except Exception as e:
            error_msg = f"⚠️ Sorry, something went wrong: {str(e)}"
            dialogue_history.append(("Ace-Bot", error_msg))
            return dialogue_history

    # Bind Events
    start_btn.click(start_interview, inputs=[role, level, itype], outputs=[chatbot, user_input, send_btn])
    user_input.submit(continue_conversation, inputs=user_input, outputs=chatbot)
    send_btn.click(continue_conversation, inputs=user_input, outputs=chatbot)

ui.launch()
