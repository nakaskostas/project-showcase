import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found. Please ensure it is set in your .env file.")
else:
    try:
        genai.configure(api_key=api_key)

        print("Available models that support 'generateContent':")
        print("-" * 40)
        found_model = False
        for m in genai.list_models():
          if 'generateContent' in m.supported_generation_methods:
            print(m.name)
            found_model = True
        
        if not found_model:
            print("No models supporting 'generateContent' were found for your API key.")

    except Exception as e:
        print(f"An error occurred while trying to connect to the Gemini API: {e}")
