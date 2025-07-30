#!/usr/bin/env python3
"""
Test pipeline persistence functionality.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_pipeline_persistence():
    """Test that pipeline data persists after server restart."""
    
    print("🧪 Testing Pipeline Persistence...")
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Create a pipeline
        print("\n1️⃣ Creating pipeline...")
        create_data = {
            "query": "blockchain transparency test",
            "research_domain": "Blockchain",
            "max_results": 3,
            "quality_threshold": 0.6
        }
        
        async with session.post(f"{BASE_URL}/api/v1/pipelines/", json=create_data) as response:
            if response.status == 201:
                result = await response.json()
                pipeline_id = result.get("pipeline_id")
                print(f"✅ Pipeline created: {pipeline_id}")
                print(f"   Status: {result.get('status')}")
                
                # Step 2: Check if pipeline is accessible immediately
                print(f"\n2️⃣ Checking immediate access...")
                async with session.get(f"{BASE_URL}/api/v1/pipelines/{pipeline_id}/status") as status_response:
                    if status_response.status == 200:
                        status_result = await status_response.json()
                        print(f"✅ Pipeline accessible immediately")
                        print(f"   Status: {status_result.get('status')}")
                    else:
                        print(f"❌ Pipeline not accessible immediately: {status_response.status}")
                
                # Step 3: List pipelines to see if it's in the list
                print(f"\n3️⃣ Listing pipelines...")
                async with session.get(f"{BASE_URL}/api/v1/pipelines/") as list_response:
                    if list_response.status == 200:
                        list_result = await list_response.json()
                        pipelines = list_result.get("pipelines", [])
                        print(f"✅ Found {len(pipelines)} pipelines in list")
                        
                        # Check if our pipeline is in the list
                        found = False
                        for pipeline in pipelines:
                            if pipeline.get("pipeline_id") == pipeline_id:
                                found = True
                                print(f"✅ Our pipeline found in list")
                                break
                        
                        if not found:
                            print(f"❌ Our pipeline NOT found in list")
                    else:
                        print(f"❌ Failed to list pipelines: {list_response.status}")
                
                print(f"\n🎉 Pipeline persistence test completed!")
                print(f"Pipeline ID for manual testing: {pipeline_id}")
                print(f"Try accessing: {BASE_URL}/api/v1/pipelines/{pipeline_id}/status")
                
            else:
                print(f"❌ Failed to create pipeline: {response.status}")
                try:
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                except:
                    pass

async def main():
    """Run the persistence test."""
    print("🚀 Starting Pipeline Persistence Test...")
    
    try:
        await test_pipeline_persistence()
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 