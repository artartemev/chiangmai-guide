#!/usr/bin/env python3
import requests
import json
import sys

LM_STUDIO_URL = "http://192.168.1.35:1143/v1"

def check_lm_studio():
    print(f"🔍 Проверка подключения к LM Studio по адресу {LM_STUDIO_URL}...")
    try:
        resp = requests.get(f"{LM_STUDIO_URL}/models", timeout=3)
        if resp.status_code == 200:
            models = resp.json().get("data", [])
            model_ids = [m.get("id") for m in models]
            print("✅ LM Studio подключен успешно!")
            print("📋 Доступные модели:", model_ids)
            return True, model_ids
    except Exception as e:
        print(f"❌ Не удалось подключиться к LM Studio: {e}")
    return False, []

def test_prompt(model_name="prism-ml/bonsai-27b"):
    print(f"\n🤖 Тестирование генерации JSON через модель '{model_name}'...")
    url = f"{LM_STUDIO_URL}/chat/completions"
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a JSON extractor for Chiang Mai places. Return valid JSON only."},
            {"role": "user", "content": "Message: Рекомендую отличное веганское кафе Goodsouls Kitchen в районе Nimman! Ссылка: https://maps.google.com/?q=Goodsouls"}
        ],
        "temperature": 0.1
    }
    try:
        resp = requests.post(url, json=payload, timeout=60)
        if resp.status_code == 200:
            answer = resp.json()["choices"][0]["message"]["content"]
            print("🎉 Ответ ИИ получен успешно:")
            print(answer)
            return True
        else:
            print(f"⚠️ Ошибка API: Code {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    return False

def main():
    ok, models = check_lm_studio()
    if ok:
        model_to_test = models[0] if models else "prism-ml/bonsai-27b"
        test_prompt(model_to_test)

if __name__ == "__main__":
    main()
