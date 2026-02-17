import os
from dotenv import load_dotenv
import google.generativeai as genai
from termcolor import colored

# 1. Load the API Key from your .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print(colored("Error: No API Key found in .env file!", "red"))
else:
    print(colored(f"Found API Key: {api_key[:10]}...******", "green"))
    
    # 2. Configure the Google Library
    genai.configure(api_key=api_key)

    print("\n--- Checking Available Models ---")
    try:
        # 3. Ask Google for a list of models
        found_any = False
        for m in genai.list_models():
            # We only care about models that can generate text
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Available: {m.name}")
                found_any = True
        
        if not found_any:
            print(colored("No text generation models found! Check your API plan.", "red"))
            
    except Exception as e:
        print(colored(f"Error connecting to Google: {e}", "red"))
        print("Try running: pip install google-generativeai")