import requests
import json

def test():
    res = requests.post("http://localhost:8000/analysis", json={
        "text": "The global leaders meet for a summit.",
        "publication_timestamp": "2026-12-31T00:00:00Z",
        "prediction_information_cutoff": "2026-12-31T00:00:00Z",
        "domain": "news.com"
    })
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    test()
