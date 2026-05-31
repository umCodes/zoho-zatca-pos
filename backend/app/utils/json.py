import json

def parse_json_response(response: str):
    cleaned = response.replace("```json", "").replace("```JSON", "").replace("```", "").strip()
    # print("Cleaned JSON:", json.dumps(cleaned, indent=2))  # Debugging line
    return json.loads(cleaned)