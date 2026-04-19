import requests
import json
import os

def process_to_llm(raw_text: str, words_data: list, system_prompt: str):
    base_url = os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434")
    model_name = os.getenv("LLM_MODEL", "") 

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Raw Text: {raw_text}\nData: {json.dumps(words_data, ensure_ascii=False)}",
            },
        ],
        "format": "json",  
        "stream": False,
        "options": {
            "num_ctx": 6000,
            "temperature": 0
        }
    }

    try:
        response = requests.post(
            base_url+"/api/chat",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        content = result.get("message", {}).get("content", "")

        return json.loads(content)

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к Ollama: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Ошибка парсинга JSON: {e}")
        return None