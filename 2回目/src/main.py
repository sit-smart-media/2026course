"""
 uv sync
 uv run python main.py
"""

from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_URL")
)

response = client.chat.completions.create(
    model=os.getenv("LLM_MODEL"),
    messages=[
        {"role": "user", "content": "リストを逆順にするPython関数を作成してください."}
    ]
)

print(response.choices[0].message.content)