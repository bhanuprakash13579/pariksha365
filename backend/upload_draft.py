import json
import urllib.request
import urllib.error

with open('frontend-web/learntheta_ssc.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

payload = {
    "title": "SSC CGL Tier 1 (09 Sep 2024 - Shift 1) [LearnTheta]",
    "category": "SSC CGL Previous Year",
    "is_published": False,
    "sections": [
        {
            "title": "General Section",
            "questions": questions
        }
    ]
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(
    'http://localhost:8000/api/v1/tests/bulk', 
    data=data, 
    headers={'Content-Type': 'application/json'}
)

try:
    response = urllib.request.urlopen(req)
    print("Success:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Error:", e.read().decode('utf-8'))
