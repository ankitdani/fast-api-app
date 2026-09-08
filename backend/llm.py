from dotenv import load_dotenv
from groq import Groq

import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=GROQ_API_KEY
)

list_item_tool = {
    "type": "function",
    "function": {
        "name": "list_items",
        "description": "List all inventory items belonging to the current user.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

delete_item_tool = {
    "type": "function",
    "function": {
        "name": "delete_item",
        "description": "Delete one of the current user's inventory",
        "parameters": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "integer",
                    "description": "The ID of the item to delete."
                }
            },
            "required": ["item_id"]
        }
    }
}

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

def chat_with_tools(user_message: str, tools: list):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You help manage inventory items."
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        model="openai/gpt-oss-20b",
        max_tokens=600,
        tools=tools
    )
    return response.choices[0].message
    

# if __name__ == "__main__":
#     print("Item summary:", summarize_items(["laptop","notebook","coffee mug"]))