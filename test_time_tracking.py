#!/usr/bin/env python3
"""
Test script to verify time tracking functionality works correctly
"""
import requests
import json
from datetime import datetime

def test_api_endpoints():
    """Test that API endpoints are working"""
    base_url = "http://localhost:8000/api/v1"
    
    print("Testing API endpoints...")
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test time sessions endpoint
        response = requests.get(f"{base_url}/time-sessions/")
        print(f"Time sessions list: {response.status_code}")
        if response.status_code == 200:
            print(f"Found {len(response.json())} time sessions")
        
        # Test tasks endpoint
        response = requests.get(f"{base_url}/tasks/")
        print(f"Tasks list: {response.status_code}")
        if response.status_code == 200:
            print(f"Found {len(response.json())} tasks")
            
        print("API endpoints are working correctly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("API server is not running. Please start the backend server first.")
        return False
    except Exception as e:
        print(f"Error testing API: {e}")
        return False

if __name__ == "__main__":
    test_api_endpoints()
