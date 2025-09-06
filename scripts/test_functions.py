import requests
import json
import time
import os

def test_cloud_functions():
    """Test deployed Cloud Functions"""
    
    # Get function URLs from environment or set them manually
    data_collector_url = os.environ.get('DATA_COLLECTOR_URL')
    metrics_collector_url = os.environ.get('METRICS_COLLECTOR_URL')
    
    if not data_collector_url or not metrics_collector_url:
        print("Please set DATA_COLLECTOR_URL and METRICS_COLLECTOR_URL environment variables")
        return
    
    print("Testing Cloud Functions...")
    print(f"Data Collector URL: {data_collector_url}")
    print(f"Metrics Collector URL: {metrics_collector_url}")
    
    # Test network data collector
    print("\n1. Testing Network Data Collector...")
    try:
        response = requests.post(data_collector_url, timeout=540)
        if response.status_code == 200:
            data = response.json()
            print("✅ Network Data Collector - SUCCESS")
            print(f"Resources collected: {data.get('resources_collected', {})}")
        else:
            print(f"❌ Network Data Collector - FAILED: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Network Data Collector - ERROR: {str(e)}")
    
    # Wait a bit before next test
    time.sleep(2)
    
    # Test network metrics collector  
    print("\n2. Testing Network Metrics Collector...")
    try:
        # Test with 30-minute window
        response = requests.post(f"{metrics_collector_url}?duration=30", timeout=120)
        if response.status_code == 200:
            data = response.json()
            print("✅ Network Metrics Collector - SUCCESS")
            print(f"Total metrics: {data.get('total_metrics_collected', 0)}")
            print(f"Metrics breakdown: {data.get('metrics_breakdown', {})}")
        else:
            print(f"❌ Network Metrics Collector - FAILED: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Network Metrics Collector - ERROR: {str(e)}")
    
    print("\nFunction testing completed!")

if __name__ == '__main__':
    test_cloud_functions()