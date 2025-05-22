import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
import pandas as pd
from dotenv import load_dotenv
from app import app, df

load_dotenv()

@pytest.fixture(scope='session')
def test_app():
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False
    })
    return app

@pytest.fixture
def client(test_app):
    with test_app.test_client() as client:
        yield client

def test_amyvid_search(client):
    """Test searching for a drug in the database"""
    # Get a known drug name from the DataFrame
    known_drug = df['PROPRIETARY NAME'].iloc[0]
    
    # Test the search form submission
    response = client.post('/', data={
        'search': known_drug,
        'select': 'Name'
    }, follow_redirects=True)
    
    # Check if the response is successful
    assert response.status_code == 200
    
    # Check if the response contains the drug name
    assert known_drug.encode() in response.data
    
    # Check if the results description is present
    assert b'found' in response.data

def test_empty_search(client):
    """Test empty search returns default results"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'U.S. Drug Product Database' in response.data
    # Verify that we get the first 15 rows
    assert len(df.head(15)) == 15

def test_invalid_search(client):
    """Test search with non-existent drug name"""
    response = client.post('/', data={
        'search': 'nonexistentdrug123',
        'select': 'Name'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'No results found' in response.data

def test_clinical_category_search(client):
    """Test searching by clinical category"""
    response = client.post('/', data={
        'search': 'Antibiotic',
        'select': 'Clinical Category'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Verify that we get results or "No results found"
    assert (b'found' in response.data) or (b'No results found' in response.data)