# 🇳🇱 Dutch Speaking Mentor Agent

A voice-based Dutch language conversation assistant running entirely offline. Speak naturally into your mic, get transcribed by [Vosk](https://alphacephei.com/vosk/), processed by a local LLM ([Ollama](https://ollama.com/) running LLaMA 3), and receive a Dutch reply spoken aloud via macOS TTS.

---

### 🎯 Features

- 🗣️ **Voice input with silence or spacebar detection**
- 🧠 **Conversation context handling** (keeps a rolling chat history)
- 🇳🇱 **Dutch language practice topics**, suitable for A2–B1 learners
- 🖥️ **Local and private** (no cloud APIs required)
- 🔊 **Text-to-speech** output using macOS `say` or other TTS backends
- ♻️ Clean codebase structured with **OOP, SOLID, and DRY** principles

---

### 📂 Project Structure

```plaintext
dutch-mentor-agent/
├── main.py               # App entry point
├── requirements.txt      # Dependencies
├── data/                 # Recordings and chat history
│   └── chat_history.json # Saved conversation history
├── models/               # Vosk or other downloaded models
│   └── vosk-model-small-nl-0.22/ # Example Vosk model
├── core/                 # Core application logic
│   ├── audio.py          # Audio recording with silence + keyboard detection
│   ├── transcription.py  # Speech-to-text using Vosk
│   ├── text_to_speech.py # Speak text via macOS or Coqui
│   ├── chat_history.py   # Load/save conversation history
│   └── mentor_agent.py   # Dutch coach logic + Ollama integration
└── utils/                # Utility scripts
    └── config.py         # Configurable constants and paths
```

---

### 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install/Download:
✅ Vosk Model (e.g. Dutch)
Download from https://alphacephei.com/vosk/models
Place it under models/, e.g.:
```
models/vosk-model-small-nl-0.22/
```
✅ Ollama with LLaMA 3
Install Ollama and pull a Dutch-capable model (e.g., LLaMA 3):

```bash
brew install ollama
ollama run llama3
```

---

### 🧑‍🏫 Topics Practiced
| **Topic**                     | **Description**                     |
|-------------------------------|-------------------------------------|
| Praten over jezelf            | Talking about yourself             |
| Familie en vrienden           | Family and friends                 |
| Eten en drinken               | Food and drinks                    |
| Wonen                         | Living                             |
| Vrije tijd                    | Leisure time                       |
| Kleding en uiterlijk          | Clothing and appearance            |
| Leren                         | Learning                           |
| Kinderen en school            | Children and school                |
| Ondernemen                    | Entrepreneurship                   |
| Zaken regelen                 | Managing affairs                   |
| Werk zoeken                   | Job searching                      |
| Kopen                         | Shopping                           |
| Reizen                        | Traveling                          |
| Het weer en Nederlandse gewoontes | Weather and Dutch customs         |
| Gezondheid                    | Health                             |
| Werk                          | Work                               |
| Dag en tijd                   | Day and time                       |
| Bellen en communicatie        | Calling and communication          |
| Geld                          | Money                              |

---

### 🎤 How It Works
🎙️ You speak (recording stops with silence or spacebar)

📜 Your sentence is transcribed using Vosk

🧠 The LLM receives your message with chat history as context

🤖 The agent responds as a Dutch mentor

🔈 The response is spoken aloud using a TTS engine

---

### ⚙️ Configuration
Edit utils/config.py to change:

Model path

Sampling rate

Thresholds for silence

TTS voice settings (e.g., macOS say voices)

---
### ✅ To-Do / Planned Improvements


0. ✅ add loop to not stop process and after answer you wait for your voice input.
1. ⬜ Refactor the codebase to fully adhere to **SOLID principles**, **DRY practices**, and **Test-Driven Development (TDD)**. Incorporate **design patterns** where applicable.
2. ⬜ Integrate a **Telegram chatbot** for remote interaction.
3. ⬜ Add functionality to **select conversation topics** dynamically.
4. ⬜ Enable users to **choose their language proficiency level** for tailored responses.
5. ⬜ Develop an **optional GUI** or enhance the **terminal interface** for better usability.
6. ⬜ Replace JSON-based chat history storage with a **lightweight database** for improved performance and scalability.
7. ⬜ Implement **interfaces and classes** for Speech-to-Text (STT) functionality.
8. ⬜ Create **interfaces and classes** for Text-to-Speech (TTS) functionality.
9. ⬜ Design a **modular interface and class** for selecting and integrating different LLMs and their models.
10. ⬜ Add support to **switch between multiple voices** (e.g., macOS `say` voices or Coqui TTS).
11. ⬜ Integrate **Coqui TTS** for higher-quality Dutch voice output.
12. ⬜ Support **Whisper** as an alternative STT backend for enhanced transcription accuracy.
13. ⬜ Introduce **CLI argument support** for flexible configuration and usage.
14. ⬜ Improve overall modularity and extensibility of the application.

---

### 🤝 Contributions
Contributions, suggestions, or bug reports are welcome!

---

### 📜 License
MIT License

---

### 💬 Say Hello
Made with ❤️ to help Dutch learners grow in confidence and fluency.