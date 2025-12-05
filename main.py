import speech_recognition as sr
import os
import webbrowser
import openai
from config import apikey
import datetime
import random
import numpy as np


chatStr = ""
# https://youtu.be/Z3ZAJoi4x6Q
def chat(query):
    global chatStr
    print(chatStr)
    openai.api_key = apikey
    chatStr += f"Harry: {query}\n Jarvis: "
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt= chatStr,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    try:
        response_text = response["choices"][0]["text"]
        say(response_text)
        chatStr += f"{response_text}\n"
        return response_text
    except (KeyError, IndexError) as e:
        error_message = f"Error processing OpenAI response: {str(e)}"
        print(error_message)
        say("Sorry, I encountered an error processing the response.")
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        print(error_message)
        say("Sorry, I encountered an unexpected error.")
        return error_message

def ai(prompt):
    openai.api_key = apikey
    text = f"OpenAI response for Prompt: {prompt} \n *************************\n\n"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # todo: Wrap this inside of a  try catch block
    # print(response["choices"][0]["text"])
    text += response["choices"][0]["text"]
    if not os.path.exists("Openai"):
        os.mkdir("Openai")

    # with open(f"Openai/prompt- {random.randint(1, 2343434356)}", "w") as f:
    with open(f"Openai/{''.join(prompt.split('intelligence')[1:]).strip() }.txt", "w") as f:
        f.write(text)

def say(text):
    os.system(f'say "{text}"')

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # r.pause_threshold =  0.6
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except Exception as e:
            return "Some Error Occurred. Sorry from Jarvis"

def searchFile(filename, searchPath=None, maxResults=10):
    """
    Search for a file by name in the system.
    Args:
        filename: Name of the file to search for (can be partial)
        searchPath: Starting directory path (default: workspace root)
        maxResults: Maximum number of results to return
    Returns:
        List of found file paths
    """
    if searchPath is None:
        # Start search from the workspace root (E:\Code)
        searchPath = os.path.dirname(os.path.abspath(__file__))
        # Go up to workspace root if we're in a subdirectory
        if "Jarvis AI" in searchPath:
            searchPath = os.path.dirname(searchPath)
    
    foundFiles = []
    filename_lower = filename.lower()
    
    try:
        # Walk through directories and search for files
        for root, dirs, files in os.walk(searchPath):
            # Skip common directories that shouldn't be searched
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
            
            for file in files:
                if filename_lower in file.lower():
                    fullPath = os.path.join(root, file)
                    foundFiles.append(fullPath)
                    if len(foundFiles) >= maxResults:
                        return foundFiles
    except Exception as e:
        print(f"Error searching for file: {str(e)}")
        return []
    
    return foundFiles

if __name__ == '__main__':
    print('Welcome to Jarvis A.I')
    say("Jarvis A.I")
    while True:
        print("Listening...")
        query = takeCommand()
        # todo: Add more sites
        sites = [["youtube", "https://www.youtube.com"], ["wikipedia", "https://www.wikipedia.com"], ["google", "https://www.google.com"],]
        for site in sites:
            if f"Open {site[0]}".lower() in query.lower():
                say(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])
        # todo: Add a feature to play a specific song
        if "open music" in query:
            musicPath = "/Users/harry/Downloads/downfall-21371.mp3"
            os.system(f"open {musicPath}")

        elif "the time" in query:
            musicPath = "/Users/harry/Downloads/downfall-21371.mp3"
            hour = datetime.datetime.now().strftime("%H")
            min = datetime.datetime.now().strftime("%M")
            say(f"Sir time is {hour} bajke {min} minutes")

        elif "open facetime".lower() in query.lower():
            os.system(f"open /System/Applications/FaceTime.app")

        elif "open pass".lower() in query.lower():
            os.system(f"open /Applications/Passky.app")

        elif "Using artificial intelligence".lower() in query.lower():
            ai(prompt=query)

        elif "Jarvis Quit".lower() in query.lower():
            exit()

        elif "reset chat".lower() in query.lower():
            chatStr = ""

        elif "search for file" in query.lower() or "find file" in query.lower() or "search file" in query.lower():
            # Extract filename from query
            query_lower = query.lower()
            filename = None
            
            # Try different patterns to extract filename
            search_patterns = [
                ("search for file", "search for file"),
                ("find file", "find file"),
                ("search file", "search file")
            ]
            
            for pattern, phrase in search_patterns:
                if phrase in query_lower:
                    # Get text after the search phrase
                    parts = query_lower.split(phrase, 1)
                    if len(parts) > 1 and parts[1].strip():
                        filename = parts[1].strip()
                        break
            
            if not filename:
                # Try to extract just the filename from the original query
                words = query.split()
                # Look for words that might be filenames (contain dots or common extensions)
                for word in words:
                    if '.' in word or any(word.lower().endswith(ext) for ext in ['.py', '.txt', '.js', '.html', '.css', '.json', '.md']):
                        filename = word
                        break
            
            if filename:
                say(f"Searching for {filename}...")
                print(f"Searching for file: {filename}")
                results = searchFile(filename)
                if results:
                    say(f"Found {len(results)} file{'s' if len(results) > 1 else ''}")
                    print(f"\nFound {len(results)} file(s):")
                    for i, filepath in enumerate(results, 1):
                        print(f"{i}. {filepath}")
                    # Speak the first result's directory
                    if results:
                        first_file_dir = os.path.dirname(results[0])
                        say(f"First result is in {os.path.basename(first_file_dir)} directory")
                else:
                    say(f"Sorry, I could not find any file named {filename}")
                    print(f"No files found matching: {filename}")
            else:
                say("Please specify which file you want me to search for")
                print("No filename specified in the search query")

        else:
            print("Chatting...")
            chat(query)





        # say(query)