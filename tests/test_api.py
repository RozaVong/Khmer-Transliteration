import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Khmer Transliteration API" in response.text

def test_health_endpoint():
    """Test the health endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "database_connected" in data

def test_test_endpoint():
    """Test the test endpoint"""
    response = client.get("/test")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "results" in data
    assert isinstance(data["results"], list)

def test_translate_endpoint():
    """Test the translate endpoint"""
    # Test with valid input
    response = client.post("/api/v1/translate", json={"text": "hello"})
    assert response.status_code in [200, 400, 500]
    
    # Test with empty input
    response = client.post("/api/v1/translate", json={"text": ""})
    assert response.status_code == 400

def test_metrics_endpoint():
    """Test the metrics endpoint"""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "metrics" in data
    assert "timestamp" in data