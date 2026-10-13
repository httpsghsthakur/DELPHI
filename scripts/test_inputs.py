import requests
import json

def test_inputs():
    url = "http://127.0.0.1:8000/analysis"
    headers = {"Content-Type": "application/json"}
    
    input_a = {
        "text": "A major country announces new restrictions on semiconductor exports.",
        "publication_timestamp": "2026-09-26T00:00:00Z",
        "prediction_information_cutoff": "2026-09-30T00:00:00Z",
        "domain": "Geopolitics",
        "forecast_horizon": 30,
        "live_research": True
    }
    
    input_b = {
        "text": "A central bank unexpectedly raises its benchmark interest rate.",
        "publication_timestamp": "2026-09-26T00:00:00Z",
        "prediction_information_cutoff": "2026-09-30T00:00:00Z",
        "domain": "Economy",
        "forecast_horizon": 30,
        "live_research": True
    }
    
    print("Testing Input A...")
    res_a = requests.post(url, json=input_a, headers=headers)
    print(f"Status A: {res_a.status_code}")
    if res_a.status_code == 200:
        data_a = res_a.json()
        print(f"A Event: {data_a.get('current_event', {}).get('event_type_code')}")
        
    print("\nTesting Input B...")
    res_b = requests.post(url, json=input_b, headers=headers)
    print(f"Status B: {res_b.status_code}")
    if res_b.status_code == 200:
        data_b = res_b.json()
        print(f"B Event: {data_b.get('current_event', {}).get('event_type_code')}")

if __name__ == "__main__":
    test_inputs()
