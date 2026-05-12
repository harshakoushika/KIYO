# Kiyo: Universal Language Support Chatbot

**Kiyo** is a multilingual, voice-enabled chatbot built with Streamlit that uses a locally hosted Large Language Model (LLM) via Ollama. It's designed to break down language barriers and promote inclusive communication, aligning with **UN Sustainable Development Goal 10 (Reduced Inequalities)**.

This application features real-time language translation, speech-to-text, and text-to-speech capabilities, allowing users to interact with an AI in their native language effortlessly.

-----

## ✨ Features

  * **Multilingual Conversation**: Automatically detects the user's language, translates the input to English for the LLM, and translates the response back to the user's language using Google Cloud Translate.
  * **Local AI Integration**: Leverages **Ollama** to run a powerful local model like **Llama 3**, ensuring privacy and fast responses without a cloud dependency for the core AI logic.
  * **Voice Interface**:
      * **Speech-to-Text**: Transcribes spoken user input to text using `SpeechRecognition`.
      * **Text-to-Speech**: Converts the chatbot's text responses into speech using `pyttsx3`.
  * **User Customization**:
      * **Dialect & Personality**: Allows users to choose the bot's conversational style (e.g., Formal, Informal) and personality type.
      * **Dyslexia-Friendly Mode**: Toggles a dyslexia-friendly font (`Lexend`) for improved readability.
  * **Location-Based Suggestions**: Provides language suggestions based on the user's geographical location (currently implemented for Indian states).
  * **RLHF (Reinforcement Learning from Human Feedback) Proxy**: Presents the user with two candidate responses and allows them to select their preferred one, which can be used to improve the model's performance.

-----

## 🛠️ Prerequisites

To run this application, you need to have the following installed:

  * **Python 3.8+**
  * **Ollama**: A local LLM server.
  * A **Google Cloud Account** with the **Cloud Translation API** enabled.

-----

## 🚀 Getting Started

### 1\. Clone the repository

```bash
git clone <repository_url>
cd <repository_name>
```

### 2\. Install Dependencies

It's highly recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: `venv\Scripts\activate`
pip install -r requirements.txt
```

**requirements.txt** content:

```
streamlit
ollama
google-cloud-translate
SpeechRecognition
pyttsx3
```

### 3\. Set Up Google Cloud Credentials

The code requires a Google Cloud service account key for the Translation API.

1.  Create a service account and download the JSON key file.

2.  Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your JSON file.

    
### 4\. Run Ollama

Make sure the Ollama server is running in the background. If you haven't already, pull the Llama 3 model.

```bash
ollama run llama3
```

### 5\. Run the Application

Execute the Streamlit app from your terminal.

```bash
streamlit run app.py
```

Replace `app.py` with the name of your main Python file if it's different. Your web browser will automatically open the application.

-----

## 🎨 Usage

1.  **Chat with Kiyo**: Type your message in the text box at the bottom and press Enter. The chatbot will automatically detect your language and respond accordingly.
2.  **Voice Interaction**: Click the microphone icon `🎙️` to reveal voice commands.
      * `🗣️ Speak to Chatbot`: Use your microphone to give a voice command.
      * `🔊 Repeat Last Response`: Repeats the last response spoken by the chatbot.
      * `⏹️ Stop`: Halts any ongoing speech output.
3.  **Provide Feedback**: After the chatbot provides two responses, select the one you prefer by clicking **"I Prefer This"**.
4.  **Customize**: Use the sidebar (`⚙️ Settings`) to adjust the bot's dialect, personality, and font settings.

-----

## 🤝 Contributing

Contributions are welcome\! If you find a bug or have a suggestion for a new feature, please open an issue or submit a pull request.
