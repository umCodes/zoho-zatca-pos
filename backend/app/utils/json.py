import json

def parse_json_response(response: str):
    cleaned = response.replace("```json", "").replace("```JSON", "").replace("```", "").strip()
    return json.loads(cleaned)