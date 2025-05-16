import requests

def get_translations(text: str, source_lang="en", target_lang="ru") -> list[str]:
    url = "http://localhost:5000/translate"
    try:
        response = requests.post(url, json={
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text",
            "api_key": "",
        }, headers={
            "Content-Type": "application/json",
        },
        timeout=20)

        if response.status_code == 200:
            translated = response.json().get("translatedText", "")
            return [translated.strip()] if translated else []
        else:
            print(f"LibreTranslate error {response.status_code}: {response.text}")
            return []

    except Exception as e:
        print(f"Ошибка при запросе к LibreTranslate: {e}")
        return []