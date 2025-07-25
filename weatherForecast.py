import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_weather(city: str) -> str:
    city_map = {
        "北京": "beijing",
        "beijing": "beijing",
        "深圳": "shenzhen",
        "shenzhen": "shenzhen"
    }
    weather_data = {
        "beijing": {
            "location": "Beijing",
            "temperature": {
                "current": 32,
                "low": 26,
                "high": 35
            },
            "rain_probability": 10,   # 百分比
            "humidity": 40  # 百分比
        },
        "shenzhen": {
            "location": "Shenzhen",
            "temperature": {
                "current": 28,
                "low": 24,
                "high": 31
            },
            "rain_probability": 90,   # 百分比
            "humidity": 85     # 百分比
        }
    }

    city_key = city_map.get(city.lower(), city.lower())
    if city_key in weather_data:
        return json.dumps(weather_data[city_key], ensure_ascii=False)
    return json.dumps({"error": "Weather Unavailable"}, ensure_ascii=False)

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of an location, the user should supply a location first",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city needs to be translated into English (e.g. Beijing)",
                    }
                },
                "required": ["location"]
            },
        }
    },
]

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message

user_input=input("How can I help you?")
input_messages = [{"role": "user", "content": user_input}]
checkingMessage = send_messages(input_messages)
input_messages.append(checkingMessage)


if hasattr(checkingMessage, "tool_calls") and checkingMessage.tool_calls:
    tool_call = checkingMessage.tool_calls[0]
    city = json.loads(tool_call.function.arguments)["location"]

    weather_result = get_weather(city)
    input_messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": weather_result
    })

    resultMessage = send_messages(input_messages)
    print(resultMessage.content)
else:
    print("Something went wrong, try again later")