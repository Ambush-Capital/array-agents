import openai
from config import OPENAI_API_KEY

# Set up your OpenAI API key
openai.api_key = OPENAI_API_KEY

def generate_strategy(data, constraints):
    # Prepare the prompt for the LLM
    prompt = f"Generate a trading strategy based on the following data and constraints:\nData: {data}\nConstraints: {constraints}"

    # Call the OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )

    # Extract the strategy from the response
    strategy = response.choices[0].text.strip()
    return strategy