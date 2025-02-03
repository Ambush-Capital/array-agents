import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up your OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY',"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")

if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")