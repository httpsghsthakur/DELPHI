from fastapi.testclient import TestClient
from delphi.api.main import app

client = TestClient(app)

def test_analysis_not_implemented():
    response = client.post("/api/v1/analysis")
    assert response.status_code == 501
    assert response.json() == {"detail": "NOT IMPLEMENTED"}
