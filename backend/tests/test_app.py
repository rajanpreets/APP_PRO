import pytest
from flask import Flask
from src.app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

def test_search_endpoint(client):
    """Test the search endpoint"""
    test_query = {
        "query": "aspirin",
        "search_type": "drug"
    }
    
    response = client.post(
        '/api/search',
        data=json.dumps(test_query),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check if all expected keys are present
    assert 'fda_data' in data
    assert 'clinical_trials_data' in data
    assert 'ncbi_data' in data
    assert 'summary' in data

def test_search_endpoint_invalid_request(client):
    """Test the search endpoint with invalid request"""
    invalid_query = {
        "query": ""  # Empty query
    }
    
    response = client.post(
        '/api/search',
        data=json.dumps(invalid_query),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_search_endpoint_missing_type(client):
    """Test the search endpoint with missing search type"""
    query = {
        "query": "aspirin"
    }
    
    response = client.post(
        '/api/search',
        data=json.dumps(query),
        content_type='application/json'
    )
    
    assert response.status_code == 200  # Should still work with default type
    data = json.loads(response.data)
    assert 'fda_data' in data
    assert 'clinical_trials_data' in data
    assert 'ncbi_data' in data
    assert 'summary' in data

def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.get('/health')
    assert response.status_code == 200
    assert 'Access-Control-Allow-Origin' in response.headers
    assert 'Access-Control-Allow-Methods' in response.headers
    assert 'Access-Control-Allow-Headers' in response.headers 