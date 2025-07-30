#!/usr/bin/env python3
"""
Test to verify the API endpoint can retrieve the existing pipeline.
"""

import requests
import json

def test_api_retrieval():
    """Test API endpoint retrieval of existing pipeline."""
    
    print("🧪 Testing API Endpoint Retrieval...")
    
    # The existing pipeline ID
    pipeline_id = "96720687-abd8-4b7d-95a5-cb6f674050eb"
    
    # API base URL
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Get pipeline results
        print(f"🔍 Testing GET /api/v1/pipelines/{pipeline_id}/results")
        response = requests.get(f"{base_url}/api/v1/pipelines/{pipeline_id}/results")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pipeline results retrieved successfully!")
            print(f"   Raw response: {json.dumps(data, indent=2)}")
            
            # Try to extract data from different possible structures
            if isinstance(data, dict):
                print(f"   Status: {data.get('status')}")
                print(f"   Query: {data.get('query')}")
                print(f"   Research Domain: {data.get('research_domain')}")
                
                # Check results
                results = data.get('results', {})
                if results:
                    print(f"   Results: {len(results)} sections")
                    for key in results.keys():
                        print(f"     - {key}")
                else:
                    print(f"   Results: No results found")
            else:
                print(f"   Unexpected response format: {type(data)}")
        else:
            print(f"❌ Failed to retrieve pipeline results")
            print(f"   Response: {response.text}")
        
        # Test 2: Get pipeline status
        print(f"\n🔍 Testing GET /api/v1/pipelines/{pipeline_id}/status")
        response = requests.get(f"{base_url}/api/v1/pipelines/{pipeline_id}/status")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pipeline status retrieved successfully!")
            print(f"   Status: {data.get('status')}")
            print(f"   Current Step: {data.get('current_step')}")
            print(f"   Total Steps: {data.get('total_steps')}")
        else:
            print(f"❌ Failed to retrieve pipeline status")
            print(f"   Response: {response.text}")
        
        # Test 3: List all pipelines
        print(f"\n📋 Testing GET /api/v1/pipelines/")
        response = requests.get(f"{base_url}/api/v1/pipelines/")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            pipelines = data.get('pipelines', [])
            print(f"✅ Found {len(pipelines)} pipelines")
            
            for pipeline in pipelines:
                print(f"   - {pipeline.get('pipeline_id')}: {pipeline.get('status')} ({pipeline.get('query')})")
        else:
            print(f"❌ Failed to list pipelines")
            print(f"   Response: {response.text}")
        
        print(f"\n🎉 API endpoint test completed!")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to API server. Make sure the server is running on {base_url}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_api_retrieval() 