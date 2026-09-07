from dotenv import load_dotenv
from groq import Groq

import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=GROQ_API_KEY
)

def summarize_items(item_names: list[str]) -> str:

    items_text = ", ".join(item_names)

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a terse assistant"
            },
            {
                "role": "user",
                "content": f"Summarize this inventory: {items_text}"
            }
        ],
        model="openai/gpt-oss-20b",
        max_tokens=600
    )
    print(response.choices[0].message)
    return response.choices[0].message.content
    
# if __name__ == "__main__":
#     print("Item summary:", summarize_items(["laptop","notebook","coffee mug"]))