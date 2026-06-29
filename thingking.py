import requests
import json

BASE_URL = "http://172.23.248.61:11435"
MODEL_NAME = "qwen3.5:9b"


def chat_no_thinking(prompt: str):
    url = f"{BASE_URL}/api/chat"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "thinking": False,   # 有些服务支持
        "options": {
            "temperature": 0.2
        }
    }

    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data


if __name__ == "__main__":
    result = chat_no_thinking("请简述什么是Python，不要输出思考过程。")
    print(json.dumps(result, ensure_ascii=False, indent=2))