import os
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from vosk import Model, KaldiRecognizer
import json
import subprocess
import time
from pynput import keyboard
import threading

chat_history = []
FS = 16000
MODEL_PATH = "vosk-models/vosk-model-small-nl-0.22"

exit_event = threading.Event()

def load_chat_history():
    global chat_history
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r") as f:
            chat_history = json.load(f)
    else:
        chat_history = []

def save_chat_history():
    with open("chat_history.json", "w") as f:
        json.dump(chat_history, f)

def build_prompt(user_input, topic, level, max_turns=10):
    system_message = (
        f"Je bent een vriendelijke en geduldige Nederlandse taalcoach. "
        f"Je helpt een student oefenen met Nederlands spreken op niveau {level}. "
        f"Geef duidelijke en begrijpelijke antwoorden in het Nederlands. "
        f"Blijf in het Nederlands praten, ook als de student fouten maakt. "
        f"Het gespreksonderwerp is: {topic}."
    )

    recent_history = chat_history[-max_turns:]
    chat = "".join(f"\n{turn['role'].capitalize()}: {turn['content']}" for turn in recent_history)
    chat += f"\nStudent: {user_input}\nCoach:"

    return f"{system_message}\n{chat}"

def ask_ollama_cmd(prompt, model="llama3"):
    full_prompt = build_prompt(prompt, topic=session_config['topic'], level=session_config['level'])
    result = subprocess.run(["ollama", "run", model, full_prompt], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    response = result.stdout.strip()
    print("\n🧠 Dutch mentor says:\n", response)
    chat_history.append({"role": "student", "content": prompt})
    chat_history.append({"role": "coach", "content": response})
    save_chat_history()
    return response

def record_until_silence_or_space(filename="output.wav", silence_threshold=1e-10, silence_duration=1.5, min_duration=1.5, duration_limit=60):
    print("🎙️ Speak now... (press SPACE to stop, SHIFT+C to quit)")
    buffer = []
    silent_chunks = 0
    max_silent_chunks = int(silence_duration / 0.2)
    start_time = time.time()
    stop_event = threading.Event()

    def on_press(key):
        if key == keyboard.Key.space:
            stop_event.set()
            return False
        elif key == keyboard.KeyCode(char='C') and keyboard.Controller().pressed_keys and keyboard.Key.shift in keyboard.Controller().pressed_keys:
            exit_event.set()
            stop_event.set()
            return False

    threading.Thread(target=keyboard.Listener(on_press=on_press).start).start()

    def callback(indata, frames, time_info, status):
        nonlocal buffer, silent_chunks
        volume = np.mean(np.abs(indata))
        buffer.append(indata.copy())
        silent_chunks = silent_chunks + 1 if volume < silence_threshold else 0
        if (silent_chunks > max_silent_chunks and (time.time() - start_time) > min_duration) or \
           (stop_event.is_set()) or (time.time() - start_time > duration_limit):
            raise sd.CallbackStop()

    try:
        with sd.InputStream(callback=callback, channels=1, samplerate=FS):
            while not stop_event.is_set() and not exit_event.is_set():
                time.sleep(0.1)
    except sd.CallbackStop:
        pass

    audio = np.concatenate(buffer, axis=0)
    audio = np.clip(audio * 2.0, -1.0, 1.0)
    wav.write(filename, FS, np.int16(audio * 32767))
    print("✅ Recording saved")
    return filename

def transcribe_audio(filename="output.wav"):
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, FS)
    with open(filename, "rb") as f:
        f.read(44)
        while True:
            data = f.read(4000)
            if not data:
                break
            rec.AcceptWaveform(data)
    result = rec.FinalResult()
    return json.loads(result).get("text", "")

def speak_text_mac(text, voice="Xander"):
    try:
        subprocess.run(["say", "-v", voice, text])
    except Exception as e:
        print("❌ TTS failed:", e)

# Session setup
session_config = {"topic": "", "level": ""}

def initialize_conversation():
    speak_text_mac("Hallo! Ik ben je Nederlandse taalcoach. Laten we oefenen met spreken.")
    speak_text_mac("Kies een onderwerp om mee te beginnen. Bijvoorbeeld: eten en drinken, werk, reizen, enzovoort.")
    session_config['topic'] = input("📌 Kies een onderwerp: ")
    speak_text_mac(f"Oké! We gaan praten over {session_config['topic']}.")

    speak_text_mac("Welk taalniveau wil je oefenen? Bijvoorbeeld A1, A2, B1, B2?")
    session_config['level'] = input("🎯 Kies je niveau: ")
    speak_text_mac(f"Prima! Ik pas mijn antwoorden aan op niveau {session_config['level']}.")

    chat_history.append({"role": "system", "content": f"Topic: {session_config['topic']}, Level: {session_config['level']}"})
    save_chat_history()

def main():
    load_chat_history()
    initialize_conversation()
    while not exit_event.is_set():
        filename = record_until_silence_or_space()
        question = transcribe_audio(filename)
        if question:
            response = ask_ollama_cmd(question)
            speak_text_mac(response)

if __name__ == "__main__":
    main()
