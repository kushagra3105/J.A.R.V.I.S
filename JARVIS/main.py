import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os

# Initialize recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Replace with your real API keys
newsapi = "5d0ca2b99d90477fa1d62ebd54bd545e"
client = OpenAI(api_key="<Your OpenAI Key Here>")

# ------------------ SPEECH FUNCTIONS ------------------ #
def speak_old(text):
    """Offline voice (pyttsx3)"""
    engine.say(text)
    engine.runAndWait()

def speak(text):
    """Convert text to speech with gTTS + pygame"""
    tts = gTTS(text)
    tts.save("temp.mp3")

    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    os.remove("temp.mp3")

# ------------------ OPENAI FUNCTION ------------------ #
def aiProcess(command):
    """Send query to OpenAI"""
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a virtual assistant named Jarvis. Keep answers short."},
            {"role": "user", "content": command},
        ],
    )
    return completion.choices[0].message.content

# ------------------ COMMAND PROCESSOR ------------------ #
def processCommand(c):
    """Process voice commands"""
    c = c.lower()

    if "open google" in c:
        webbrowser.open("https://google.com")

    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")

    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")

    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")

    elif c.startswith("play"):
        song = c.split(" ")[1]
        link = musicLibrary.music.get(song)
        if link:
            webbrowser.open(link)
            speak(f"Playing {song}")
        else:
            speak("Sorry, I don't know that song.")

    elif "news" in c:
        try:
            r = requests.get(
                f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}"
            )
            if r.status_code == 200:
                articles = r.json().get("articles", [])[:5]  # limit to 5
                for article in articles:
                    speak(article["title"])
            else:
                speak("Sorry, I couldn't fetch the news right now.")
        except Exception:
            speak("Error fetching news.")

    else:
        output = aiProcess(c)
        speak(output)

# ------------------ MAIN LOOP ------------------ #
if __name__ == "__main__":
    speak("Initializing Jarvis....")

    # Check microphones
    mics = sr.Microphone.list_microphone_names()
    print("Available Microphones:", mics)

    # Use default mic (index 0) or change index if needed
    mic_index = 0

    while True:
        print("\nWaiting for wake word: 'Jarvis'...")
        try:
            with sr.Microphone(device_index=mic_index) as source:
                recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

            word = recognizer.recognize_google(audio)
            print("You said:", word)

            if word.lower() == "jarvis":
                speak("Ya")
                with sr.Microphone(device_index=mic_index) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=2)
                    print("Jarvis Active... listening for command...")
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
                    command = recognizer.recognize_google(audio)

                    print("Command:", command)
                    processCommand(command)

        except sr.WaitTimeoutError:
            print("Timeout: No speech detected, retrying...")
            continue
        except sr.UnknownValueError:
            print("Sorry, could not understand audio.")
            continue
        except Exception as e:
            print("Error:", e)
            continue
