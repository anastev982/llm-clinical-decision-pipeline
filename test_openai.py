import os
from dotenv import load_dotenv  # type: ignore
from openai import OpenAI  # type: ignore
from pathlib import Path
from src.utils.env import load_env

load_env()

key = os.getenv("OPENAI_API_KEY")
if key:
    key = key.strip()
print("LEN:", len(key) if key else 0)
print("START:", key[:10] if key else None)


client = OpenAI(api_key=key)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role":"user", "content":"Hello!"}
    ],
    temperature=0.7
)

print(response.choices[0].message.content)