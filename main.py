import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import os
import subprocess
import time
from textblob import TextBlob
import playsound
import json
import random
import requests
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify API credentials (replace with yours from https://developer.spotify.com/dashboard/)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='e87c03d2ea6844bd91753a165fb9dcf7',
    client_secret='b9690f47eb824c15a54c144f3febb0ae',
    redirect_uri='http://192.168.1.13:8501',
    scope='user-read-playback-state user-modify-playback-state'
))

def play_on_spotify(song_name):
    try:
        results = sp.search(q=song_name, limit=1, type='track')
        tracks = results['tracks']['items']
        if tracks:
            uri = tracks[0]['uri']
            sp.start_playback(uris=[uri])
            speak(f"Playing {tracks[0]['name']} by {tracks[0]['artists'][0]['name']} on Spotify.")
        else:
            speak("I couldn't find that song on Spotify.")
    except Exception as e:
        speak("Something went wrong with Spotify.")
        print("Spotify error:", e)


# Initialize recognizer and TTS engine
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 160)
engine.setProperty('volume', 0.9)

#history
chat_history = [
    {"role": "system", "content": "You are Nova, a helpful, emotional and witty virtual assistant. You assist users with daily tasks and answer questions naturally."}
]

# Emotional Personalities
personalities = {
    "default": {
        "tone": "friendly and helpful",
        "greetings": ["Hi! I'm Nova. What can I do for you today?"],
        "style": {"rate": 160, "volume": 0.9},
        "laugh": "Haha!"
    },
    "cheerful": {
        "tone": "super enthusiastic and bubbly",
        "greetings": ["Hey sunshine! What are we doing today?", "Yay! You're back!"],
        "style": {"rate": 180, "volume": 1.0},
        "laugh": "Hehehe, I love that one!"
    },
    "calm": {
        "tone": "relaxed and soothing",
        "greetings": ["Hello. How can I assist you calmly today?", "Peace and productivity, what can I help with?"],
        "style": {"rate": 140, "volume": 0.8},
        "laugh": "That was a light chuckle."
    },
    "sassy": {
        "tone": "sarcastic but lovable",
        "greetings": ["Oh look who needs me again", "What now, genius?"],
        "style": {"rate": 165, "volume": 0.95},
        "laugh": "Pfft! That was gold."
    }
}

current_personality = "default"

def set_personality(name):
    global current_personality
    if name in personalities:
        current_personality = name
        tone = personalities[name]['tone']
        talk(f"Okay! Switching to my {name} mood. {tone}")
    else:
        talk("Sorry, I don't have that mood.")

def get_news():
    api_key = "b8100c434f0b402d9c1299a379825f07"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    res = requests.get(url).json()
    articles = res.get("articles", [])[:5]
    if articles:
        talk("Here are the top headlines:")
        for article in articles:
            talk(article['title'])
    else:
        talk("Sorry, I couldn't fetch the news.")

def daily_quote():
    quotes = [
        "Believe in yourself and all that you are.",
        "You are capable of amazing things.",
        "Every day is a fresh start.",
        "The secret of getting ahead is getting started.",
        "A little progress each day adds up to big results.",
        "Push yourself, because no one else is going to do it for you.",
        "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle.",
        "Dream big. Start small. Act now.",
        "Doubt kills more dreams than failure ever will."
        "Your only limit is your mind.",
    ]
    quote = random.choice(quotes)
    talk(f"Here’s your quote for the day: {quote}")

def play_rps():
    choices = ["rock", "paper", "scissors"]
    talk("Let's play Rock, Paper, Scissors! Say your choice now.")
    user_choice = take_command()
    if user_choice not in choices:
        talk("Please say rock, paper, or scissors.")
        return
    nova_choice = random.choice(choices)
    talk(f"I choose {nova_choice}!")
    if user_choice == nova_choice:
        talk("It's a tie!")
    elif (user_choice == "rock" and nova_choice == "scissors") or \
         (user_choice == "paper" and nova_choice == "rock") or \
         (user_choice == "scissors" and nova_choice == "paper"):
        talk("You win! 🎉")
    else:
        talk("I win! 😎")

def talk(text):
    style = personalities[current_personality]['style']
    engine.setProperty('rate', style['rate'])
    engine.setProperty('volume', style['volume'])
    engine.say(text)
    engine.runAndWait()

def greet():
    greeting = random.choice(personalities[current_personality]['greetings'])
    talk(greeting)

def take_command():
    try:
        with sr.Microphone() as source:
            print('listening...')
            listener.adjust_for_ambient_noise(source)
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'nova' in command:
                command = command.replace('nova', '')
            print(f"Recognized command: {command}")
            return command
    except Exception as e:
        print(f"I couldn't catch that, please repeat... ({e})")
        return ""  # Return empty string to avoid crash


def therapy_conversation(command):
    talk("I'm really sorry you're feeling this way, but I'm here for you. Can you tell me more about what's going on?")
    # Give space for the user to express their feelings
    user_response = take_command()
    talk("Thank you for sharing that. It sounds tough. Let's work through it together. You’re not alone.")
    # Nova can give supportive feedback or follow up with deeper questions
    talk("What usually helps you feel better when you're down?")
    user_response = take_command()
    talk("I believe that taking small steps can make a big difference. You're doing great by talking to me!")

def comfort_the_user():
    comforting_messages = [
        "You are stronger than you think.",
        "It's okay to take breaks and breathe. Everything will get better.",
        "I'm proud of you for reaching out, even in tough times.",
        "You're doing your best, and that's enough. Keep going!"
    ]
    message = random.choice(comforting_messages)
    talk(message)

def set_reminder(task, time):
    reminder = {"task": task, "time": time}
    # Read existing reminders from the file
    try:
        with open("reminders.json", "r") as file:
            existing_reminders = [json.loads(line) for line in file.readlines()]
    except FileNotFoundError:
        existing_reminders = []
    except json.JSONDecodeError:
        talk("There was an issue with the reminder file. Resetting reminders.")
        existing_reminders = []
    # Check if the reminder already exists
    if any(r["task"] == task and r["time"] == time for r in existing_reminders):
        talk(f"You already have a reminder for {task} at {time}.")
        return
    # Append the new reminder to the file
    with open("reminders.json", "a") as file:
        file.write(json.dumps(reminder) + "\n")
    talk(f"Reminder set for {time}: {task}")


def set_alarm_with_clock_app():
    talk("Opening the Windows Clock app so you can set your alarm.")
    try:
        # This opens the built-in Alarms & Clock app on Windows
        subprocess.Popen(['start', 'ms-clock:'], shell=True)
    except Exception as e:
        talk("Sorry, I couldn't open the Clock app.")
        print(e)

def run_nova(command=None):
    command = take_command()
    print(command)
    if not command:
        command = take_command()
    print(command)
    if not command:
        return True

    if 'stop' in command or 'shutup' in command:
        talk("Shutting down. Goodbye!")
        return False  # Break out of the loop and stop Nova

    if any(phrase in command for phrase in ['i feel sad', 'i am feeling low', 'i am upset', 'cheer me up']):
        therapy_conversation(command)

    elif 'How are you' in command:
        talk('I am feeling good! Thanks for asking.')

    elif 'rock paper scissors' in command:
        play_rps()

    elif 'play' in command and 'on spotify' in command:
        song = command.replace('play', '').replace('on spotify', '').strip()
        play_on_spotify(song)

    elif 'play' in command:
        song = command.replace('play', '')
        talk('playing ' + song)
        pywhatkit.playonyt(song)

    elif 'time' in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        talk('Current time is ' + current_time)


    elif 'open whatsapp' in command:
        talk('Opening WhatsApp')
        try:
            # Try launching WhatsApp Desktop app (Windows)
            subprocess.Popen(["C:\\Users\\shail\\AppData\\Local\\WhatsApp\\WhatsApp.exe"])
        except Exception:
            talk("WhatsApp app not found. Opening WhatsApp Web instead.")
            webbrowser.open("https://web.whatsapp.com")

    elif 'open spotify' in command:
        talk('Opening Spotify')
        try:
            # For Spotify app on Windows
            subprocess.Popen(['C:\\Users\\shail\\AppData\\Roaming\\Spotify\\Spotify.exe'])
        except Exception:
            talk("Spotify app not found. Opening Spotify Web instead.")
            webbrowser.open("https://open.spotify.com")


    elif any(word in command for word in ['who', 'where', 'what', 'wikipedia']):
        item = command
        for word in ['who is', 'what is', 'where is', 'wikipedia']:
            item = item.replace(word, '')
        info = wikipedia.summary(item.strip(), 1)
        print(info)
        talk(info)

    elif 'joke' in command:
        talk(pyjokes.get_joke())
        talk(personalities[current_personality]['laugh'])

    elif any(x in command for x in ["search", "google"]):
        query = command.replace("search", "").replace("google", "").strip()
        talk(f"Searching for {query} on Google")
        pywhatkit.search(query)
        return f"🔍 Searching Google for: {query}"

    elif 'microsoft word' in command:
        talk('Opening Microsoft Word')
        subprocess.Popen(['start', 'winword'], shell=True)

    elif 'excel' in command:
        talk('Opening Microsoft Excel')
        subprocess.Popen(['start', 'excel'], shell=True)

    elif 'open powerpoint' in command:
        talk('Opening Microsoft PowerPoint')
        subprocess.Popen(['start', 'powerpnt'], shell=True)

    elif 'open calculator' in command:
        talk('Opening Calculator')
        subprocess.Popen(['calc'], shell=True)

    elif 'open calendar' in command:
        talk('Opening Calendar')
        subprocess.Popen(['start', 'outlookcal:'], shell=True)

    elif 'open notepad' in command:
        talk('Opening Notepad')
        subprocess.Popen(['notepad'])

    elif 'open chrome' in command:
        talk('Opening Google Chrome')
        subprocess.Popen(['start', 'chrome'], shell=True)

    elif 'open command prompt' in command:
        talk('Opening Command Prompt')
        subprocess.Popen(['cmd'], shell=True)

    elif 'set alarm' in command:
        set_alarm_with_clock_app()

    elif 'remind me' in command:
        try:
            task = command.split('to')[1].strip()
            time_str = command.split('at')[1].strip()
            set_reminder(task, time_str)
        except:
            talk("Sorry, I couldn't set the reminder. Please say it like: remind me to call John at 5 PM.")

    elif 'forget everything' in command:
        chat_history[:] = chat_history[:1]
        talk("Memory wiped! Starting fresh.")

    elif 'become cheerful' in command:
        set_personality("cheerful")

    elif 'become calm' in command:
        set_personality("calm")


    elif 'become sarcastic' in command or 'becomes sarcastic' in command:
        set_personality("sassy")

    elif 'become normal' in command or 'default mood' in command:
        set_personality("default")

    elif 'news' in command:
        get_news()

    elif 'quote' in command or 'motivation' in command:
        daily_quote()

    elif 'record my mood' in command:
        mood_text = command.replace('record my mood', '').strip()
        if not mood_text:
            talk("Tell me how you're feeling and I'll log it.")
            mood_text = take_command()
        analysis = TextBlob(mood_text)
        sentiment = analysis.sentiment.polarity
        mood_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "text": mood_text,
            "sentiment": sentiment
        }
        with open("mood_log.json", "a") as file:
            file.write(json.dumps(mood_data) + "\n")
        talk("Got it. I've saved how you're feeling.")


    elif 'how have i been feeling' in command or 'show me my mood' in command:
        try:
            with open("mood_log.json", "r") as file:
                entries = [json.loads(line) for line in file.readlines()]
                if not entries:
                    talk("I don't have any mood entries yet.")
                    return True
                last_7 = [e for e in entries if datetime.datetime.fromisoformat(
                    e["timestamp"]) >= datetime.datetime.now() - datetime.timedelta(days=7)]
                if not last_7:
                    talk("No mood data found for the last week.")
                    return True
                sentiments = [e["sentiment"] for e in last_7]
                avg = sum(sentiments) / len(sentiments)
                if avg > 0.2:
                    talk("You've mostly been feeling positive this week 😊")
                elif avg < -0.2:
                    talk("You've seemed a bit down this week 😔")
                else:
                    talk("It's been a pretty balanced week emotionally.")
        except FileNotFoundError:
            talk("I couldn't find any mood logs yet.")


    else:
        talk('Please say the command again.')
        run_nova()

    # Sleep to reduce CPU usage
    time.sleep(1)
    return True  # Keep running unless shutdown command is issued

if __name__ == "__main__":
    greet()
    while True:
        if not run_nova():
            break

