import contextlib
import os
from vosk import Model, KaldiRecognizer
import sys
import time
import subprocess
import json
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from pynput import keyboard
import threading
import requests

chat_history = []
FS = 16000
MODEL_PATH = "vosk-models/vosk-model-small-nl-0.22"

exit_event = threading.Event()

session_config = {"topic": "", "level": ""}

def merge_responses(api_output):
    # Split the API output into individual JSON objects
    lines = api_output.strip().split("\n")
    
    # Parse each line as JSON and extract the "response" field
    responses = [json.loads(line)["response"] for line in lines if line.strip()]
    
    # Join all responses into a single unified text
    unified_text = "".join(responses)
    
    return unified_text

# ------------------------ Multi-Agent Support ------------------------

def call_llama(prompt, model="llama3"):
    try:
        url = f"http://localhost:11434/api/generate"
        payload = {"model": model, "prompt": prompt}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        unified_text = merge_responses(response.text)
        print(unified_text)
        return unified_text
        # return response.json().get("response", "").strip()
    except subprocess.CalledProcessError as e:
        print("❌ Fout bij het oproepen van LLaMA. Zorg ervoor dat Ollama draait.")
        print("Details:", e.stderr)
        speak_text_mac("Er is een fout opgetreden. Zorg ervoor dat Ollama actief is.")
        exit_event.set()
        return ""

def run_multi_agent_chain(user_input):
    # 1. Intent Agent
    intent_prompt = f"Je bent een taaldocent. Wat probeert de student te zeggen of vragen?\nInput: {user_input}\nAntwoord:"
    print("🤖 Intent Prompt:", intent_prompt)
    intent = call_llama(intent_prompt)
    if not intent:
        return ""

    # 2. Topic Expert Agent
    topic_prompt = (
        f"Je bent een Nederlandse taalcoach. Geef een voorbeeldzin over het onderwerp '{session_config['topic']}'"
        f" die past bij deze intentie: '{intent}'.\nGebruik natuurlijk Nederlands.\nZin:"
    )
    draft_response = call_llama(topic_prompt)
    if not draft_response:
        return ""

    # 3. Level Adjuster Agent
    adjust_prompt = (
        f"Pas deze zin aan naar taalniveau {session_config['level']}:\n\"{draft_response}\"\nResultaat:"
    )
    simplified_response = call_llama(adjust_prompt)
    if not simplified_response:
        return ""

    chat_history.append({"role": "student", "content": user_input})
    chat_history.append({"role": "coach", "content": simplified_response})
    save_chat_history()
    return simplified_response

# ------------------------ History Management ------------------------

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

# ------------------------ Audio & Transcription ------------------------

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

@contextlib.contextmanager
def capture_stderr_to_file(log_path):
    original_stderr_fd = sys.stderr.fileno()
    saved_stderr_fd = os.dup(original_stderr_fd)  # Save original stderr
    log_file = open(log_path, 'w')
    os.dup2(log_file.fileno(), original_stderr_fd)  # Redirect stderr to file

    try:
        yield
    finally:
        os.dup2(saved_stderr_fd, original_stderr_fd)  # Restore original stderr
        os.close(saved_stderr_fd)
        log_file.close()

def transcribe_audio(filename="output.wav"):
    with capture_stderr_to_file("vosk_log.txt"):
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
    text = json.loads(result).get("text", "")
    print("📝 Transcription:", text)
    return text

# ------------------------ TTS ------------------------

def speak_text_mac(text, voice="Xander"):
    try:
        print("🤖 TTS:", text)
        subprocess.run(["say", "-v", voice, text])
    except Exception as e:
        print("❌ TTS failed:", e)

# ------------------------ Initialization ------------------------

def initialize_conversation():
    print("🕹️ Druk op ENTER om de introductie over te slaan of wacht om te luisteren...")
    skip_intro = False

    def wait_for_enter():
        nonlocal skip_intro
        input()
        skip_intro = True

    t = threading.Thread(target=wait_for_enter)
    t.start()
    time.sleep(1)

    if not skip_intro:
        speak_text_mac("Hallo! Ik ben je Nederlandse taalcoach. Laten we oefenen met spreken.")
    if not skip_intro:
        speak_text_mac("Kies een onderwerp om mee te beginnen. Bijvoorbeeld: eten en drinken, werk, reizen, enzovoort.")

    session_config['topic'] = input("📌 Kies een onderwerp: ")
    speak_text_mac(f"Oké! We gaan praten over {session_config['topic']}.")

    if not skip_intro:
        speak_text_mac("Welk taalniveau wil je oefenen? Bijvoorbeeld A1, A2, B1, B2?")
    session_config['level'] = input("🎯 Kies je niveau: ")
    speak_text_mac(f"Prima! Ik pas mijn antwoorden aan op niveau {session_config['level']}.")

    chat_history.append({"role": "system", "content": f"Topic: {session_config['topic']}, Level: {session_config['level']}"})
    save_chat_history()

# ------------------------ Main ------------------------

def main():
    load_chat_history()
    initialize_conversation()
    while not exit_event.is_set():
        filename = record_until_silence_or_space()
        question = transcribe_audio(filename)
        # if question:
        response = run_multi_agent_chain(question)
        if response:
            speak_text_mac(response)

if __name__ == "__main__":
    main()
