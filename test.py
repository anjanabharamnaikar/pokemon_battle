from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def test_llm():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'hello'"}],
            timeout=5
        )
        print("Success! Response:", response.choices[0].message.content)
    except Exception as e:
        print("Failed:", str(e))

if __name__ == "__main__":
    test_llm()