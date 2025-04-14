import sys
import os
import glob
# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from app import app
from database import init_db, get_user, get_transactions

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Clear the data/ directory before each test
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    for file in glob.glob(os.path.join(data_dir, '*.json')):
        os.remove(file)
    
    with app.test_client() as client:
        init_db()  # Reset database for tests
        yield client

def test_ussd_main_menu(client):
    response = client.post('/ussd', data={
        'sessionId': '12345',
        'phoneNumber': '08012345678',
        'text': ''
    })
    assert response.status_code == 200
    assert "CON Welcome to eNaira Offline" in response.json['response']

def test_transaction_with_correct_pin(client):
    response = client.post('/ussd', data={
        'sessionId': '12345',
        'phoneNumber': '08012345678',
        'text': '1*user2*100*1234'
    })
    assert response.status_code == 200
    assert "END Transaction initiated" in response.json['response']
    assert os.path.exists('data/tx_12345.json')

def test_transaction_with_incorrect_pin(client):
    response = client.post('/ussd', data={
        'sessionId': '12345',
        'phoneNumber': '08012345678',
        'text': '1*user2*100*9999'
    })
    assert response.status_code == 200
    assert "END Incorrect PIN" in response.json['response']
    assert not os.path.exists('data/tx_12345.json')

def test_sync_transactions(client):
    # Create a transaction
    client.post('/ussd', data={
        'sessionId': '12345',
        'phoneNumber': '08012345678',
        'text': '1*user2*100*1234'
    })
    # Sync
    response = client.post('/ussd', data={
        'sessionId': '12345',
        'phoneNumber': '08012345678',
        'text': '4'
    })
    assert response.status_code == 200
    assert "END Transactions synced successfully" in response.json['response']
    assert not os.path.exists('data/tx_12345.json')
    transactions = get_transactions('user1')
    assert len(transactions) == 1
    assert transactions[0]['status'] == 'completed'
    user = get_user('08012345678')
    assert user['balance'] == 4900.0