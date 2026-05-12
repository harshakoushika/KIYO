import streamlit as st
import ollama
from google.cloud import translate_v2 as translate
import speech_recognition as sr
import pyttsx3
import threading
import os
import time

# Import the new location detection module
import auto_detect

# Set up Google Cloud credentials from an environment variable.
try:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
    translate_client = translate.Client()
except Exception as e:
    st.error(f"Error initializing Google Cloud Translate client: {e}")
    st.warning("Please ensure you have set up your Google Cloud credentials correctly.")
    st.stop()

# Initialize session state variables at the top
if "stop_flag" not in st.session_state:
    st.session_state.stop_flag = False
if "speech_thread" not in st.session_state:
    st.session_state.speech_thread = None
if "dyslexia_mode" not in st.session_state:
    st.session_state.dyslexia_mode = False
if "user_location" not in st.session_state:
    st.session_state.user_location = None
if "last_detected_lang" not in st.session_state:
    st.session_state.last_detected_lang = 'en'
if "show_speech_options" not in st.session_state:
    st.session_state.show_speech_options = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "candidate_responses" not in st.session_state:
    st.session_state.candidate_responses = None
if "dialect" not in st.session_state:
    st.session_state.dialect = 'Informal'
if "personality" not in st.session_state:
    st.session_state.personality = 'Default'

# Function to stop the speech engine
def stop_speaking():
    if st.session_state.speech_thread and st.session_state.speech_thread.is_alive():
        if hasattr(st.session_state, 'speech_engine') and st.session_state.speech_engine:
            st.session_state.speech_engine.stop()
        st.session_state.speech_thread.join()
        st.session_state.speech_thread = None

# Function to run the TTS engine in a separate thread
def speak_async(text, lang):
    """Initializes and runs the TTS engine in a new thread."""
    def run_engine():
        engine = pyttsx3.init()
        st.session_state.speech_engine = engine
        engine.setProperty('rate', 170)
        try:
            voices = engine.getProperty('voices')
            for voice in voices:
                if voice.id.lower().startswith(lang.lower()):
                    engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            st.warning(f"Could not set voice for language '{lang}': {e}")
        engine.say(text)
        engine.runAndWait()
        st.session_state.speech_engine = None
    if st.session_state.speech_thread and st.session_state.speech_thread.is_alive():
        return
    st.session_state.speech_thread = threading.Thread(target=run_engine)
    st.session_state.speech_thread.start()

# Streamlit UI configuration
st.set_page_config(page_title="Kiyo: Universal Language Chatbot", layout="wide")

# Custom CSS for a modern, responsive chat interface and dyslexia font support
font_family = "Lexend" if st.session_state.dyslexia_mode else "sans-serif"
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;700&display=swap');
    
    body, .stText, .stMarkdown, .stTextInput, .st-expander, .stButton, .chat-bubble, .user-message, .bot-message {{
        font-family: '{font_family}', {font_family}, sans-serif !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: '{font_family}', {font_family}, sans-serif !important;
    }}
    
    .reportview-container .main .block-container {{
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
    }}
    .chat-bubble {{
        border-radius: 15px;
        padding: 10px 15px;
        margin-bottom: 10px;
        max-width: 75%;
    }}
    .user-message {{
        background-color: #007bff;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 0;
    }}
    .bot-message {{
        background-color: #f1f1f1;
        color: black;
        border-bottom-left-radius: 0;
    }}
    .st-expander {{
        border-radius: 15px;
    }}
    .stButton>button {{
        border-radius: 15px;
        width: 100%;
        border: none;
        padding: 10px;
    }}
    .stButton>button[key="prefer_1"], .stButton>button[key="prefer_2"] {{
        background-color:BLUE;
        color: white;
    }}
    .stButton>button[key="speak_button"], .stButton>button[key="repeat_button"], .stButton>button[key="stop_button"], .stButton>button[key="mic_button"] {{
        background-color:BLUE;
        color: white;
    }}
    .stButton>button:hover {{
        background-color:blue;
    }}
    .stButton>button:active {{
        background-color: Blue;
    }}
    h1, h2 {{
        text-align: center;
    }}
    .chat-input-container {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        background-color: #fff;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    }}
    .chat-input-container .stTextInput, .chat-input-container .stButton {{
        flex: 1;
    }}
    .chat-input-container .stButton {{
        flex: 0 1 auto;
        width: auto;
    }}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    
    st.subheader("Feedback System")
    with st.expander("Share your feedback"):
        feedback_text = st.text_area("Your comments and suggestions:", height=100)
        if st.button("Submit Feedback"):
            if feedback_text:
                st.success("Thank you for your feedback! It has been submitted.")
            else:
                st.warning("Please enter your feedback before submitting.")
    
    # Bot Customization moved to the sidebar as requested
    with st.expander("Bot Customization"):
        st.subheader("Dialect")
        
        # Use st.radio for a simple and effective single-choice selection.
        # It automatically handles the logic of ensuring only one option is selected.
        st.session_state.dialect = st.radio(
            "Select a dialect:",
            options=('Formal', 'Informal'),
            index=('Formal', 'Informal').index(st.session_state.dialect),
            key='dialect_radio'  # A unique key is a good practice for widgets
        )
        st.write(f"Current Dialect: **{st.session_state.dialect}**")
        
        st.subheader("Personality")
        st.session_state.personality = st.radio(
            "Select a personality:",
            options=('Default', 'Logic', 'Brainstorm', 'Example-based Learning (Analogy-based)', 'Explanation', 'Differentiative', 'Pros and Cons Type'),
            index=('Default', 'Logic', 'Brainstorm', 'Example-based Learning (Analogy-based)', 'Explanation', 'Differentiative', 'Pros and Cons Type').index(st.session_state.personality),
            key='personality_radio'
        )
        st.write(f"Current Personality: **{st.session_state.personality}**")


# Main App UI
st.title("🗣️ Kiyo: Universal Language Support Chatbot")
st.write("Promoting SDG 10.")

# Dyslexia-friendly font toggle button
dyslexia_toggle = st.checkbox("Toggle Dyslexia-Friendly Font", value=st.session_state.dyslexia_mode)
if dyslexia_toggle != st.session_state.dyslexia_mode:
    st.session_state.dyslexia_mode = dyslexia_toggle
    st.rerun()

# Use auto-detected location for language suggestion
if st.session_state.user_location is None:
    ip_address = auto_detect.get_public_ip()
    if ip_address:
        state, country = auto_detect.get_state_from_ip(ip_address)
        if state and country == "India":
            st.session_state.user_location = state
        else:
            st.session_state.user_location = None
    else:
        st.session_state.user_location = None
        st.warning("Could not automatically detect your location. Please check your network connection.")
        
if st.session_state.user_location:
    suggested_lang = auto_detect.get_language_from_state(st.session_state.user_location)
    st.info(f"Based on your location ({st.session_state.user_location.title()}), the suggested language is: **{suggested_lang.title()}**")
    if not st.session_state.messages and not st.session_state.candidate_responses:
        st.markdown(f"Start by speaking or typing in **{suggested_lang.title()}**!")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to handle chat logic
def handle_chat_input(prompt):
    if prompt:
        st.session_state.stop_flag = False
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Reset candidate responses for a new chat turn
        st.session_state.candidate_responses = None
        
        try:
            detected_lang = translate_client.detect_language(prompt)['language']
            st.info(f"Detected Language: {detected_lang}")
            if detected_lang == 'hi-Latn':
                detected_lang = 'hi'
            st.session_state.last_detected_lang = detected_lang
        except Exception as e:
            st.error(f"Error detecting language with Google Cloud Translate: {e}")
            detected_lang = 'en'
            st.session_state.last_detected_lang = detected_lang
        
        if detected_lang != 'en':
            try:
                translated_prompt = translate_client.translate(prompt, target_language='en')['translatedText']
            except Exception as e:
                st.error(f"Error translating to English: {e}")
                translated_prompt = prompt
        else:
            translated_prompt = prompt
        
        # Append dialect statement to the translated prompt
        prompt_suffix = ""
        if st.session_state.dialect == 'Formal':
            prompt_suffix = ", formal"
        else:
            prompt_suffix = ", informal"
        
        # Only add the personality if it's not the default option
        if st.session_state.personality != 'Default':
            prompt_suffix += f", act as a {st.session_state.personality} type bot"

        translated_prompt += prompt_suffix

        # Generate two responses for RLHF
        with st.spinner("Generating two responses..."):
            try:
                # First response
                response_stream1 = ollama.chat(
                    model='llama3',
                    messages=[{'role': 'user', 'content': translated_prompt}],
                    stream=True
                )
                full_response1 = "".join(chunk['message']['content'] for chunk in response_stream1 if chunk.get('done') is not True)
                
                # Second response (can be a slightly different prompt for variety)
                response_stream2 = ollama.chat(
                    model='llama3',
                    messages=[{'role': 'user', 'content': translated_prompt + " Give a different version."}],
                    stream=True
                )
                full_response2 = "".join(chunk['message']['content'] for chunk in response_stream2 if chunk.get('done') is not True)

                # Translate responses back
                if detected_lang != 'en':
                    translated_response1 = translate_client.translate(full_response1, target_language=detected_lang)['translatedText']
                    translated_response2 = translate_client.translate(full_response2, target_language=detected_lang)['translatedText']
                else:
                    translated_response1 = full_response1
                    translated_response2 = full_response2

                st.session_state.candidate_responses = {
                    'response1': translated_response1,
                    'response2': translated_response2
                }

            except Exception as e:
                st.error(f"An error occurred with Ollama: {e}. Please ensure Ollama is running and the 'llama3' model is installed.")
                st.stop()
        
        st.rerun()

def transcribe_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        try:
            audio = r.listen(source, timeout=5)
            st.info("Transcribing...")
            text = r.recognize_google(audio)
            st.info(f"You said: {text}")
            handle_chat_input(text)
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Create a fixed container at the bottom for the chat input and speech controls
with st.container():
    st.markdown("""
        <style>
            .stTextInput>div>div>div>input {
                border-top-right-radius: 0;
                border-bottom-right-radius: 0;
            }
            .stButton>button {
                border-top-left-radius: 0;
                border-bottom-left-radius: 0;
            }
        </style>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([10, 1])

    with col1:
        prompt_input = st.chat_input("Start chatting...", key="chat_input")

    with col2:
        mic_button = st.button("🎙️", key="mic_button")

# Check if the microphone button was clicked
if mic_button:
    st.session_state.show_speech_options = not st.session_state.show_speech_options

# Display the speech options if the flag is True
if st.session_state.show_speech_options:
    st.info("Speech Control Options:")
    col_speech1, col_speech2, col_speech3 = st.columns(3)
    with col_speech1:
        if st.button("🗣️ Speak to Chatbot", key="speak_button"):
            st.session_state.show_speech_options = False
            transcribe_speech()
    with col_speech2:
        if st.button("🔊 Repeat Last Response", key="repeat_button"):
            st.session_state.show_speech_options = False
            if st.session_state.messages:
                last_message = st.session_state.messages[-1]
                if last_message["role"] == "assistant":
                    speak_async(last_message["content"], st.session_state.last_detected_lang)
                else:
                    st.warning("There is no assistant response to repeat.")
            else:
                st.warning("No messages in history to repeat.")
    with col_speech3:
        if st.button("⏹️ Stop", key="stop_button"):
            st.session_state.stop_flag = True
            stop_speaking()
            st.warning("Generation and speech stopped.")
            st.session_state.show_speech_options = False

# Check for candidate responses to display
if st.session_state.candidate_responses:
    st.info("I have two responses. Please select your preferred one:")
    
    col_resp1, col_resp2 = st.columns(2)
    
    with col_resp1:
        with st.container(border=True):
            st.write(st.session_state.candidate_responses['response1'])
            if st.button("I Prefer This", key="prefer_1"):
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.candidate_responses['response1']})
                st.session_state.candidate_responses = None
                speak_async(st.session_state.messages[-1]["content"], st.session_state.last_detected_lang)
                st.rerun()
    
    with col_resp2:
        with st.container(border=True):
            st.write(st.session_state.candidate_responses['response2'])
            if st.button("I Prefer This", key="prefer_2"):
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.candidate_responses['response2']})
                st.session_state.candidate_responses = None
                speak_async(st.session_state.messages[-1]["content"], st.session_state.last_detected_lang)
                st.rerun()
    
elif prompt_input:
    handle_chat_input(prompt_input)

st.markdown("---")

