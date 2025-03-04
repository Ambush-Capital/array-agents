import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up your OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")