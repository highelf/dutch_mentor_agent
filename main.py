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


# Global or external storage
chat_history = []
# Constants
DURATION = 60  # seconds
FS = 16000
MODEL_PATH = "vosk-models/vosk-model-small-en-us-0.15"  # Make sure you've downloaded and set this correctly


def build_prompt(history, user_input, max_turns=10):
    global chat_history
    # Load history
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r") as f:
            chat_history = json.load(f)
    else:
        chat_history = []
    print("Chat history loaded.")

    # Dutch mentor role definition
    system_message = (
        "Je bent een vriendelijke en geduldige Nederlandse taalcoach. "
        "Je helpt een student oefenen met Nederlands spreken op A2-B1 niveau. "
        "Geef duidelijke en begrijpelijke antwoorden in het Nederlands. "
        "Blijf in het Nederlands praten, ook als de student fouten maakt. "
        "We oefenen in de volgende onderwerpen:\n"
        "- praten over jezelf\n"
        "- familie en vrienden\n"
        "- eten en drinken\n"
        "- wonen\n"
        "- vrije tijd\n"
        "- kleding en uiterlijk\n"
        "- leren\n"
        "- kinderen en school\n"
        "- ondernemen\n"
        "- zaken regelen\n"
        "- werk zoeken\n"
        "- kopen\n"
        "- reizen\n"
        "- het weer en Nederlandse gewoontes\n"
        "- gezondheid\n"
        "- werk\n"
        "- dag en tijd\n"
        "- bellen en communicatie\n"
        "- geld\n"
    )

    recent_history = history[-max_turns:]  # limit history
    chat = ""
    for turn in recent_history:
        chat += f"\n{turn['role'].capitalize()}: {turn['content']}"
    chat += f"\nStudent: {user_input}\nCoach:"

    return f"{system_message}\n{chat}"

def ask_ollama_cmd(prompt, model="llama3"):
    global chat_history

    # Build prompt with history
    full_prompt = build_prompt(chat_history, prompt)

    result = subprocess.run(
        ["ollama", "run", model, full_prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    response = result.stdout.strip()
    print("🧠 Dutch mentor says:\n", response)
    # Update history
    chat_history.append({"role": "student", "content": prompt})
    chat_history.append({"role": "coach", "content": response})
    # Save history
    with open("chat_history.json", "w") as f:
        json.dump(chat_history, f)

    return response

def record_audio(filename="output.wav", duration=DURATION, fs=FS):
    print("🎙️ Recording for 5 seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    audio = audio * 2.0  # Increase the volume by multiplying the amplitude
    audio = np.clip(audio, -1.0, 1.0)  # Ensure the values stay within the valid range
    wav.write(filename, fs, np.int16(audio * 32767))
    print("✅ Recording complete and saved as", filename)

def record_until_silence_or_space(filename="output.wav", fs=FS, silence_threshold=1e-10, silence_duration=1.5, min_duration=1.5):
    print("🎙️ Start speaking... (press SPACE to stop early)")
    duration_limit = DURATION
    chunk_duration = 0.2
    buffer = []

    silent_chunks = 0
    max_silent_chunks = int(silence_duration / chunk_duration)
    start_time = time.time()
    stop_recording = threading.Event()

    # Keyboard listener
    def on_press(key):
        try:
            if key == keyboard.Key.space:
                print("🛑 Spacebar pressed: stopping recording.")
                stop_recording.set()
                return False  # stop listener
        except AttributeError:
            print(f"Key pressed: {AttributeError}")
            pass  # for special keys like shift, etc.

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    def callback(indata, frames, time_info, status):
        nonlocal buffer, silent_chunks
        volume = np.mean(np.abs(indata))
        #print(f"Volume: {volume:.2e}")

        buffer.append(indata.copy())

        if volume < silence_threshold:
            silent_chunks += 1
        else:
            silent_chunks = 0
        if (
            (silent_chunks > max_silent_chunks and (time.time() - start_time) > min_duration)
            or (time.time() - start_time > duration_limit)
            or stop_recording.is_set()
        ):
            raise sd.CallbackStop()

    try:
        with sd.InputStream(callback=callback, channels=1, samplerate=fs):
            print("here")
            while not stop_recording.is_set():
                time.sleep(0.1)
    except sd.CallbackStop:
        pass

    audio = np.concatenate(buffer, axis=0)
    audio = audio * 2.0
    audio = np.clip(audio, -1.0, 1.0)
    wav.write(filename, fs, np.int16(audio * 32767))
    print("✅ Done recording and saved to", filename)


def transcribe_audio(filename="output.wav", MODEL_PATH=MODEL_PATH):
    print("🔍 Transcribing with Vosk...")
    print(f"🔍 Transcribing audio Modle is {MODEL_PATH}...")
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, FS)

    with open(filename, "rb") as f:
        f.read(44)  # skip WAV header
        while True:
            data = f.read(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)

    result = rec.FinalResult()
    text = json.loads(result).get("text", "")
    print("📝 Transcribed text:", text)
    return text

def speak_text_mac(text, voice=None):
    print("🔊 Speaking...")
    try:
        if voice is None:
            subprocess.run(["say", text])
        else:
            subprocess.run(["say", "-v", voice, text])
    except Exception as e:
        print("❌ TTS failed:", e)

def main():
    # record_audio()
    record_until_silence_or_space(filename="output.wav")
    question = transcribe_audio(MODEL_PATH="vosk-models/vosk-model-small-nl-0.22")
    print("🗣️ :", question)

    # Generate an answer using LLaMA
    response = ask_ollama_cmd(question)
    #print("Respons: ", response)
    speak_text_mac(response, "Xander")

if __name__ == "__main__":
    main()
