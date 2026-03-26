import os
# Alternative without dotenv - set OPENAI_API_KEY environment variable directly
from openai import OpenAI  # type: ignore

# You can set the API key directly in environment or here (not recommended for production)
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role":"system", "content":"Hello system!"},
        {"role":"user", "content":"Hello user!"}
    ],
    temperature=0.7
)

print(response.choices[0].message.content)