import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

user_input="How's the weather in Shanghai?"

def get_weather(city: str) -> str:
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

    city_key = city.lower()
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
                        "description": "The city, e.g. San Francisco",
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
    print(response)
    return response.choices[0].message

input_messages = [{"role": "user", "content": user_input}]
checkingMessage = send_messages(input_messages)
print(checkingMessage.content) # remain
print(input_messages)
input_messages.append(checkingMessage)
print(input_messages)


if hasattr(checkingMessage, "tool_calls") and checkingMessage.tool_calls:
    tool_call = checkingMessage.tool_calls[0]
    print(tool_call)
    city = json.loads(tool_call.function.arguments)["location"]
    print(city)

    weather_result = get_weather(city)
    print("----------------")
    print(weather_result)
    input_messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": weather_result
    })

    resultMessage = send_messages(input_messages)
    print("true")
    print(resultMessage.content)
else:
    print("error")
    print(checkingMessage.content)