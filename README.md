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

### ✅ To-Do / Improvements
 Optional GUI or terminal interface

 Switch between voices (macOS/Coqui)

 Add Coqui TTS for higher-quality Dutch voice

 Support Whisper as STT backend

 Add CLI argument support

---

### 🤝 Contributions
Contributions, suggestions, or bug reports are welcome!

---

### 📜 License
MIT License

---

### 💬 Say Hello
Made with ❤️ to help Dutch learners grow in confidence and fluency.